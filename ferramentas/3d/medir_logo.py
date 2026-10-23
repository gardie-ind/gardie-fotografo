"""Mede o logo a laser no render ortográfico de frente e compara com o E-0001-V1.

Uso: medir_logo.py orto.png [cx cy] [mm_por_px] [prata_diam]
Padrão: centro do vidro (503,8; 468,4) e 0,25 mm/px, da vista --orto 1200x1200.
E-0001-V1: logo com 20 mm de largura e 2,98 de altura total, topo 8,71 mm acima da borda de
baixo da área espelhada (Ø158,75), centrado.
"""
import sys, json
import numpy as np
from PIL import Image

img = sys.argv[1]
cx, cy = (float(sys.argv[2]), float(sys.argv[3])) if len(sys.argv) > 3 else (503.8, 468.4)
mm = float(sys.argv[4]) if len(sys.argv) > 4 else 0.25
a = np.asarray(Image.open(img).convert('L')).astype(float)
# Com a prata menor (frente do protótipo, 23/10) o logo sobe na mesma proporção.
prata = float(sys.argv[5]) if len(sys.argv) > 5 else 158.75
topo_mm, alt_mm, larg_mm = (158.75 / 2 - 8.71) * prata / 158.75, 2.98, 20.0
# janela em volta do lugar previsto, com folga de 5 mm
y0, y1 = int(cy + (topo_mm - 4) / mm), int(cy + (topo_mm + alt_mm + 2.5) / mm)   # o anel sobe nos lados
x0, x1 = int(cx - (larg_mm / 2 + 4) / mm), int(cx + (larg_mm / 2 + 4) / mm)
J = a[y0:y1, x0:x1]
fundo = np.median(J)
marca = np.abs(J - fundo) > 10   # 18 perdia traços do logo aceso (23/10)
ys, xs = np.nonzero(marca)
bx0, bx1, by0, by1 = xs.min() + x0, xs.max() + x0 + 1, ys.min() + y0, ys.max() + y0 + 1
med = {
    'largura_mm': round((bx1 - bx0) * mm, 2), 'altura_mm': round((by1 - by0) * mm, 2),
    'topo_abaixo_do_centro_mm': round((by0 - cy) * mm, 2),
    'desvio_do_centro_horizontal_mm': round(((bx0 + bx1) / 2 - cx) * mm, 2),
    'desenho': {'largura_mm': larg_mm, 'altura_mm': alt_mm, 'topo_abaixo_do_centro_mm': round(topo_mm, 2)},
}
print(json.dumps(med, ensure_ascii=False))
