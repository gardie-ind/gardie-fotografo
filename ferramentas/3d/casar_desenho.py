"""Casa a vista frontal do A-0001 (página 1, 110 dpi) com o render ortográfico frontal.

Uso: casar_desenho.py desenho.png render_orto.png saida.png [mm_por_px_render]

O render ortográfico tem o centro da imagem no centro da caixa do produto (render_lumiere.py
--orto). O desenho é medido: caixa das linhas pretas da vista frontal. As linhas do desenho
vão em vermelho por cima do render, na mesma escala, e a saída leva as três vistas lado a lado.
"""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

des, ren, saida = sys.argv[1:4]
mmpx = float(sys.argv[4]) if len(sys.argv) > 4 else 0.25
D = np.asarray(Image.open(des).convert('RGB')).astype(int)
x0, y0, x1, y1 = 180, 40, 740, 620          # janela da vista frontal na página 1
J = D[y0:y1, x0:x1]
preto = (J.max(axis=2) < 110)
ys, xs = np.nonzero(preto)
bx0, bx1, by0, by1 = xs.min(), xs.max(), ys.min(), ys.max()
larg_px, alt_px = bx1 - bx0 + 1, by1 - by0 + 1
px_mm = (larg_px / 252.6 + alt_px / 270.3) / 2
print(f'desenho: caixa {larg_px} x {alt_px} px, {px_mm:.4f} px/mm '
      f'(largura {larg_px / px_mm:.1f} mm, altura {alt_px / px_mm:.1f} mm)')

R = Image.open(ren).convert('RGB')
esc = px_mm * mmpx                            # render (px) -> desenho (px)
Rs = R.resize((round(R.width * esc), round(R.height * esc)), Image.LANCZOS)
cx_d, cy_d = bx0 + larg_px / 2, by0 + alt_px / 2
ox, oy = round(cx_d - Rs.width / 2), round(cy_d - Rs.height / 2)
# Recorte comum: a janela do desenho, com margem
M = 20
caixa = (bx0 - M, by0 - M, bx1 + M, by1 + M)
Rc = Image.new('RGB', (x1 - x0, y1 - y0), 'white'); Rc.paste(Rs, (ox, oy))
Rc = Rc.crop(caixa)
Dc = Image.fromarray(J.astype(np.uint8)).crop(caixa)
P = preto[caixa[1]:caixa[3], caixa[0]:caixa[2]]
Ov = np.asarray(Rc).copy(); Ov[P] = (230, 20, 20)
Ov = Image.fromarray(Ov)
# Medida: fração das linhas do desenho com uma borda do render a até 2 px (1 mm).
G = np.asarray(Rc.convert('L')).astype(float)
gx = np.zeros_like(G); gy = np.zeros_like(G)
gx[:, 1:-1] = G[:, 2:] - G[:, :-2]; gy[1:-1, :] = G[2:, :] - G[:-2, :]
borda = np.hypot(gx, gy) > 24
viz = np.zeros_like(borda)
for dy in range(-2, 3):
    for dx in range(-2, 3):
        viz |= np.roll(np.roll(borda, dy, 0), dx, 1)
casadas = (P & viz).sum() / max(P.sum(), 1)
print(f'linhas do desenho com borda do render a <= 1 mm: {100 * casadas:.1f}% de {P.sum()} px')
w, h = Dc.size
f = 2                                         # amplia para ler os detalhes
out = Image.new('RGB', (w * 3 * f + 40, h * f + 70), 'white')
dr = ImageDraw.Draw(out)
fonte = ImageFont.truetype('DejaVuSans.ttf', 30)
for i, (im, t) in enumerate(((Dc, 'Desenho A-0001-V3 (vista frontal)'), (Rc, 'Render ortográfico do CAD'),
                             (Ov, 'Linhas do desenho sobre o render'))):
    out.paste(im.resize((w * f, h * f), Image.LANCZOS), (i * (w * f + 20), 64))
    dr.text((i * (w * f + 20) + 6, 14), t, fill=(0, 0, 0), font=fonte)
out.save(saida)
print('salvo', saida, out.size)
