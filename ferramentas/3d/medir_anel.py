# -*- coding: utf-8 -*-
"""Mede o anel de luz numa vista --orto de frente (0,25 mm/px): B/R mediano dos pixels não
saturados (canal máx. 60–244) em 4 amostras (12, 3, 6 e 9 h), dividido pelo B/R da parede
(guia/criterios.md, passo 6). Também a fração de pixels estourados no anel.
Uso: python medir_anel.py render.png [cx cy] [mm_por_px]"""
import sys, json
import numpy as np
from PIL import Image
a = np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(float)
h, w, _ = a.shape
cx = float(sys.argv[2]) if len(sys.argv) > 2 else 503.8
cy = float(sys.argv[3]) if len(sys.argv) > 3 else 468.4
s = float(sys.argv[4]) if len(sys.argv) > 4 else 0.25
yy, xx = np.mgrid[0:h, 0:w]
r = np.hypot(xx - cx, yy - cy) * s
ang = (np.degrees(np.arctan2(xx - cx, -(yy - cy))) + 360) % 360   # 0 = 12 h, 90 = 3 h
anel = (r > 80.5) & (r < 88.5)
out = {}
for nome, a0 in (('12h', 0), ('3h', 90), ('6h', 180), ('9h', 270)):
    d = np.minimum(np.abs(ang - a0), 360 - np.abs(ang - a0))
    sel = anel & (d < 12)
    px = a[sel]; mx = px.max(1)
    ok = (mx >= 60) & (mx <= 244)
    out[nome] = dict(br=round(float(np.median(px[ok, 2] / np.maximum(px[ok, 0], 1))), 3) if ok.sum() else None,
                     estourado=round(float((mx > 250).mean()), 3), media=[int(v) for v in px.mean(0)])
par = a[:60, :60].reshape(-1, 3)
br_par = float(np.median(par[:, 2] / np.maximum(par[:, 0], 1)))
brs = [v['br'] for v in out.values() if v['br']]
out['parede_br'] = round(br_par, 3)
out['anel_br_norm'] = round(float(np.median(brs)) / br_par, 3) if brs else None
print(json.dumps(out))
