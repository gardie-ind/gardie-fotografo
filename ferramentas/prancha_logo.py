"""Prancha de um LUX com logo a laser e padrão de luz: linhas = acabamentos
(ordem do Thiago), colunas = desligado e os 3 tons; última linha = o logo a
100% no cromado.

uso: python3 prancha_logo.py <pasta do modelo> <modelo> <título> <saida.jpg>"""
import sys, json, glob
from PIL import Image, ImageDraw, ImageFont

P, modelo, titulo, saida = sys.argv[1:5]
ACAB = [('cromado', 'Cromo'), ('brushed-nickel', 'Brushed Nickel'), ('gold', 'Gold'),
        ('red-gold', 'Red Gold'), ('black-matte', 'Matte Black')]
COLS = [('desligado', 'Desligado'), ('3000k', '3000K'), ('4500k', '4500K'), ('6000k', '6000K')]
c, lab, top, gap = 420, 200, 96, 8
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 26)
fb = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 30)
zh = 300
W = lab + 4 * (c + gap); H = top + 5 * (c + gap) + 50 + zh + gap
im = Image.new('RGB', (W, H), (255, 255, 255)); d = ImageDraw.Draw(im)
d.text((12, 12), titulo, fill=(0, 0, 0), font=fb)
for j, (_, t) in enumerate(COLS):
    d.text((lab + j * (c + gap) + 8, top - 36), t, fill=(0, 0, 0), font=f)
for i, (a, nome) in enumerate(ACAB):
    y = top + i * (c + gap)
    d.text((12, y + c // 2 - 14), nome, fill=(0, 0, 0), font=f)
    for j, (k, _) in enumerate(COLS):
        tile = Image.open(f'{P}/cabeca/{a}-{k}.jpg'); tile.thumbnail((c, c), Image.LANCZOS)
        im.paste(tile, (lab + j * (c + gap) + (c - tile.width) // 2, y + (c - tile.height) // 2))
# logo a 100% no cromado
med = json.load(open(f'{P}/logo-medidas.json'))['cromado']
cx, cy = med['logo_novo_centro']; lw = med['logo_novo_largura_px']
y = top + 5 * (c + gap) + 10
d.text((12, y), 'Logo, cromado', fill=(0, 0, 0), font=f)
d.text((12, y + 34), '(100%)', fill=(0, 0, 0), font=f)
for j, (k, _) in enumerate(COLS):
    p = glob.glob(f'{P}/{modelo}-cromado-{"desligado" if k == "desligado" else "ligado-" + k}.*')[0]
    src = Image.open(p).convert('RGB')
    hw = max(int(lw * 0.75), c // 2); hh = int(hw * zh / c)
    t = src.crop((int(cx - hw), int(cy - hh), int(cx + hw), int(cy + hh))).resize((c, zh), Image.LANCZOS)
    im.paste(t, (lab + j * (c + gap), y))
im.save(saida, quality=90)
print(im.size)
