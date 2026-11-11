"""Mede a mancha escura de reflexo no vidro de uma still de catálogo: uso
python3 medir_mancha_vidro.py <png> <cx,cy,a,b,ang> [fração=0.92]

A elipse do vidro (centro, semieixos e ângulo em graus, nas coordenadas do
PNG) é a da borda de fora do vidro. Mede só dentro dela, encolhida pela
fração (0,92 deixa de fora a borda do vidro, que é escura de verdade), nos
pixels opacos. Dá a parte desses pixels com luminância sRGB abaixo de 40, 60
e 80.

Critério (guia/criterios.md, item p), só para a still sem ambiente: no
máximo 1% abaixo de 60. Em 30/10/2026, o Svelte 10479 vetado pelo Thiago
("o Svelte com a mancha preta no espelho precisa ser barrado") deu 23%; as
outras 7 stills sem LED (Flex, Flex Cristal, Mobile, Royale Cristal,
Classique, Platine e Jolie), de 0 a 0,1%; o Svelte com o reflexo trocado, 0.
Nos modelos com cabeça de cristal (Flex Cristal, Royale Cristal), passe a
elipse da cabeça com fração 0.6, que cai dentro do vidro.
"""
import sys
import numpy as np
from PIL import Image

png, elipse = sys.argv[1:3]
frac = float(sys.argv[3]) if len(sys.argv) > 3 else 0.92
cx, cy, a, b, ang = (float(v) for v in elipse.split(','))
im = np.asarray(Image.open(png).convert('RGBA')).astype(np.float32) / 255
H, W = im.shape[:2]
yy, xx = np.mgrid[0:H, 0:W]
t = np.radians(ang)
u = (xx - cx) * np.cos(t) + (yy - cy) * np.sin(t)
v = -(xx - cx) * np.sin(t) + (yy - cy) * np.cos(t)
m = ((u / (a * frac)) ** 2 + (v / (b * frac)) ** 2 <= 1) & (im[..., 3] > 0.99)
Y = (0.2126 * im[..., 0] + 0.7152 * im[..., 1] + 0.0722 * im[..., 2])[m] * 255
abaixo = {lim: 100 * (Y < lim).mean() for lim in (40, 60, 80)}
print('%s: abaixo de 40 = %.1f%%, de 60 = %.1f%%, de 80 = %.1f%% | p5 = %.0f | %d px do vidro' % (
    png, abaixo[40], abaixo[60], abaixo[80], np.percentile(Y, 5), m.sum()))
print('mancha no vidro: %s (limite 1%% abaixo de 60)' % ('VETO' if abaixo[60] > 1 else 'ok'))
