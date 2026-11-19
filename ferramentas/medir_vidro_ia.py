# medir_vidro_ia.py <img> <cx> <cy> <r0> [mais imagens no mesmo quadro...]
# Vidro de uma still refeita por IA (vista de frente): a IA às vezes inventa no vidro um arco ou uma
# mancha grande de reflexo, que lê como cúpula (critério r, `guia/criterios.md`).
# Mede a faixa de luminância do vidro: L* suavizado (gaussiana de 4% do raio do vidro), p98 − p2,
# no disco r < 0,85·r0 do centro do vidro, sem a caixa do logo a laser embaixo
# (y > cy + 0,45·r0 e |x − cx| < 0,45·r0). r0 = raio do vidro até o anel de LED, em px da imagem.
# Lumière 22005, recortada do site de 2510 px: cx 1091,6, cy 1011,0, r0 652.
import sys, numpy as np
from PIL import Image
from scipy import ndimage as nd

def lstar(rgb):
    c = rgb / 255.0
    c = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    y = 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]
    return np.where(y > 0.008856, 116 * np.cbrt(y) - 16, 903.3 * y)

def faixa(caminho, cx, cy, r0):
    L = lstar(np.asarray(Image.open(caminho).convert('RGB')).astype(float))
    yy, xx = np.mgrid[:L.shape[0], :L.shape[1]]
    r = np.hypot(xx - cx, yy - cy)
    m = (r < 0.85 * r0) & ~((yy > cy + 0.45 * r0) & (np.abs(xx - cx) < 0.45 * r0))
    v = nd.gaussian_filter(L, 0.04 * r0)[m]
    return np.percentile(v, 98) - np.percentile(v, 2), np.median(v)

if __name__ == '__main__':
    args = sys.argv[1:]
    nums = [a for a in args if a.replace('.', '', 1).lstrip('-').isdigit()]
    cx, cy, r0 = map(float, nums[:3])
    for p in [a for a in args if a not in nums[:3]]:
        f, med = faixa(p, cx, cy, r0)
        print('%-60s faixa %.1f  mediana %.1f  %s' % (p.split('/')[-1], f, med, 'VETO r' if f > 14 else 'ok'))
