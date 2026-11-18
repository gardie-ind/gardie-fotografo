# -*- coding: utf-8 -*-
"""Svelte 10479: reflexo liso na canopla inteira, sem IA (03/11/2026).

Thiago, 03/11/2026 01:12, sobre a -2 (`svelte_canopla_lisa.py`, que só tirou os dois furos): "Sobre a canopla
do svelte, não está bom. Está com um rechupe do plástico e uma deformidade do reflexo. Essa peça é lisa e o
reflexo é liso". A still de origem é da canopla antiga: o rechupe é a mancha escura (e a clara embaixo dela)
dentro do reflexo claro da direita, entre o bloco do braço e a borda, e a deformidade é a lasca clara que
corre colada na borda (y 780-870). Do lado esquerdo sobraram marcas do rebaixo antigo (um risco escuro junto
do bloco e arcos fracos).

Como (só pixels da própria foto):
- reflexo da direita: a região entre o reflexo do bloco (cunha escura), a barra, a borda da face e o topo
  limpo do reflexo é refeita como a superfície mais lisa que encosta nos pixels em volta (membrana com um
  pouco de rigidez, `tensao`: minimiza gradiente² + 3·laplaciano², então não cria pico nem vale). O anel
  colado na borda da face recebe o perfil da borda medido ao longo dela com mediana de 41 linhas (tira a
  lasca); no topo e à esquerda, onde a foto já é lisa, o preenchimento entra aos poucos em 14 px;
- o flanco da linha escura da borda, na altura da lasca, também recebe o perfil mediano;
- lado esquerdo, uma pinta no escuro de cima e um borrão na aba: o mesmo preenchimento, em áreas pequenas;
- grão: o ruído fino medido na própria canopla, na mesma força.
As linhas e máscaras saem do cromado; cada acabamento é preenchido com os próprios pixels (as cores são
recolorações do mesmo quadro).

Conferência medida (criterios.md › q): `medir_reflexo_liso.py <img> 1975,775,2040,915` dá no máximo 0,02
(as -2 deram 0,036 a 0,070; as -3, 0,003 a 0,010). `--medir` aqui só compara o passa-alta antes e depois.
O brushed nickel sai daqui sem o escovado no trecho refeito: o escovado é refeito com `escovado.py`
(`recolorir_nk`) sobre o cromado novo, no recorte `svelte-limpo` com o peso `svelte-wmet.npy`, e colado só
na área mudada, com 15 px de transição (kit de 03/11 do projeto).

uso: python3 svelte_reflexo_liso.py entrada.png saida.png [--cromado cromado-2.png] [--medir]
"""
import argparse
import os

import cv2
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spl
from PIL import Image
from scipy.ndimage import binary_dilation, gaussian_filter1d, map_coordinates, median_filter

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CROMADO = os.path.join(RAIZ, "aprovadas", "10479CR", "espelho-de-aumento-parede-svelte-cromado-gardie-2.png")
ALFA, BETA = 1.0, 3.0
DR = 5            # a máscara da direita para 5 px antes do centro da linha escura da borda
FAIXA_LASCA = (770, 882)


def tensao(img, mask, alfa=ALFA, beta=BETA):
    """Preenche mask minimizando alfa*|grad u|^2 + beta*|lap u|^2, com os pixels fora da máscara fixos."""
    ys, xs = np.nonzero(mask)
    y0, y1 = ys.min() - 3, ys.max() + 4
    x0, x1 = xs.min() - 3, xs.max() + 4
    m = mask[y0:y1, x0:x1]
    sub = img[y0:y1, x0:x1].astype(float)
    idx = -np.ones(m.shape, int)
    uy, ux = np.nonzero(m)
    idx[uy, ux] = np.arange(len(uy))
    I, J, V, Bs = [], [], [], []
    r = 0

    def termo(pts, peso):
        nonlocal r
        b = np.zeros(sub.shape[2])
        tem = False
        for yy, xx, c in pts:
            if idx[yy, xx] >= 0:
                I.append(r); J.append(idx[yy, xx]); V.append(c * peso); tem = True
            else:
                b -= c * peso * sub[yy, xx]
        if tem:
            Bs.append(b); r += 1

    sa, sb = np.sqrt(alfa), np.sqrt(beta)
    for y, x in zip(*np.nonzero(binary_dilation(m, iterations=1))):
        termo([(y, x, -1.0), (y, x + 1, 1.0)], sa)
        termo([(y, x, -1.0), (y + 1, x, 1.0)], sa)
        if beta > 0:
            termo([(y, x, -4.0), (y + 1, x, 1.0), (y - 1, x, 1.0), (y, x + 1, 1.0), (y, x - 1, 1.0)], sb)
    A = sp.csr_matrix((V, (I, J)), shape=(r, len(uy)))
    B = np.array(Bs)
    lu = spl.splu((A.T @ A).tocsc())
    out = img.astype(float).copy()
    for ch in range(sub.shape[2]):
        blk = out[y0:y1, x0:x1, ch]
        blk[uy, ux] = lu.solve(A.T @ B[:, ch])
    return out


def geometria(Lc):
    """Linhas da canopla no cromado: borda da face (xf por y), cunha do bloco (pw) e topo da barra (yb por x)."""
    L = cv2.GaussianBlur(Lc, (0, 0), 1.0)
    gy = [700, 730, 760, 780, 800, 825, 850, 875, 900, 925, 945]
    gx = [2025, 2045, 2060, 2072, 2080, 2090, 2098, 2103, 2106, 2108, 2109]
    Y = np.arange(700, 950)
    xe = []
    for y in Y:
        g = int(np.interp(y, gy, gx))
        xe.append(g - 10 + int(np.argmin(L[y, g - 10:g + 10])))
    xf = np.polyval(np.polyfit(Y, np.array(xe, float), 4), Y)
    yw = np.arange(868, 946)
    xw = np.array([1895 + np.nonzero(L[y, 1895:2010] > 90)[0][0] for y in yw], float)
    ok = np.ones(len(xw), bool)
    for _ in range(3):
        pw = np.polyfit(yw[ok], xw[ok], 2)
        ok = np.abs(np.polyval(pw, yw) - xw) < 3
    Xb = np.arange(1960, 2110)
    yb = []
    for x in Xb:
        ys = np.nonzero(L[915:965, x] < 90)[0]
        yb.append(915 + ys[0] if len(ys) else 965)
    yb = median_filter(np.array(yb, float), 5)
    return Y, xf, pw, yb


def mascara_direita(shape, Y, xf, pw, yb):
    M = np.zeros(shape, bool)
    for y in range(715, 950):
        xl = 1915 if y < 866 else max(1915, np.polyval(pw, y) + 6)
        xr = xf[y - 700] - DR
        for x in range(int(np.ceil(xl)), int(np.floor(xr)) + 1):
            if 1960 <= x < 2110 and y > yb[x - 1960] - 8:
                continue
            M[y, x] = True
    return M


def mascaras_pequenas(shape):
    """Lado esquerdo (risco junto do bloco, pintas e arcos do rebaixo antigo), pinta no escuro de cima e
    borrão na aba da direita."""
    esq = np.zeros(shape, np.uint8)
    cv2.fillPoly(esq, [np.array([(1590, 690), (1602, 668), (1626, 664), (1648, 690), (1648, 735), (1638, 740),
                                 (1637, 782), (1620, 792), (1596, 784), (1590, 750)], np.int32)], 1)
    topo = np.zeros(shape, np.uint8)
    cv2.circle(topo, (1785, 671), 11, 1, -1)
    aba = np.zeros(shape, np.uint8)
    cv2.ellipse(aba, (2132, 786), (7, 16), -22, 0, 360, 1, -1)
    return [esq.astype(bool), topo.astype(bool), aba.astype(bool)]


def ruido(a):
    return (a - cv2.blur(a, (3, 3)))[1:-1, 1:-1].std(axis=(0, 1))


def alisar(rgba, Lc):
    img = rgba[..., :3].astype(float)
    H, W = Lc.shape
    Y, xf, pw, yb = geometria(Lc)
    M = mascara_direita((H, W), Y, xf, pw, yb)
    anel = binary_dilation(M, iterations=2) & ~M
    ds = np.arange(-14, 11)
    P = np.zeros((len(Y), len(ds), 3))
    for j, d in enumerate(ds):
        for c in range(3):
            P[:, j, c] = map_coordinates(img[..., c], [Y.astype(float), xf + d], order=1)
    Ps = gaussian_filter1d(median_filter(P, size=(41, 1, 1), mode="nearest"), 6, axis=0, mode="nearest")

    def perfil(y, x):
        j = np.clip(x - xf[y - 700] + 14, 0, len(ds) - 1.001)
        j0 = int(j); f = j - j0
        return Ps[y - 700, j0] * (1 - f) + Ps[y - 700, min(j0 + 1, len(ds) - 1)] * f

    base = img.copy()
    sm = cv2.GaussianBlur(img, (0, 0), 3)
    ay, ax = np.nonzero(anel)
    junto_borda = lambda y, x: 700 <= y < 950 and x > xf[y - 700] - 14
    for y, x in zip(ay, ax):
        base[y, x] = perfil(y, x) if junto_borda(y, x) else sm[y, x]
    out = tensao(base, M)
    # flanco da linha escura da borda na altura da lasca
    y0, y1 = FAIXA_LASCA
    for y in range(y0, y1):
        rampa = min(1.0, (y - y0) / 8, (y1 - 1 - y) / 8)
        for x in range(int(np.floor(xf[y - 700] - DR)) + 1, int(np.floor(xf[y - 700] + 8.0)) + 1):
            if not M[y, x]:
                out[y, x] = img[y, x] + rampa * (perfil(y, x) - img[y, x])
    # topo e esquerda: o preenchido entra aos poucos (a foto ali já é lisa)
    macio = np.zeros((H, W), bool)
    for y, x in zip(ay, ax):
        dura = junto_borda(y, x) or (1960 <= x < 2110 and y > yb[x - 1960] - 12) or \
            (y >= 866 and x < np.polyval(pw, y) + 8)
        macio[y, x] = not dura
    dm = cv2.distanceTransform((~macio).astype(np.uint8), cv2.DIST_L2, 5)
    wi = np.clip(dm / 14, 0, 1)
    wi = wi * wi * (3 - 2 * wi)
    out[M] = img[M] + wi[M][:, None] * (out[M] - img[M])
    peso_grao = np.where(M, wi, 0.0)
    # áreas pequenas
    for m in mascaras_pequenas((H, W)):
        b2 = out.copy()
        an2 = binary_dilation(m, iterations=2) & ~m
        b2[an2] = cv2.GaussianBlur(out, (0, 0), 3)[an2]
        f2 = tensao(b2, m)
        d2 = cv2.distanceTransform(m.astype(np.uint8), cv2.DIST_L2, 5)
        w2 = np.clip(d2 / 5, 0, 1)
        out[m] = out[m] + w2[m][:, None] * (f2[m] - out[m])
        peso_grao = np.where(m, np.maximum(peso_grao, w2), peso_grao)
    sig = (ruido(img[1012:1032, 1895:1925]) + ruido(img[780:800, 1905:1935])) / 2
    puro = ruido(np.random.default_rng(0).normal(0, 1, (400, 400, 1)))[0]
    g = np.random.default_rng(10479).normal(0, 1, (H, W))[..., None] * (sig / puro)[None, None, :]
    out += g * peso_grao[..., None]
    res = rgba.copy()
    res[..., :3] = np.clip(out + 0.5, 0, 255).astype(np.uint8)
    return res, M


def medir(rgba, M):
    """Desvio do passa-alta (σ 12 px) da luminância no miolo do reflexo da direita e no grão de referência."""
    L = rgba[..., :3].astype(float).mean(-1)
    hp = L - cv2.GaussianBlur(L, (0, 0), 12)
    miolo = cv2.erode(M.astype(np.uint8), np.ones((25, 25), np.uint8)).astype(bool)
    ref = hp[600:640, 1720:1760]   # área lisa no escuro de cima da canopla
    return float(hp[miolo].std()), float(np.abs(hp[miolo]).max()), float(ref.std())


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("entrada"); ap.add_argument("saida")
    ap.add_argument("--cromado", default=CROMADO)
    ap.add_argument("--medir", action="store_true")
    a = ap.parse_args()
    rgba = np.asarray(Image.open(a.entrada).convert("RGBA")).copy()
    assert rgba.shape[:2] == (3365, 3365), rgba.shape
    Lc = np.asarray(Image.open(a.cromado).convert("RGB")).astype(float).mean(-1)
    res, M = alisar(rgba, Lc)
    Image.fromarray(res, "RGBA").save(a.saida, optimize=True)
    if a.medir:
        antes = medir(rgba, M); depois = medir(res, M)
        print("passa-alta no reflexo (desvio, pico | grão de referência): antes %.1f, %.0f | %.1f  depois %.1f, %.0f | %.1f"
              % (antes + depois))
    print(a.saida)
