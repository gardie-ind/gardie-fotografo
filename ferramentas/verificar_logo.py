"""Confere um modelo do lote_logo.py: o que mudou fora da luz do LED e dos dois
logos (o impresso, apagado, e o gravado, novo)?

Para cada acabamento mede, contra as fotos de origem:
- apagada nova: pixels com diferença > 3 níveis fora das caixas dos logos;
- ligadas: pixels com diferença > 3 níveis fora da luz do LED (E > 0, dilatada)
  e das caixas dos logos.
Também confere se o logo impresso sumiu: desvio do anel (L2 − L1) dentro da
caixa dele, antes e depois.

uso: [CROMO_DIR=pasta] [ACAB_DIR=pasta] python3 verificar_logo.py <pasta do modelo> <modelo> <código>
(as mesmas fontes do lote_logo.py)"""
import sys, os, glob, json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from luz_anel import lin

APROVADAS = os.environ.get('CROMO_DIR', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'aprovadas'))
ACAB = os.environ.get('ACAB_DIR', '/mnt/project-files/fotografo/2026-10-21-acabamentos')
P, modelo, codigo = sys.argv[1:4]
med = json.load(open(f'{P}/logo-medidas.json'))


def rgba(p):
    a = np.asarray(Image.open(p).convert('RGBA')).astype(np.int16)
    return a[..., :3], a[..., 3]


res = {}
for acab, m in med.items():
    if acab == 'cromado':
        fs = sorted(glob.glob(f'{APROVADAS}/{codigo}CR/*.jpg')); lig, apa = fs[-2], fs[-1]; ext = 'jpg'
    else:
        lig, apa = (f'{ACAB}/{modelo}/{modelo}-{acab}-{e}.png' for e in ('ligado', 'desligado')); ext = 'png'
    R1, A1 = rgba(lig); R2, A2 = rgba(apa)
    L1 = lin(R1 / 255.0); L2 = lin(R2 / 255.0)
    E = (np.clip(L1 - L2 - 0.004, 0, None).max(-1) > 0)
    E = ndi.binary_dilation(E, iterations=4)
    # caixas dos logos
    neg = (L2 - L1).max(-1) > 0.03
    lb, _ = ndi.label(ndi.binary_dilation(neg, iterations=6)); cnt = np.bincount(lb.ravel()); cnt[0] = 0
    imp = neg & (lb == np.argmax(cnt))
    ys, xs = np.where(imp)
    caixa = np.zeros(imp.shape, bool)
    caixa[max(ys.min() - 30, 0):ys.max() + 31, max(xs.min() - 30, 0):xs.max() + 31] = True
    cx, cy = m['logo_novo_centro']; r = int(m['logo_novo_largura_px'] * 0.75) + 10
    caixa[max(int(cy) - r, 0):int(cy) + r, max(int(cx) - r, 0):int(cx) + r] = True
    linha = {}
    N2, B2 = rgba(f'{P}/{modelo}-{acab}-desligado.{ext}')
    d = np.abs(N2 - R2).max(-1) > 3
    linha['apagada_fora'] = int((d & ~caixa).sum())
    linha['alfa_igual'] = bool((np.abs(B2 - A2) <= 0).all())
    for tom in ('3000', '4500', '6000'):
        N1, B1 = rgba(f'{P}/{modelo}-{acab}-ligado-{tom}k.{ext}')
        d = np.abs(N1 - R1).max(-1) > 3
        linha[f'{tom}k_fora'] = int((d & ~caixa & ~E).sum())
    # o impresso sumiu? energia de borda do (L2-L1) dentro da caixa do impresso, antes/depois
    bx = (slice(max(ys.min() - 4, 0), ys.max() + 5), slice(max(xs.min() - 4, 0), xs.max() + 5))
    Y = lambda L: L[bx].mean(-1)
    N2l = lin(N2 / 255.0)
    for nome, L in (('antes', L2), ('depois', N2l)):
        y = Y(L); hp = y - ndi.gaussian_filter(y, 3)
        linha[f'impresso_{nome}'] = round(float(np.percentile(np.abs(hp), 99.5)) * 1000, 2)
    res[acab] = linha
    print(acab, linha, flush=True)
json.dump(res, open(f'{P}/verificacao.json', 'w'), indent=1)
