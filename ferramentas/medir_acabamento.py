"""Medidas de acabamento nas stills recoloridas (critério b).

tom <imagem> [<imagem> ...] [--papel x0,y0,x1,y1[;x0,y0,x1,y1]] [--mascara m.png]
    Matiz e croma do metal (CIELAB, D65) por faixa de L*, nos pixels do
    produto com (R - B) / (R + G + B) > 0,1 em luz linear. Foto de celular
    em Display P3 é convertida para sRGB linear sem cortar a gama; com
    --papel o branco é acertado pela mediana dessas caixas de papel, e com
    --mascara só entram os pixels brancos da máscara. Red gold: compare com a
    peça real (guia/criterios.md, item b), medida assim:
    tom referencias/red-gold/foto-real-red-gold-parede-2026-10-22.jpeg
        --papel "1280,1230,1340,1290;1330,1580,1390,1640"
        --mascara referencias/red-gold/mascara-aros-2026-10-22.png

carcaca <ligada> <desligada>
    Black matte: luminância sRGB p99,9 do produto fora da cabeça na still
    desligada. A cabeça (vidro e anel de luz) é achada pela luz do LED, que é
    a diferença entre a ligada e a desligada; o furo é preenchido e dilatado
    em 2% do Ø. Mede a parte do produto fora da cabeça acima de 180 de
    luminância sRGB. Em 22/10/2026: carcaça branca, 1,1 a 13,8%; pintada de
    preto, e Flex e Mobile (sem carcaça branca), 0 a 0,1%.
"""
import io, sys
import numpy as np
from PIL import Image, ImageCms
from scipy import ndimage as ndi

M_P3 = np.array([[1.2249, -0.2247, 0], [-0.0420, 1.0419, 0], [-0.0197, -0.0786, 1.0979]])
M_XYZ = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
W = M_XYZ.sum(1)
FAIXAS = ((20, 40), (40, 55), (55, 70), (70, 85))


def lin(c):
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def abrir(p):
    im = Image.open(p)
    p3 = 'icc_profile' in im.info and 'P3' in ImageCms.getProfileDescription(
        ImageCms.ImageCmsProfile(io.BytesIO(im.info['icc_profile'])))
    a = np.asarray(im.convert('RGBA')).astype(np.float32) / 255
    L = lin(a[..., :3])
    if p3:
        L = L @ M_P3.T
    return L, a[..., 3]


def lab(L):
    X = L @ M_XYZ.T / W
    f = lambda t: np.where(t > 0.008856, np.cbrt(np.maximum(t, 0)), 7.787 * t + 16 / 116)
    fx, fy, fz = f(X[..., 0]), f(X[..., 1]), f(X[..., 2])
    return np.stack([116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)], -1)


def tom(caminhos, papel=None, mascara=None):
    for p in caminhos:
        L, al = abrir(p)
        if papel:
            ref = np.median(np.concatenate([L[y0:y1, x0:x1].reshape(-1, 3) for x0, y0, x1, y1 in papel]), 0)
            L = L / (ref / ref[1])
        ch = (L[..., 0] - L[..., 2]) / np.maximum(L.sum(-1), 1e-6)
        sel = (al > 0.99) & (ch > 0.1) & (L @ M_XYZ[1] > 0.01)
        if mascara:
            sel &= np.asarray(Image.open(mascara).convert('L')) > 127
        Lb = lab(L[sel])
        h = np.degrees(np.arctan2(Lb[:, 2], Lb[:, 1])); C = np.hypot(Lb[:, 1], Lb[:, 2])
        print(p)
        for lo, hi in FAIXAS:
            s = (Lb[:, 0] >= lo) & (Lb[:, 0] < hi)
            if s.sum() > 200:
                print(f'  L* {lo}-{hi}: matiz {np.median(h[s]):5.1f}°  croma {np.median(C[s]):5.1f}  (n={s.sum()})')


def carcaca(lig, apa):
    L1, a1 = abrir(lig); L2, a2 = abrir(apa)
    Y = lambda L: L @ M_XYZ[1]
    E = np.clip(Y(L1) - Y(L2) - 0.004, 0, None)
    nivel = np.percentile(E[E > 0.3], 50)
    anel = ndi.binary_opening(E > 0.5 * nivel, iterations=2)
    lb, _ = ndi.label(anel); anel = lb == np.argmax(np.bincount(lb.ravel())[1:]) + 1
    cabeca = ndi.binary_fill_holes(anel)
    ys, xs = np.where(cabeca)
    d = int(0.02 * max(np.ptp(ys), np.ptp(xs))) + 2
    cabeca = ndi.binary_dilation(cabeca, iterations=d)
    fora = (a2 > 0.5) & ~cabeca
    ys_srgb = np.where(Y(L2) <= 0.0031308, Y(L2) * 12.92, 1.055 * np.clip(Y(L2), 0, 1) ** (1 / 2.4) - 0.055) * 255
    claro = 100 * (ys_srgb[fora] > 180).mean()
    print(f'{apa}: p99,9 = {np.percentile(ys_srgb[fora], 99.9):.0f}, acima de 180 = {claro:.2f}% do produto fora da cabeça  (n={fora.sum()})')


if __name__ == '__main__':
    a = sys.argv[1:]
    if a and a[0] == 'tom':
        papel = mascara = None
        if '--papel' in a:
            i = a.index('--papel'); a, v = a[:i] + a[i + 2:], a[i + 1]
            papel = [[int(n) for n in caixa.split(',')] for caixa in v.split(';')]
        if '--mascara' in a:
            i = a.index('--mascara'); a, mascara = a[:i] + a[i + 2:], a[i + 1]
        tom(a[1:], papel, mascara)
    elif a and a[0] == 'carcaca':
        carcaca(a[1], a[2])
    else:
        print(__doc__)
