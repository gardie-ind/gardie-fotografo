"""Fração de pixels estourados (os três canais >= 250) no produto, fora do anel de LED.

Uso: medir_estouro.py render.png silhueta.png [cx cy r_in r_out]
A silhueta é o mesmo quadro com --silhueta (produto branco sobre preto). O anel de LED (aceso,
legitimamente claro) sai da conta por uma elipse medida na própria silhueta, se passada.
"""
import sys, json
import numpy as np
from PIL import Image

a = np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(int)
m = np.asarray(Image.open(sys.argv[2]).convert('L')) > 128
est = (a.min(axis=2) >= 250) & m
quase = (a.min(axis=2) >= 240) & m
canal = (a.max(axis=2) >= 250) & m            # algum canal no teto (ouro estoura no R e no G)
print(json.dumps({'produto_px': int(m.sum()), 'estourado_pct': round(100 * est.sum() / m.sum(), 2),
                  'acima_240_pct': round(100 * quase.sum() / m.sum(), 2),
                  'canal_no_teto_pct': round(100 * canal.sum() / m.sum(), 2)}))
