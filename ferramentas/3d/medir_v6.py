# -*- coding: utf-8 -*-
"""Medidas do lote v6 (25/10, braço meio aberto, cromado 4500K), por vista:
- estouro no produto com o LED apagado (quadro cru; três canais >= 250 dentro da silhueta);
- estouro no produto no 4500K final fora da área que o LED ilumina (E = aceso − apagado > 0,02);
- folga do produto até a borda do quadro (px), para não cortar placa nem cabeça;
- pose: cotovelo e centro da cabeça (mm, x saindo da parede), lidos do registro do render.

Uso: medir_v6.py renders/v6 saida.json
"""
import sys, json
from pathlib import Path
import numpy as np
from PIL import Image


def lin(c):
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def rgb(p):
    return np.asarray(Image.open(p).convert('RGB')).astype(int)


base = Path(sys.argv[1]); res = {}
for d in sorted(p for p in base.iterdir() if p.is_dir() and (p / 'final' / 'lumiere-cromado-4500.png').exists()):
    m = np.asarray(Image.open(d / 'silhueta.png').convert('L')) > 128
    A, B, C = rgb(d / 'lumiere-cromado-aceso.png'), rgb(d / 'lumiere-cromado-apagado.png'), rgb(d / 'final' / 'lumiere-cromado-4500.png')
    Ey = np.clip(lin(A / 255) - lin(B / 255), 0, None) @ np.array([0.2126, 0.7152, 0.0722])
    fora = m & (Ey < 0.02)
    ys, xs = np.nonzero(m); h, w = m.shape
    info = json.load(open(d / 'lumiere-cromado-aceso.json'))
    r = {'estouro_apagado_pct': round(100 * ((B.min(2) >= 250) & m).sum() / m.sum(), 2),
         'estouro_4500_fora_led_pct': round(100 * ((C.min(2) >= 250) & fora).sum() / fora.sum(), 2),
         'area_led_pct': round(100 * (m & (Ey >= 0.02)).sum() / m.sum(), 1),
         'folga_borda_px': int(min(xs.min(), ys.min(), w - 1 - xs.max(), h - 1 - ys.max())),
         'camera': {k: info['camera'][k] for k in ('azimute', 'elevacao')}, 'pose': info['materiais'].get('pose')}
    res[d.name] = r
    print(d.name, json.dumps(r, ensure_ascii=False))
json.dump(res, open(sys.argv[2], 'w'), ensure_ascii=False, indent=1)
