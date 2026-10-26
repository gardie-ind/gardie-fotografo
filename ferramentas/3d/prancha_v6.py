# -*- coding: utf-8 -*-
"""Prancha do lote v6 (25/10): dez perfis de braço meio aberto, cromado 4500K, em 2 × 5.
Cada quadro leva a vista, o braço e a câmera. Uso: prancha_v6.py renders/v6 saida.png
"""
import sys, json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W = 432; H = 540; M = 14; T = 70; R = 64
F = ImageFont.truetype('DejaVuSans.ttf', 19); FT = ImageFont.truetype('DejaVuSans-Bold.ttf', 30)


def rotulo(v, info):
    az, el = info['camera']['azimute'], info['camera']['elevacao']
    t1, t2 = info['materiais']['pose']['braco_graus']
    lado = 'esq.' if az > 0 else 'dir.'
    alt = '%g° acima' % el if el > 0 else ('%g° abaixo' % -el if el < 0 else 'na altura')
    return ['%s · braço %g°/%g°' % (v, t1, t2 % 360 or 360), 'câmera %g° à %s, %s' % (abs(az), lado, alt)]


base, saida = Path(sys.argv[1]), sys.argv[2]
vistas = sorted(p for p in base.iterdir() if p.is_dir() and (p / 'final' / 'lumiere-cromado-4500.png').exists())
cols = 5; lin = (len(vistas) + cols - 1) // cols
out = Image.new('RGB', (M + cols * (W + M), T + lin * (H + R + M)), 'white'); d = ImageDraw.Draw(out)
d.text((M, 16), 'Lumière 22005 · braço meio aberto · cromado, 4500K', font=FT, fill=(0, 0, 0))
for i, p in enumerate(vistas):
    x = M + (i % cols) * (W + M); y = T + (i // cols) * (H + R + M)
    out.paste(Image.open(p / 'final' / 'lumiere-cromado-4500.png').convert('RGB').resize((W, H), Image.LANCZOS), (x, y))
    for k, s in enumerate(rotulo(p.name, json.load(open(p / 'lumiere-cromado-aceso.json')))):
        d.text((x + 2, y + H + 6 + 26 * k), s, font=F, fill=(0, 0, 0) if k == 0 else (70, 70, 70))
out.save(saida)
print(saida, out.size)
