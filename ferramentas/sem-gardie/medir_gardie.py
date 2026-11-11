"""Mede se ainda há o "gardie" impresso no vidro de um espelho sem luz (critério g2).
Na caixa do logo (caixas.json), o contraste do traço escuro = percentil 99,5 de (fechamento em cinza por canal − imagem),
com o elemento do tamanho de ~45% da altura da caixa. Calibragem de 10/11/2026 (Flex e Mobile): nas stills, com o logo
104 a 193 e limpas 0 a 22; VETO acima de 50. Nas ambientadas por IA o logo é fraco (8 a 56, limpas 1 a 7): lá a
medida só aponta, e quem decide é o zoom de 4x.
Uso: python3 -I medir_gardie.py <pasta> <caixas.json>   (arquivo = <chave>.png/.jpg)"""
import sys, json, glob, os
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
pasta, C = sys.argv[1], json.load(open(sys.argv[2]))
for fid, cfg in C.items():
    p = [x for x in glob.glob(os.path.join(pasta, fid + '.*')) if not x.endswith('.json')]
    if not p: continue
    x0, y0, x1, y1 = cfg['caixa'] if isinstance(cfg, dict) else cfg
    R = np.asarray(Image.open(p[0]).convert('RGB')).astype(np.float32)
    h = y1 - y0; pad = h; s = max(5, int(round(h * 0.45)) | 1)
    sub = R[max(0, y0 - pad):y1 + pad, max(0, x0 - pad):x1 + pad]
    fundo = np.stack([ndi.grey_closing(sub[..., c], (s, s)) for c in range(3)], -1)
    esc = (fundo - sub).max(-1)
    box = esc[y0 - max(0, y0 - pad):y1 - max(0, y0 - pad), x0 - max(0, x0 - pad):x1 - max(0, x0 - pad)]
    v = float(np.percentile(box, 99.5))
    print('%-40s %6.1f  %s' % (fid, v, 'VETO' if v > 50 else 'ok'))
