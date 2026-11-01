"""Separação entre os tons do anel nas stills LUX (critério c, guia/criterios.md).

Pedido do Thiago (01/11/2026, 12:13): "Aqui no site, na prática, o 4500K e o
6000K parecem a mesma coisa." Medido: nas stills publicadas, o anel do 4500K
(render 5150K) ficava a ΔE2000 4,8 a 6,7 do 6000K. Desde 01/11 (13:08 e
13:09), os tons de divulgação são 3000K = render 3800K, 4500K = render 4500K e
6000K = render 6000K (`luz_padrao.py`).

Para cada código, a região do LED é onde a ligada em 4500K soma luz sobre a
apagada (luz linear, ΔY > 0,03, alfa cheio). Nela:
- anel: os pixels que, na ligada em 4500K, passam de 0,94 no canal máximo;
- halo: os que ficam entre 0,25 e 0,85 (o halo no vidro e os reflexos).
Em cada uma, a mediana sRGB de cada tom e o ΔE2000 entre tons vizinhos
(3000K × 4500K e 4500K × 6000K). Reprova (VETO c) se o ΔE do anel entre
vizinhos ficar abaixo de LIMITE.

uso: python3 medir_tons.py [csv] [código ...]
     csv padrão: ferramentas/fotos-lux-centradas-2026-11-01.csv
     (posições 1 = 4500K, 2 = apagada, 3 = 3000K, 4 = 6000K)"""
import csv
import json
import os
import sys

import numpy as np
from PIL import Image

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CSV = os.path.join(RAIZ, 'ferramentas', 'fotos-lux-centradas-2026-11-01.csv')
LIMITE = 7.5          # placar.md › Calibragem, 2026-11-01: vetado 4,8 a 6,7; aprovado 8,2 a 11,1
YW = np.array([0.2126, 0.7152, 0.0722])
F = 4                 # mede em 1/4 da resolução (média por caixa)


def lin(c):
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def lab(rgb):
    """sRGB (0 a 1) → CIELAB, branco D65."""
    M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    xyz = lin(np.asarray(rgb, float)) @ M.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > (6 / 29) ** 3, np.cbrt(xyz), xyz / (3 * (6 / 29) ** 2) + 4 / 29)
    return np.array([116 * f[1] - 16, 500 * (f[0] - f[1]), 200 * (f[1] - f[2])])


def de2000(l1, l2):
    """CIEDE2000 entre duas cores Lab (Sharma, Wu e Dalal, 2005)."""
    L1, a1, b1 = l1; L2, a2, b2 = l2
    C1, C2 = np.hypot(a1, b1), np.hypot(a2, b2); Cm = (C1 + C2) / 2
    G = 0.5 * (1 - np.sqrt(Cm ** 7 / (Cm ** 7 + 25 ** 7)))
    a1p, a2p = (1 + G) * a1, (1 + G) * a2
    C1p, C2p = np.hypot(a1p, b1), np.hypot(a2p, b2)
    h1p, h2p = np.degrees(np.arctan2(b1, a1p)) % 360, np.degrees(np.arctan2(b2, a2p)) % 360
    dL, dC = L2 - L1, C2p - C1p
    dh = 0 if C1p * C2p == 0 else (h2p - h1p + 180) % 360 - 180
    dH = 2 * np.sqrt(C1p * C2p) * np.sin(np.radians(dh / 2))
    Lm, Cpm = (L1 + L2) / 2, (C1p + C2p) / 2
    if C1p * C2p == 0: hm = h1p + h2p
    elif abs(h1p - h2p) <= 180: hm = (h1p + h2p) / 2
    else: hm = (h1p + h2p + 360) / 2 if h1p + h2p < 360 else (h1p + h2p - 360) / 2
    T = 1 - 0.17 * np.cos(np.radians(hm - 30)) + 0.24 * np.cos(np.radians(2 * hm)) \
        + 0.32 * np.cos(np.radians(3 * hm + 6)) - 0.20 * np.cos(np.radians(4 * hm - 63))
    SL = 1 + 0.015 * (Lm - 50) ** 2 / np.sqrt(20 + (Lm - 50) ** 2)
    SC, SH = 1 + 0.045 * Cpm, 1 + 0.015 * Cpm * T
    RT = -2 * np.sqrt(Cpm ** 7 / (Cpm ** 7 + 25 ** 7)) * np.sin(np.radians(60 * np.exp(-((hm - 275) / 25) ** 2)))
    return float(np.sqrt((dL / SL) ** 2 + (dC / SC) ** 2 + (dH / SH) ** 2 + RT * (dC / SC) * (dH / SH)))


def ler(p):
    im = Image.open(p).convert('RGBA')
    im = im.resize((im.width // F, im.height // F), Image.BOX)
    a = np.asarray(im).astype(np.float32) / 255
    return a[..., :3], a[..., 3]


def medir(f45, fapa, f30, f60):
    L45, A = ler(f45); L2, _ = ler(fapa)
    tons = {'3000': ler(f30)[0], '4500': L45, '6000': ler(f60)[0]}
    E = (lin(L45) - lin(L2)) @ YW
    led = (A > 0.98) & (E > 0.03)
    regioes = {'anel': led & (L45.max(-1) > 0.94), 'halo': led & (L45.max(-1) < 0.85) & (L45.max(-1) > 0.25)}
    out = {}
    for nome, m in regioes.items():
        med = {t: np.median(v[m], 0) for t, v in tons.items()}
        L = {t: lab(c) for t, c in med.items()}
        out[nome] = {'rgb': {t: [int(round(x * 255)) for x in c] for t, c in med.items()},
                     'dE_3000_4500': round(de2000(L['3000'], L['4500']), 1),
                     'dE_4500_6000': round(de2000(L['4500'], L['6000']), 1), 'px': int(m.sum())}
    a = out['anel']
    out['veto_c'] = min(a['dE_3000_4500'], a['dE_4500_6000']) < LIMITE
    return out


if __name__ == '__main__':
    args = sys.argv[1:]
    csvp = args.pop(0) if args and args[0].endswith('.csv') else CSV
    pos = {}
    for r in csv.DictReader(open(csvp)):
        pos.setdefault(r['codigo'], {})[r['posicao']] = os.path.join(RAIZ, 'aprovadas', r['codigo'], r['arquivo'])
    res = {}
    for cod in (args or pos):
        p = pos[cod]
        res[cod] = medir(p['1'], p['2'], p['3'], p['4'])
        a, h = res[cod]['anel'], res[cod]['halo']
        print(f"{cod:11s} anel ΔE 3000×4500 {a['dE_3000_4500']:5.1f}  4500×6000 {a['dE_4500_6000']:5.1f} | "
              f"halo {h['dE_3000_4500']:5.1f} {h['dE_4500_6000']:5.1f} | anel sRGB {a['rgb']['3000']} {a['rgb']['4500']} {a['rgb']['6000']}"
              f"{'  VETO c' if res[cod]['veto_c'] else ''}", flush=True)
    print(json.dumps({'limite': LIMITE, 'vetos': [c for c, v in res.items() if v['veto_c']]}))
