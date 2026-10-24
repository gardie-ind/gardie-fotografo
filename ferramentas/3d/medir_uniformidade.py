# -*- coding: utf-8 -*-
"""Uniformidade do anel aceso: luz do LED E = aceso − apagado (luz linear, mesmo quadro), lida
ao longo do anel em vários raios. Reporta a variação (p95 − p5) / mediana de Y(E) por raio, fora
dos setores do logo e do braço, e o perfil radial (mediana por raio).

Uso: medir_uniformidade.py aceso.png apagado.png cx cy px_por_mm r_in r_out [setores_excluidos]
setores: lista "a0-a1,a2-a3" em graus (0 = 12 h, sentido horário)."""
import sys, json, math
import numpy as np
from PIL import Image


def lin(c):
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


A = lin(np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(float) / 255)
B = lin(np.asarray(Image.open(sys.argv[2]).convert('RGB')).astype(float) / 255)
cx, cy, k, r0, r1 = map(float, sys.argv[3:8])
fora = [tuple(map(float, s.split('-'))) for s in sys.argv[8].split(',')] if len(sys.argv) > 8 else []
Y = np.clip(A - B, 0, None) @ np.array([0.2126, 0.7152, 0.0722])
ang = np.arange(0, 360, 0.5)
ok = np.array([not any(a0 <= a <= a1 for a0, a1 in fora) for a in ang])
out = {'raios': []}
for rr in np.linspace(r0, r1, 7):
    v = np.array([Y[int(round(cy - rr * k * math.cos(math.radians(a)))), int(round(cx + rr * k * math.sin(math.radians(a))))] for a in ang])[ok]
    med = float(np.median(v))
    out['raios'].append({'r_mm': round(float(rr), 1), 'Y_mediana': round(med, 4),
                         'variacao_pct': round(100 * float(np.percentile(v, 95) - np.percentile(v, 5)) / max(med, 1e-6), 1)})
meds = [r['Y_mediana'] for r in out['raios']]
out['variacao_max_pct'] = max(r['variacao_pct'] for r in out['raios'])
out['radial_min_max'] = round(min(meds) / max(meds), 3)
print(json.dumps(out, ensure_ascii=False))
