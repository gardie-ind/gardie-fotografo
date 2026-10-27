"""Brushed nickel v2 (aprovado pelo Thiago em 22/10/2026): escovado visível.
- reflexo espalhado ATRAVÉS do riscado (é assim que o escovado espalha a luz):
  média gaussiana ponderada pelo metal na direção perpendicular à da peça;
- riscado em duas escalas, seguindo a peça (linha de corrente, acompanha a
  curva do aro): fios finos (~1 px, 120 px de comprimento, 5%) e faixas largas
  (~6 px, 240 px, 3,5%), que somem nos 4 px junto da silhueta;
- os vãos e as faixas escuras do reflexo seguram o escuro, com borda de 2,5 px.
O resto (tom da referência Deca, faixa de luminância 0,10 a 0,72, o que é
metal) é o do piloto aprovado."""
import numpy as np
import scipy.ndimage as ndi
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from acabamentos import lin, srgb, tingir, borrar_mascarado


def direcao(Ylum, peso, s_lum=8, s_msk=12):
    """Sentido de cada peça (como direcao_das_pecas do piloto, com o tensor
    mais suave: ~32 e ~48 px, para o riscado não rodar em volta de rebites e
    pinos) e a coerência do sentido (0 = indefinido, 1 = um sentido só)."""
    H, W = Ylum.shape
    q = 4
    def tensor(img, s):
        gx_, gy_ = ndi.sobel(img, 1), ndi.sobel(img, 0)
        return [ndi.gaussian_filter(v, s) for v in (gx_ * gx_, gy_ * gy_, gx_ * gy_)]
    lum = ndi.zoom(srgb(Ylum) * peso, 1 / q, order=1)
    msk = ndi.zoom(peso, 1 / q, order=1)
    a1, a2 = tensor(lum, s_lum), tensor(msk, s_msk)
    Jxx, Jyy, Jxy = [x + 0.5 * y for x, y in zip(a1, a2)]
    coh = np.sqrt((Jxx - Jyy) ** 2 + 4 * Jxy ** 2) / np.maximum(Jxx + Jyy, 1e-9)
    ang = 0.5 * np.arctan2(2 * Jxy, Jxx - Jyy) + np.pi / 2
    zy, zx = H / coh.shape[0], W / coh.shape[1]
    c2 = ndi.zoom(np.cos(2 * ang), (zy, zx), order=1)[:H, :W]
    s2 = ndi.zoom(np.sin(2 * ang), (zy, zx), order=1)[:H, :W]
    coh = ndi.zoom(coh, (zy, zx), order=1)[:H, :W]
    a = 0.5 * np.arctan2(s2, c2)
    return np.cos(a).astype(np.float32), np.sin(a).astype(np.float32), np.clip(coh, 0, 1).astype(np.float32)


def corrente(campo, dx, dy, idx, meio, passo=1.0, peso=None):
    """Média de campo (H x W) ao longo da linha de corrente do campo de direções
    (dx, dy), meio comprimento `meio` px, para os pixels idx."""
    iy, ix = idx
    acc = ndi.map_coordinates(campo, [iy, ix], order=1, mode='nearest').astype(np.float32)
    wac = np.ones(len(iy), np.float32)
    for sinal in (1, -1):
        py, px = iy.astype(np.float32), ix.astype(np.float32)
        vx, vy = dx[iy, ix] * sinal, dy[iy, ix] * sinal
        for _ in range(int(meio / passo)):
            px, py = px + passo * vx, py + passo * vy
            nx = ndi.map_coordinates(dx, [py, px], order=1, mode='nearest')
            ny = ndi.map_coordinates(dy, [py, px], order=1, mode='nearest')
            s = np.sign(nx * vx + ny * vy)
            s[s == 0] = 1
            vx, vy = nx * s, ny * s
            w = np.ones(len(iy), np.float32) if peso is None else ndi.map_coordinates(peso, [py, px], order=1, mode='nearest')
            acc += w * ndi.map_coordinates(campo, [py, px], order=1, mode='nearest')
            wac += w
    return acc / np.maximum(wac, 1e-6)


def atraves(campo, dx, dy, idx, peso, sigma):
    """Média gaussiana de campo ao longo da perpendicular à peça, ponderada por peso."""
    iy, ix = idx
    px_, py_ = -dy[iy, ix], dx[iy, ix]
    acc = np.zeros(len(iy), np.float32)
    wac = np.zeros(len(iy), np.float32)
    for t in np.arange(-3 * sigma, 3 * sigma + 0.01, 1.0):
        g = np.exp(-0.5 * (t / sigma) ** 2)
        py, px = iy + t * py_, ix + t * px_
        w = g * ndi.map_coordinates(peso, [py, px], order=1, mode='constant')
        acc += w * ndi.map_coordinates(campo, [py, px], order=1, mode='nearest')
        wac += w
    return acc / np.maximum(wac, 1e-6)


def campos(Y, peso_met, area, semente=10554, meio_fino=60, meio_largo=120):
    """Sentido das peças e riscado (fino e largo), normalizados. Dependem só da
    forma das peças: calcule uma vez por modelo e use nas versões ligada e
    desligada, para o riscado ser o mesmo nas duas."""
    H, W = Y.shape
    idx = np.nonzero(area)
    dx, dy, coh = direcao(Y, peso_met)
    rng = np.random.default_rng(semente)
    r1 = rng.standard_normal((H, W)).astype(np.float32)
    r2 = ndi.gaussian_filter(rng.standard_normal((H, W)).astype(np.float32), 3.0)
    fino = np.zeros((H, W), np.float32)
    largo = np.zeros((H, W), np.float32)
    fino[idx] = corrente(r1, dx, dy, idx, meio_fino, 1.0)
    del r1
    largo[idx] = corrente(r2, dx, dy, idx, meio_largo, 2.0)
    del r2
    fino /= max(fino[idx].std(), 1e-6)
    largo /= max(largo[idx].std(), 1e-6)
    # onde o sentido é indefinido (cruzamento de peças, centro de rebite) o
    # riscado enfraquece, em vez de virar emenda
    forca = np.clip((coh - 0.15) / 0.35, 0, 1)
    return dx, dy, fino * forca, largo * forca


def escovado(Y, peso_met, area, cmp=None, sig_atraves=5.0, amp_fino=0.05, amp_largo=0.035,
             faixa=(0.10, 0.72), cap_sigma=2.5, cap_folga=0.08):
    idx = np.nonzero(area)
    dx, dy, fino, largo = cmp if cmp is not None else campos(Y, peso_met, area)
    # reflexo: espalhado através do riscado (é assim que o escovado espalha a luz)
    Ya = Y.copy()
    Ya[idx] = atraves(Y, dx, dy, idx, peso_met, sig_atraves)
    Yb = borrar_mascarado(Ya[..., None], peso_met, 1.0)[..., 0]
    del Ya
    # vãos e faixas escuras seguram o escuro, com borda macia
    Y25 = borrar_mascarado(Y[..., None], peso_met, cap_sigma)[..., 0]
    Yb = np.minimum(Yb, Y25 + cap_folga)
    del Y25
    Yd = faixa[0] + (faixa[1] - faixa[0]) * np.clip(Yb, 0, 1)
    # junto da silhueta e dos vãos o riscado some em 4 px: o contorno fica liso
    borda = np.clip((ndi.distance_transform_edt(peso_met > 0.5) - 1) / 4, 0, 1)
    return Yd * (1 + borda * (amp_fino * fino + amp_largo * largo))


def luminancia(R):
    F = lin(R[..., :3].astype(np.float32) / 255)
    return F, F @ np.array([0.2126, 0.7152, 0.0722], np.float32)


def recolorir_nk(R, w_met, cmp=None, **kw):
    alfa8 = R[..., 3]
    F, Y = luminancia(R)
    peso_met = (w_met * alfa8 / 255).astype(np.float32)
    area = w_met > 0.001
    metal = tingir(escovado(Y, peso_met, area, cmp=cmp, **kw), 'brushed-nickel')
    out = F * (1 - w_met[..., None]) + metal * w_met[..., None]
    rgb = (srgb(out) * 255 + 0.5).astype(np.uint8)
    return np.dstack([rgb, alfa8])
