# -*- coding: utf-8 -*-
"""Acabamento de câmera (25/10, Thiago: "Agora remova o aspecto de render e faça mais realista").

O render sai perfeito demais: sem o brilho que a lente espalha em volta do que é muito claro,
sem queda de luz nos cantos, sem a franja de cor das bordas e sem ruído do sensor. Este passo
aplica, nesta ordem e sempre igual (nada aleatório entre o aceso e o apagado do mesmo quadro):

1. brilho de lente (bloom) em luz linear: só o que passa de 0,75 espalha, em três raios (4, 18 e
   60 px), como o véu em volta do anel aceso e dos brilhos do cromo nas fotos reais; o véu não
   cai sobre a própria fonte, para o anel manter o tom do padrão;
2. vinheta: 9% de queda nos cantos;
3. aberração cromática lateral: vermelho +0,05% e azul −0,05% de escala (0,4 px no canto);
4. nitidez de câmera: máscara de nitidez leve (raio 1,2 px, 35%);
5. grão: ruído de luminância de 1,8/255 (menos nas altas luzes) e de cor de 0,6/255, com semente
   fixa por quadro.

Uso: foto.py entrada.png saida.png [semente] [aceso_cru.png apagado_cru.png]

Com o par cru (aceso e apagado do render), o quadro aceso ganha também o vazamento de luz do anel:
o vidro de 3 mm conduz parte da luz do jateado para dentro, e nas stills reais (Mobile Lux e
Classique Lux ligadas) o espelho fica claro junto ao anel, num degradê que some em ~1 cm. Sem isso
a borda entre o anel e o espelho fica num corte seco, que é marca de render. A fonte é a própria luz
do LED (aceso − apagado), então o vazamento tem a cor do tom (3000K, 4500K ou 6000K).
"""
import sys
import numpy as np
from PIL import Image, ImageFilter


def lin(c):
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def srgb(l):
    l = np.clip(l, 0, 1)
    return np.where(l <= 0.0031308, l * 12.92, 1.055 * l ** (1 / 2.4) - 0.055)


def caixa(a, r, eixo):
    """Média móvel de largura 2r+1 ao longo do eixo, bordas repetidas."""
    pad = [(0, 0)] * a.ndim; pad[eixo] = (r + 1, r)
    c = np.cumsum(np.pad(a, pad, mode='edge'), axis=eixo, dtype=np.float64)
    n = a.shape[eixo]
    sl1 = [slice(None)] * a.ndim; sl0 = [slice(None)] * a.ndim
    sl1[eixo] = slice(2 * r + 1, 2 * r + 1 + n); sl0[eixo] = slice(0, n)
    return ((c[tuple(sl1)] - c[tuple(sl0)]) / (2 * r + 1)).astype(np.float32)


def gauss(a, sigma):
    """Gaussiana aproximada por três médias móveis em cada eixo."""
    r = max(1, int(round(np.sqrt(12 * sigma * sigma / 3 + 1) / 2)))
    for _ in range(3):
        a = caixa(caixa(a, r, 0), r, 1)
    return a


def escala_canal(c, s):
    h, w = c.shape
    im = Image.fromarray(c.astype(np.float32), 'F')
    cx, cy = w / 2, h / 2
    # transformação afim inversa: ponto de saída (x, y) lê a entrada em cx + (x - cx)/s
    return np.asarray(im.transform((w, h), Image.AFFINE, (1 / s, 0, cx - cx / s, 0, 1 / s, cy - cy / s),
                                   resample=Image.BICUBIC))


def foto(im, semente=0, aceso=None, apagado=None):
    a = np.asarray(im.convert('RGB')).astype(np.float32) / 255
    L = lin(a).astype(np.float32)
    h, w = L.shape[:2]
    if aceso is not None:
        A = lin(np.asarray(aceso.convert('RGB')).astype(np.float32) / 255)
        B = lin(np.asarray(apagado.convert('RGB')).astype(np.float32) / 255)
        E = np.clip(A - B, 0, None) @ np.array([0.2126, 0.7152, 0.0722], np.float32)
        anel = np.clip((E - 0.05) / 0.15, 0, 1)[..., None]          # onde o LED domina o pixel
        luz = L * anel                                               # a luz do anel, já no tom
        vaza = 0.55 * gauss(luz, 10) + 0.45 * gauss(luz, 28)
        L = L + 0.5 * vaza * (1 - anel)
    # 1. bloom
    claro = np.clip(L - 0.75, 0, None)
    veu = 0.5 * gauss(claro, 4) + 0.35 * gauss(claro, 18) + 0.15 * gauss(claro, 60)
    # O véu só cai em volta da fonte: dentro do anel aceso o tom do padrão de 22/10 fica como está
    # (somar ali levava o difusor ao branco puro e apagava o 3000K e o 6000K).
    fonte = np.clip((L.max(-1, keepdims=True) - 0.6) / 0.2, 0, 1)
    L = L + 0.45 * veu * (1 - fonte)
    # 2. vinheta
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    r2 = ((xx - w / 2) ** 2 + (yy - h / 2) ** 2) / ((w / 2) ** 2 + (h / 2) ** 2)
    L = L * (1 - 0.09 * r2 ** 1.1)[..., None]
    s = srgb(L).astype(np.float32)
    # 3. aberração cromática lateral
    s[..., 0] = escala_canal(s[..., 0], 1.0005); s[..., 2] = escala_canal(s[..., 2], 0.9995)
    # 4. nitidez
    im8 = Image.fromarray((np.clip(s, 0, 1) * 255 + 0.5).astype(np.uint8))
    im8 = im8.filter(ImageFilter.UnsharpMask(radius=1.2, percent=35, threshold=2))
    s = np.asarray(im8).astype(np.float32) / 255
    # 5. grão
    rng = np.random.default_rng(semente)
    y = s @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    lum = rng.normal(0, 1, (h, w, 1)).astype(np.float32); cor = rng.normal(0, 1, (h, w, 3)).astype(np.float32)
    lum = 0.55 * lum + 0.45 * caixa(caixa(lum, 1, 0), 1, 1)   # grão de ~1,5 px, sem "sal" de pixel isolado
    cor = 0.55 * cor + 0.45 * caixa(caixa(cor, 1, 0), 1, 1)
    ruido = lum / lum.std() * (1.8 / 255) + cor / cor.std() * (0.6 / 255)
    s = s + ruido * (1 - 0.7 * y[..., None] ** 2)
    return Image.fromarray((np.clip(s, 0, 1) * 255 + 0.5).astype(np.uint8))


if __name__ == '__main__':
    sem = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    par = (Image.open(sys.argv[4]), Image.open(sys.argv[5])) if len(sys.argv) > 5 else (None, None)
    foto(Image.open(sys.argv[1]), sem, *par).save(sys.argv[2])
    print(sys.argv[2])
