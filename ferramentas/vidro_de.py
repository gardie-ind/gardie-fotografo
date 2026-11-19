# vidro_de.py base.png doador.png cx cy r0 r1 saida.png : troca o vidro (disco dentro do anel de LED) da base pelo do doador,
# outra versão de IA aprovada no mesmo enquadramento. Peso 1 até r0, rampa suave até 0 em r1 (o brilho do anel por dentro).
# O nível do doador é igualado ao da base no miolo do vidro (mediana por canal), para a emenda não aparecer.
import sys, numpy as np
from PIL import Image
b_p, d_p = sys.argv[1:3]; cx, cy, r0, r1 = map(float, sys.argv[3:7]); s_p = sys.argv[7]
B = np.asarray(Image.open(b_p).convert('RGB')).astype(float); D = np.asarray(Image.open(d_p).convert('RGB')).astype(float)
H, W = B.shape[:2]; yy, xx = np.mgrid[:H, :W]; r = np.hypot(xx - cx, yy - cy)
fx = r < 0.75 * r0; k = np.median(B[fx], 0) / np.median(D[fx], 0)   # nível pelo miolo do vidro (fora da emenda)
w = np.clip((r1 - r) / (r1 - r0), 0, 1); w = w * w * (3 - 2 * w)
O = B * (1 - w[..., None]) + np.clip(D * k, 0, 255) * w[..., None]
print('ganho do doador', k.round(3), 'pixels trocados', int((w > 0.01).sum()))
Image.fromarray(O.round().astype(np.uint8)).save(s_p)
