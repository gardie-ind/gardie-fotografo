"""Tira o "gardie" impresso do vidro das fotos do Flex (10578) e do Mobile (10431), sem IA.

Pedido do Thiago (09/11/2026): "Consegue remover o gardie que está gravado nos
espelhos sem luz? [...] Nós também não fazemos mais essa gravação de marca nos
espelhos." Só os espelhos sem luz: o logo a laser dos LUX fica.

Para cada foto, dentro da caixa do logo (caixas.json, medida à mão em cada uma):
1. traços = onde a foto fica mais escura que o fundo (fechamento morfológico de
   cada canal, que apaga traços finos), acima de um limiar relativo ao traço
   mais forte; a máscara é alargada para levar a borda suavizada do traço;
2. o buraco é preenchido pela superfície mais lisa presa aos pixels em volta
   (equação de Laplace, por canal), que no vidro é um degradê;
3. o grão volta copiado de um trecho de vidro limpo logo acima (passa-alta de
   sigma 1,5), o que mantém o pontilhado das stills do Mobile.
Fora da máscara nenhum pixel muda. Dentro dela o alfa também é preenchido:
nas stills recortadas em gold e red gold o removedor de fundo tinha deixado o
logo um pouco transparente (alfa 242), e o vidro em volta é opaco.

uso: python3 -I tirar_gardie.py <pasta orig> <pasta saida> [caixas.json] [fid,fid,...]"""
import json, os, sys, glob
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from scipy.sparse import lil_matrix, csr_matrix
from scipy.sparse.linalg import spsolve


def laplace(F, msk, wx=1.0):
    """Preenche F[msk] resolvendo Laplace com os pixels de fora como borda (Dirichlet).
    wx < 1 faz o preenchimento seguir a vertical (reflexo com faixas verticais)."""
    ys, xs = np.nonzero(msk); n = len(ys)
    idx = -np.ones(msk.shape, int); idx[ys, xs] = np.arange(n)
    A = lil_matrix((n, n)); b = np.zeros((n, F.shape[2]))
    H, W = msk.shape
    for k, (y, x) in enumerate(zip(ys, xs)):
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            w = 1.0 if dx == 0 else wx
            yy, xx = y + dy, x + dx
            if not (0 <= yy < H and 0 <= xx < W):
                continue
            A[k, k] += w
            if msk[yy, xx]: A[k, idx[yy, xx]] = -w
            else: b[k] += w * F[yy, xx]
    A = csr_matrix(A); out = F.copy()
    for c in range(F.shape[2]):
        out[ys, xs, c] = spsolve(A, b[:, c])
    return out


def mascara(R, cx, aro=True):
    x0, y0, x1, y1 = cx
    h = y1 - y0; pad = h
    Y0, X0 = max(0, y0 - pad), max(0, x0 - pad)
    sub = R[Y0:y1 + pad, X0:x1 + pad].astype(np.float32)
    s = max(5, int(round(h * 0.45)) | 1)          # maior que a largura do traço
    fundo = np.stack([ndi.grey_closing(sub[..., c], size=(s, s)) for c in range(3)], -1)
    esc = (fundo - sub).max(-1)
    box = np.zeros(esc.shape, bool); box[y0 - Y0:y1 - Y0, x0 - X0:x1 - X0] = True
    pico = np.percentile(esc[box], 99.5)
    m = (esc > max(2.0, 0.12 * pico)) & box
    lab, nl = ndi.label(m); tam = ndi.sum(m, lab, range(1, nl + 1))
    m = np.isin(lab, 1 + np.nonzero(tam >= max(3, h * 0.15))[0])
    # a palavra inteira vira um bloco (miolo das letras e franja do traço entram)
    rr = max(2, int(round(h * 0.35)))
    yy, xx = np.mgrid[-rr:rr + 1, -rr:rr + 1]; disco = yy ** 2 + xx ** 2 <= rr ** 2
    m = m | ndi.binary_closing(np.pad(m, rr), structure=disco)[rr:-rr, rr:-rr]
    r = max(2, int(round(h * 0.18)))
    m = ndi.binary_dilation(m, iterations=r) & box
    # o aro não entra: fundo bem mais escuro que o vidro da caixa é aro, não vidro
    if aro:
        lum = fundo.mean(-1); vidro = np.median(lum[box])
        m &= ~ndi.binary_dilation(lum < vidro - 25, iterations=2)
    M = np.zeros(R.shape[:2], bool); M[Y0:y1 + pad, X0:x1 + pad] = m
    return M, pico


def grao(F, M, cx):
    """Passa-alta de um trecho limpo logo acima da caixa, colado na máscara."""
    x0, y0, x1, y1 = cx; h = y1 - y0
    hp = F - np.stack([ndi.gaussian_filter(F[..., c], 1.5) for c in range(3)], -1)
    for d in (h + 4, 2 * h + 4, 3 * h + 4):
        ok = M.copy(); ok[:] = False
        ys, xs = np.nonzero(M)
        if (ys - d < 0).any(): continue
        if not M[ys - d, xs].any():
            return hp[ys - d, xs]
    return np.zeros((M.sum(), 3))


def tirar(path, cfg):
    cx = cfg['caixa'] if isinstance(cfg, dict) else cfg
    aro = cfg.get('aro', True) if isinstance(cfg, dict) else True
    wx = 0.02 if isinstance(cfg, dict) and cfg.get('vertical') else 1.0
    im = Image.open(path); modo = im.mode
    a = np.asarray(im.convert('RGBA')).copy()
    R = a[..., :3]
    M, pico = mascara(R, cx, aro)
    if isinstance(cfg, dict) and cfg.get('inteira'):   # a caixa toda (traço quase sem contraste sobre o reflexo)
        x0, y0, x1, y1 = cx; M = np.zeros_like(M); M[y0:y1, x0:x1] = True
    F = a.astype(np.float64)          # RGBA: o alfa do logo (recortado pelo removedor de fundo) volta ao do vidro
    out = laplace(F, M, wx)
    ys, xs = np.nonzero(M)
    out[ys, xs, :3] += grao(F[..., :3], M, cx)
    novo = np.clip(np.round(out), 0, 255).astype(np.uint8)
    return novo, modo, M, pico


if __name__ == '__main__':
    orig, saida = sys.argv[1], sys.argv[2]
    C = json.load(open(sys.argv[3] if len(sys.argv) > 3 else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'caixas.json')))
    os.makedirs(saida, exist_ok=True); rel = {}
    so = sys.argv[4].split(',') if len(sys.argv) > 4 else None
    for fid, cx in C.items():
        if so and fid not in so: continue
        p = glob.glob(os.path.join(orig, fid + '.*'))[0]
        novo, modo, M, pico = tirar(p, cx)
        im0 = Image.open(p)
        if modo in ('RGBA', 'LA', 'P') and np.asarray(im0.convert('RGBA'))[..., 3].min() < 255:
            Image.fromarray(novo, 'RGBA').save(os.path.join(saida, fid + '.png'), optimize=True)
        else:
            Image.fromarray(novo[..., :3], 'RGB').save(os.path.join(saida, fid + '.png'), optimize=True)
        a0 = np.asarray(im0.convert('RGBA'))
        mud = (a0 != novo).any(-1)
        rel[fid] = {'px_mascara': int(M.sum()), 'contraste_logo': round(float(pico), 1),
                    'px_mudados_fora_da_mascara': int((mud & ~M).sum()),
                    'alfa_igual_fora_da_mascara': bool((a0[..., 3] == novo[..., 3])[~M].all()),
                    'alfa_min_na_mascara_antes_depois': [int(a0[..., 3][M].min()), int(novo[..., 3][M].min())]}
        print(fid, rel[fid])
    rp = os.path.join(saida, 'relatorio.json')
    velho = json.load(open(rp)) if os.path.exists(rp) else {}
    velho.update(rel); json.dump(velho, open(rp, 'w'), indent=1)
