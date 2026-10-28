# -*- coding: utf-8 -*-
"""Royale Lux 10288: troca a alça de vareta meia-cana pela barra chata 0007-AL, sem IA.

Thiago, 28/10/2026, 20:36: "Essa alça da foto é vareta 1/2 cana, e o modelo da
vida real é barra chata de alumínio, igual o do Classique Lux e da foto
dourada". Roda depois do pescoço (royale_foguetinho.py), na foto já centrada.

Forma: a do desenho 25 "Alça Alumínio 365x15,9x3mm" (gardie-engenharia,
conjuntos/lux/modelos.py): barra de 15,9 × 3 curvada em U, R103,10 por dentro
e R106,28 por fora, em volta do pivô; pernas até 114 de altura, furo Ø5 a 8,5
da ponta (ponta arredondada em volta do furo). Ela é traçada raio a raio na
câmera da still, que sai de três medidas da própria foto:
- o eixo da coluna (x = 2215) passa pelo fundo da alça;
- o botão do pivô (3320, 1462) fica no furo;
- do furo ao topo da borda do foguetinho (y = 2740) cabem os 105,5 mm do
  desenho, a 12,1 px/mm. Com a câmera à altura do pivô a ≈1 m (a elipse da
  base dá ≈12° de inclinação lá embaixo), o pivô à vista dá o giro da alça
  (≈35°).

Cromado: o da barra real do Classique Lux (aprovadas/10202*), fotografada no
mesmo estúdio e no mesmo ângulo. Ali a barra aparece como uma quina estreita
escura (a borda de 3 mm, de frente) e uma face larga clara (os 15,9 mm, de
lado). Cada pixel da barra nova copia o pixel do Classique na mesma face, na
mesma fração da largura e no trecho do braço com a mesma inclinação na foto.
O alfa é o mesmo nos 4138 px de todos os acabamentos e posições do Classique,
então a faixa é medida uma vez na 10202CR-4.

Composição:
- no braço do lado do pivô à vista, a barra fica na frente da cabeça; embaixo
  e do outro lado, atrás dela (a borda da frente da cabeça desce na frente do
  assento);
- a vareta velha que a barra não cobre some (fica o fundo transparente);
- o botão do pivô fica por cima de tudo, com os pixels originais;
- sobre o assento vai o niple aberto 0011-AL (aba Ø14,5 × 1 e calota de 2,5),
  com o reflexo do próprio corpo da coluna.
"""
import os
import warnings

import cv2
import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CLASSIQUE = os.path.join(RAIZ, "aprovadas", "10202{acab}",
                         "espelho-de-aumento-mesa-led-classique-lux-{nome}-gardie-{n}.png")
NOME_ACAB = {"CR": "cromado", "GL": "dourado", "GL.RD": "red-gold", "NK.BU": "brushed-nickel",
             "BL.MT": "black-matte"}
# posição do Royale -> posição do Classique no mesmo estado de LED (no 10202CR a numeração é outra)
POS_CR = {"1": "3", "2": "4", "3": "8", "4": "9"}

# barra 0007-AL (mm)
RI, RO, MEIA = 103.10, 106.28, 15.9 / 2
TOPO = 114.0 - RO                 # pernas acima do centro do arco
Y_FURO = TOPO - 8.5               # furo a 8,5 da ponta; a ponta é um semicírculo em volta dele
RC = (RI + RO) / 2
F_EXT, F_INT, F_FRENTE, F_TRAS, F_PONTA = 1, 2, 3, 4, 5

# câmera da still (foto centrada de 4379 px, depois do pescoço)
PSI, DIST, K, U_O, V_O = np.radians(34.74), 1030.0, 12.1, 2215.0, 1452.0
LADO = 4379
CAIXA = (1700, 1300, 3500, 2760)  # onde a barra pode aparecer
SS = 3                            # superamostragem por eixo
S_FRENTE = 80.0                   # mm de arco a partir do fundo: daqui ao pivô, a barra fica na frente da cabeça
Y_COLUNA = 2740                   # topo da borda do foguetinho
# fronteira cabeça x vareta por baixo da cabeça (abaixo dela era vareta)
B = np.array([(1852, 2669), (1868, 2670), (1900, 2668), (1960, 2667), (2050, 2664), (2100, 2660),
              (2150, 2652)], float)
FONTE_NIPLE = (2905, 2945)        # linhas limpas do corpo da coluna


def projetar(P):
    x, y, z = P[..., 0], P[..., 1], P[..., 2]
    c, s = np.cos(PSI), np.sin(PSI)
    X = x * c - z * s
    Z = x * s + z * c
    w = DIST - Z
    f = K * DIST
    return np.stack([U_O + f * X / w, V_O - f * y / w], -1)


def raios(u, v):
    """Raios da câmera no referencial da alça (x ao longo do pivô, y para cima, z normal ao U)."""
    c, s = np.cos(PSI), np.sin(PSI)
    f = K * DIST
    dX = (u - U_O) / f
    dY = -(v - V_O) / f
    dZ = -np.ones_like(u)
    o = np.array([DIST * s, 0.0, DIST * c])
    return o, np.stack([dX * c + dZ * s, dY, -dX * s + dZ * c], -1)


def tracar(o, d):
    """Face, s (mm de arco a partir do fundo, + para o pivô à vista) e a coordenada
    de través (z nas faces largas, raio nas quinas) do ponto mais próximo."""
    n = d.shape[0]
    T = np.full(n, np.inf)
    FACE = np.zeros(n, np.int8)
    S = np.zeros(n, np.float32)
    A = np.zeros(n, np.float32)
    dx, dy, dz = d[:, 0], d[:, 1], d[:, 2]

    def aceitar(t, ok, face, x, y, z, atrav):
        ok = ok & (t > 0) & (t < T)
        s = np.where(y <= 0, RC * np.arctan2(x, -y), np.sign(x) * (RC * np.pi / 2 + y))
        T[ok] = t[ok]
        FACE[ok] = face
        S[ok] = s[ok]
        A[ok] = atrav[ok]

    for R, face in ((RO, F_EXT), (RI, F_INT)):
        a = dx * dx + dy * dy
        b = 2 * (o[0] * dx + o[1] * dy)
        c = o[0] ** 2 + o[1] ** 2 - R * R
        disc = b * b - 4 * a * c
        sq = np.sqrt(np.maximum(disc, 0))
        for sg in (-1, 1):
            t = (-b + sg * sq) / (2 * a)
            x, y, z = o[0] + t * dx, o[1] + t * dy, o[2] + t * dz
            aceitar(t, (disc >= 0) & (y <= 0) & (np.abs(z) <= MEIA), face, x, y, z, z)
        for sx in (-1, 1):  # pernas: planos x = ±R
            t = (sx * R - o[0]) / dx
            x, y, z = o[0] + t * dx, o[1] + t * dy, o[2] + t * dz
            aceitar(t, (y > 0) & (z * z + np.maximum(y - Y_FURO, 0) ** 2 <= MEIA * MEIA), face, x, y, z, z)
    for zs, face in ((MEIA, F_FRENTE), (-MEIA, F_TRAS)):
        t = (zs - o[2]) / dz
        x, y, z = o[0] + t * dx, o[1] + t * dy, o[2] + t * dz
        r = np.where(y <= 0, np.hypot(x, y), np.abs(x))
        aceitar(t, (r >= RI) & (r <= RO) & (y <= Y_FURO), face, x, y, z, r)
    # ponta: cilindro de raio MEIA em volta do furo, eixo ao longo de x
    a = dy * dy + dz * dz
    b = 2 * ((o[1] - Y_FURO) * dy + o[2] * dz)
    c = (o[1] - Y_FURO) ** 2 + o[2] ** 2 - MEIA * MEIA
    disc = b * b - 4 * a * c
    sq = np.sqrt(np.maximum(disc, 0))
    for sg in (-1, 1):
        t = (-b + sg * sq) / (2 * a)
        x, y, z = o[0] + t * dx, o[1] + t * dy, o[2] + t * dz
        aceitar(t, (disc >= 0) & (y > Y_FURO) & (np.abs(x) >= RI) & (np.abs(x) <= RO), F_PONTA, x, y, z,
                np.abs(x))
    return FACE, S, A


_GEOMETRIA = None


def geometria():
    """Faces, s e través de cada subamostra da CAIXA (calculado uma vez)."""
    global _GEOMETRIA
    if _GEOMETRIA is None:
        x0, y0, x1, y1 = CAIXA
        us = x0 + (np.arange((x1 - x0) * SS) + 0.5) / SS
        vs = y0 + (np.arange((y1 - y0) * SS) + 0.5) / SS
        F = np.zeros((len(vs), len(us)), np.int8)
        S = np.zeros(F.shape, np.float32)
        A = np.zeros(F.shape, np.float32)
        for i, v in enumerate(vs):
            o, d = raios(us, np.full_like(us, v))
            F[i], S[i], A[i] = tracar(o, d)
        _GEOMETRIA = (F, S, A)
    return _GEOMETRIA


def _robusto(y, v, grau=4):
    ok = np.ones(len(y), bool)
    for _ in range(5):
        c = np.polyfit(y[ok], v[ok], grau)
        r = v - np.polyval(c, y)
        ok = np.abs(r) < 3 * 1.4826 * np.median(np.abs(r[ok])) + 0.5
    return np.polyval(c, y)


_FAIXA = None


def faixa_classique():
    """Por linha do braço do Classique: borda de dentro, degrau quina/face e borda de fora."""
    global _FAIXA
    if _FAIXA is None:
        im = np.asarray(Image.open(CLASSIQUE.format(acab="CR", nome="cromado", n=4))).astype(float)
        a, L = im[..., 3], im[..., :3].mean(-1)
        linhas = []
        for y in range(1520, 2702, 2):
            d = np.diff(np.r_[0, (a[y] > 128).astype(int), 0])
            s, e = np.nonzero(d == 1)[0], np.nonzero(d == -1)[0]
            i1 = e[-1]
            i0 = s[-1] if (y >= 1790 and len(s) >= 2 and e[-1] - s[-1] >= 40) else np.nan
            lo = i1 - 125
            g = np.diff(L[y, lo:i1])
            linhas.append((y, i0, lo + np.argmax(g[3:-30]) + 3 + 0.5, i1))
        fx = np.array(linhas, float)
        sem = np.isnan(fx[:, 1])
        fx[sem, 1] = fx[sem, 2] - np.nanmedian((fx[:, 2] - fx[:, 1])[(fx[:, 0] >= 1790) & (fx[:, 0] < 1900)])
        ys = fx[:, 0]
        lin = {nome: _robusto(ys, fx[:, i]) for i, nome in ((1, "int"), (2, "degrau"), (3, "ext"))}
        meio = np.polyval(np.polyfit(ys, (lin["int"] + lin["ext"]) / 2, 4), ys)
        tC = np.degrees(np.arctan2(np.gradient(ys), np.gradient(meio)))
        _FAIXA = (ys, lin, tC)
    return _FAIXA


def linha_classique(s):
    """s (mm de arco) -> linha do braço do Classique com a mesma inclinação na foto."""
    ys, _, tC = faixa_classique()
    ss = np.linspace(0, RC * np.pi / 2, 400)
    al = ss / RC
    uv = projetar(np.stack([RC * np.sin(al), -RC * np.cos(al), 0 * al], -1))
    tR = np.degrees(np.unwrap(np.arctan2(-np.gradient(uv[:, 1]), -np.gradient(uv[:, 0]))))
    tR = np.where(tR < 0, tR + 360, tR)
    o = np.argsort(tC)
    return np.interp(np.interp(np.abs(s), ss, tR), tC[o], ys[o])


def barra(classique):
    """Cobertura, cor (0-1) e s (mm) da barra nova em cada pixel da CAIXA."""
    F, S, A = geometria()
    ys, lin, _ = faixa_classique()
    hit = F > 0
    yC = linha_classique(S[hit])
    g = {k: np.interp(yC, ys, v) for k, v in lin.items()}
    f, a = F[hit], A[hit]
    larga = (f == F_EXT) | (f == F_INT)
    ins = 1.5   # longe do contorno do Classique, onde o alfa já cai
    x0 = np.where(larga, g["degrau"] + ins, g["int"] + ins)
    x1 = np.where(larga, g["ext"] - ins, g["degrau"] - ins)
    t = np.where(larga, (MEIA - a) / (2 * MEIA), (a - RI) / (RO - RI))
    xC = x0 + np.clip(t, 0, 1) * (x1 - x0)
    cor = np.zeros(F.shape + (3,), np.float32)
    cor[hit] = np.stack([map_coordinates(classique[..., c], [yC, xC], order=1) for c in range(3)], -1)
    h, w = F.shape[0] // SS, F.shape[1] // SS
    blocos = lambda m: m.reshape(h, SS, w, SS, *m.shape[2:])
    n = blocos(hit).sum((1, 3))
    cob = n / SS ** 2
    rgb = blocos(cor).sum((1, 3)) / np.maximum(n, 1)[..., None]
    with np.errstate(all="ignore"), warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)      # blocos sem barra ficam NaN
        s = np.nanmean(blocos(np.where(hit, S, np.nan)), axis=(1, 3))
    return cob.astype(np.float32), rgb.astype(np.float32), s


def _sobre(top_rgb, top_a, bot):
    a = top_a + bot[..., 3] * (1 - top_a)
    c = (top_rgb * top_a[..., None] + bot[..., :3] * bot[..., 3:] * (1 - top_a[..., None])) / np.maximum(a, 1e-6)[..., None]
    return np.concatenate([c, a[..., None]], -1)


def _botao(X, Y):
    """Arruela, pescoço e corpo do botão do pivô (pixels originais por cima da barra)."""
    return ((((X - 3283) / 24.0) ** 2 + ((Y - 1455) / 58.0) ** 2 <= 1) |
            ((X >= 3283) & (X <= 3304) & (Y >= 1398) & (Y <= 1513)) |
            ((X >= 3302) & (X <= 3350) & (Y >= 1425) & (Y <= 1495)) |
            ((X >= 3348) & (X <= 3440) & (Y >= 1396) & (Y <= 1529)) |
            ((((X - 3440) / 24.0) ** 2 + ((Y - 1462) / 67.0) ** 2) <= 1))


def trocar_alca(tela, classique):
    """tela: RGBA uint8 do Royale com o pescoço novo, centrada (4379 px).
    classique: RGBA uint8 do Classique Lux no mesmo acabamento e estado de LED."""
    if tela.shape[:2] != (LADO, LADO):
        raise SystemExit("a foto do Royale devia ter %d px (depois do pescoço)" % LADO)
    roy = tela.astype(np.float32) / 255
    x0, y0, x1, y1 = CAIXA
    cob_c, rgb_c, s_c = barra(classique.astype(np.float32))
    H, W = roy.shape[:2]
    cob = np.zeros((H, W), np.float32)
    cob[y0:y1, x0:x1] = cob_c
    rgb = np.zeros((H, W, 3), np.float32)
    rgb[y0:y1, x0:x1] = rgb_c / 255
    sp = np.full((H, W), -999, np.float32)
    sp[y0:y1, x0:x1] = np.nan_to_num(s_c, nan=-999)
    Y, X = np.mgrid[0:H, 0:W]
    alfa = roy[..., 3]
    zona = (X >= x0) & (X < x1) & (Y >= y0) & (Y < Y_COLUNA)
    botao = _botao(X, Y)
    yB = np.interp(X, B[:, 0], B[:, 1])
    abaixoB = (X >= B[0, 0]) & (X <= B[-1, 0]) & (Y > yB)
    linhaB = (X >= B[0, 0]) & (X <= B[-1, 0]) & (np.abs(Y - yB) < 1.5)
    pegada = cv2.dilate((cob > 0).astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    s = cv2.dilate(sp, np.ones((7, 7), np.uint8))
    frente = pegada & (s > S_FRENTE)
    tras = pegada & ~frente
    # cabeça: o componente dela, sem a barra da frente, sem o botão e com a vareta cortada em B
    A = (alfa > 0) & zona & ~frente & ~botao & ~abaixoB & ~linhaB
    _, lab = cv2.connectedComponents(A.astype(np.uint8), connectivity=4)
    cab = lab == lab[1400, 2100]
    base = roy.copy()
    base[(alfa > 0) & zona & ~frente & ~botao & ~cab] = 0      # vareta velha fora da barra
    cx = np.full(H, np.nan)
    for yy in range(y0, y1):
        xs = np.nonzero(frente[yy] & (cob[yy] > 0.5))[0]
        if len(xs):
            cx[yy] = (xs[0] + xs[-1]) / 2
    with np.errstate(invalid="ignore"):
        base[frente & (X > cx[:, None]) & ~botao] = 0           # vareta velha por fora da barra
    out = _sobre(rgb, cob, base)
    # niple 0011-AL sobre o assento (centro da face de cima da barra, no eixo)
    y_base = projetar(np.array([0.0, -RI, 0.0]))[1]
    r_cal = (7.25 ** 2 + 2.5 ** 2) / (2 * 2.5)
    xs = np.arange(W, dtype=float)
    for yy in range(int(y_base - 3.5 * K) - 1, int(np.ceil(y_base)) + 1):
        h = (y_base - (yy + 0.5)) / K
        if h < 0 or h > 3.5:
            continue
        r = 7.25 if h <= 1.0 else np.sqrt(max(r_cal ** 2 - (r_cal - 2.5 + h - 1.0) ** 2, 0))
        fy = int(FONTE_NIPLE[0] + (FONTE_NIPLE[1] - FONTE_NIPLE[0]) * h / 3.5)
        lin = roy[fy]
        ii = np.nonzero(lin[2000:2450, 3] > 0.5)[0] + 2000
        cs, hs = (ii[0] + ii[-1] + 1) / 2, (ii[-1] - ii[0] + 1) / 2
        xsrc = cs + (xs + 0.5 - U_O) * hs / (7.25 * K) - 0.5   # o reflexo tem a largura da aba; a calota só recorta
        px = np.stack([np.interp(xsrc, xs, lin[:, c], left=0, right=0) for c in range(4)], -1)
        cobre = np.clip(r * K + 0.5 - np.abs(xs + 0.5 - U_O), 0, 1) * (px[:, 3] > 0)
        out[yy] = _sobre(px[None, :, :3], cobre[None], out[yy][None])[0]
    # cabeça na frente da barra (embaixo e do outro lado) e botão por cima de tudo
    for m in (tras & cab, botao & (alfa > 0)):
        out[m] = _sobre(roy[m][None, :, :3], roy[m][None, :, 3], out[m][None])[0]
    return np.clip(out * 255 + 0.5, 0, 255).astype(np.uint8)


def classique_de(acab, pos):
    n = POS_CR[pos] if acab == "CR" else pos
    return np.asarray(Image.open(CLASSIQUE.format(acab=acab, nome=NOME_ACAB[acab], n=n)).convert("RGBA"))
