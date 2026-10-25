# -*- coding: utf-8 -*-
"""Medidas do lote v4 (24/10), por vista e acabamento:
- estouro no produto com o LED apagado (luz do estúdio; três canais >= 250 dentro da silhueta);
- estouro no produto no tom 4500K fora da área que o LED ilumina (E = aceso − apagado > 0,02);
- de frente, uniformidade do anel aceso: (p95 − p5) / mediana da luminância ao longo do anel, em
  7 raios de 77 a 90 mm, fora do setor 160–200°, no quadro aceso e no tom 4500K. (A conta pela
  diferença aceso − apagado infla o número: o anel apagado reflete o estúdio e varia 90–200%
  em volta de um valor baixo, o que não aparece na foto acesa.)

Uso: medir_v4.py renders/v4 saida.json
     medir_v4.py renders/v5 saida.json final   (v5, 25/10: mede os quadros finais, depois do
     acabamento de câmera; o aceso e o apagado crus só servem para achar a área do LED)
"""
import sys, json, math
from pathlib import Path
import numpy as np
from PIL import Image

ACAB = ['cromado', 'brushed-nickel', 'gold', 'red-gold', 'black-matte']


def lin(c):
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def rgb(p):
    return np.asarray(Image.open(p).convert('RGB')).astype(int)


def uniformidade(img, cx=471.2, cy=577.7, k=3.0592):
    y = lin(img / 255) @ np.array([0.2126, 0.7152, 0.0722])
    ang = np.arange(0, 360, 0.5); ok = ~((ang >= 160) & (ang <= 200))
    var, meds = [], []
    for rr in np.linspace(77, 90, 7):
        v = np.array([y[int(round(cy - rr * k * math.cos(math.radians(a)))), int(round(cx + rr * k * math.sin(math.radians(a))))]
                      for a in ang])[ok]
        med = float(np.median(v)); meds.append(med)
        var.append(100 * float(np.percentile(v, 95) - np.percentile(v, 5)) / max(med, 1e-6))
    return round(max(var), 1), round(min(meds) / max(meds), 3)


base = Path(sys.argv[1]); res = {}
SUB = sys.argv[3] if len(sys.argv) > 3 else None
for vista in ('frente', 'tres-quartos', 'braco-aberto'):
    d = base / vista
    if not (d / 'silhueta.png').exists():
        continue
    m = np.asarray(Image.open(d / 'silhueta.png').convert('L')) > 128
    for a in ACAB:
        ac, ap, t45 = d / f'lumiere-{a}-aceso.png', d / f'lumiere-{a}-apagado.png', d / (SUB or 'tons') / f'lumiere-{a}-4500.png'
        if not (ac.exists() and ap.exists() and t45.exists()):
            continue
        A, B, C = rgb(ac), rgb(ap), rgb(t45)
        Bf = rgb(d / SUB / f'lumiere-{a}-apagado.png') if SUB else B
        Ey = np.clip(lin(A / 255) - lin(B / 255), 0, None) @ np.array([0.2126, 0.7152, 0.0722])
        fora_led = m & (Ey < 0.02)
        r = {'estouro_apagado_pct': round(100 * ((Bf.min(2) >= 250) & m).sum() / m.sum(), 2),
             'estouro_4500_fora_led_pct': round(100 * ((C.min(2) >= 250) & fora_led).sum() / fora_led.sum(), 2),
             'area_led_pct': round(100 * (m & (Ey >= 0.02)).sum() / m.sum(), 1)}
        if vista == 'frente':
            for nome, img in (('aceso', A), ('4500', C)):
                v, meds = uniformidade(img)
                r[f'anel_variacao_max_pct_{nome}'] = v; r[f'anel_radial_min_max_{nome}'] = meds
            # cor do difusor no tom 4500K: mediana dos pixels do anel (r 80–88 mm)
            yy, xx = np.mgrid[0:C.shape[0], 0:C.shape[1]]
            rr = np.hypot(xx - 471.2, yy - 577.7) / 3.0592
            ang = (np.degrees(np.arctan2(xx - 471.2, -(yy - 577.7))) + 360) % 360
            anel = (rr > 80) & (rr < 88) & ~((ang > 160) & (ang < 200))
            for t in ('3000', '4500', '6000'):
                T = rgb(d / (SUB or 'tons') / f'lumiere-{a}-{t}.png')
                r[f'difusor_{t}'] = [int(v) for v in np.median(T[anel], axis=0)]
        res[f'{vista}/{a}'] = r
        print(vista, a, json.dumps(r, ensure_ascii=False))
json.dump(res, open(sys.argv[2], 'w'), ensure_ascii=False, indent=1)
