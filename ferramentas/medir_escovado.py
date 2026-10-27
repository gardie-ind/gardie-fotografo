"""Mede se o brushed nickel lê escovado: uso
python3 medir_escovado.py <png do acabamento> <w-met-k.npy> [rótulo]

No metal (peso > 0,95, a 6 px da borda, onde o sentido da peça é definido,
coerência > 0,5), pega o passa-alta fino da luminância (Y − gauss 3 px) e mede:
- anisotropia: rms da derivada através da peça ÷ rms da derivada ao longo
  dela. Só informativa: em 22/10/2026 não separou o nickel vetado do aprovado
  (2,4 a 4,0 nos dois), porque o reflexo do cromado já corre ao longo da peça;
- riscado: rms do passa-alta através da peça, em % da luminância local;
- borda do reflexo: largura (px) da transição das faixas de luz através da
  peça, mediana do sigma equivalente nos degraus fortes (o gold polido dá
  2,4 px).
Critério (guia/criterios.md, item b), na escala da still de catálogo:
riscado >= 1,2% e borda >= 3,8 px. Os pesos de metal (w-met-k.npy) saem da
recoloração do modelo (acabamento_modelo.py, na pasta de ferramentas dos
acabamentos em /mnt/project-files/fotografo/2026-10-21-acabamentos/).
"""
import sys, os
import numpy as np
import scipy.ndimage as ndi
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from escovado import direcao

png, wpath = sys.argv[1:3]
rot = sys.argv[3] if len(sys.argv) > 3 else os.path.basename(png)
R = np.asarray(Image.open(png))
w = np.load(wpath).astype(np.float32)
a = R[..., 3].astype(np.float32) / 255 if R.shape[-1] == 4 else np.ones(R.shape[:2], np.float32)
Ys = (R[..., :3].astype(np.float32) / 255) @ np.array([0.2126, 0.7152, 0.0722], np.float32)
peso = w * a
dx, dy, coh = direcao(Ys, peso)
mask = ndi.binary_erosion(peso > 0.95, iterations=6) & (coh > 0.5)
H = Ys - ndi.gaussian_filter(Ys, 3)
loc = ndi.gaussian_filter(Ys, 8)
iy, ix = np.nonzero(mask)
rng = np.random.default_rng(1)
sel = rng.choice(len(iy), size=min(300000, len(iy)), replace=False)
iy, ix = iy[sel], ix[sel]
ux, uy = dx[iy, ix], dy[iy, ix]          # ao longo
vx, vy = -uy, ux                          # através
def amostra(img, oy, ox):
    return ndi.map_coordinates(img, [iy + oy, ix + ox], order=1, mode='nearest')
h0 = H[iy, ix]
d_ao = amostra(H, uy * 1.5, ux * 1.5) - amostra(H, -uy * 1.5, -ux * 1.5)
d_at = amostra(H, vy * 1.5, vx * 1.5) - amostra(H, -vy * 1.5, -vx * 1.5)
an = np.sqrt((d_at ** 2).mean() / max((d_ao ** 2).mean(), 1e-12))
risco = np.sqrt(np.median((h0 / np.maximum(loc[iy, ix], 0.05)) ** 2)) * 100
# borda do reflexo: perfil através da peça nos degraus fortes da luminância
g = np.hypot(ndi.sobel(Ys, 1), ndi.sobel(Ys, 0)) / 8
forte = g[iy, ix] > np.percentile(g[iy, ix], 97)
sig = []
for j in np.nonzero(forte)[0][:4000]:
    t = np.arange(-8, 8.5, 0.5)
    p = ndi.map_coordinates(Ys, [iy[j] + t * vy[j], ix[j] + t * vx[j]], order=1, mode='nearest')
    dp = np.abs(np.diff(p))
    if dp.sum() < 1e-6:
        continue
    tm = (t[:-1] + 0.25)
    m = (dp * tm).sum() / dp.sum()
    sig.append(np.sqrt((dp * (tm - m) ** 2).sum() / dp.sum()))
print('%s: anisotropia %.2f | riscado %.1f%% | borda do reflexo %.1f px | %d px medidos'
      % (rot, an, risco, np.median(sig), mask.sum()))
