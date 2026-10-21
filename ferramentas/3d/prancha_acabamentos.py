"""Prancha dos renders finais: uma coluna por acabamento, LED aceso em cima e apagado embaixo.

Uso: prancha_acabamentos.py pasta_renders saida.png
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

pasta, saida = Path(sys.argv[1]), sys.argv[2]
ACAB = [('brushed-nickel', 'Brushed nickel'), ('gold', 'Gold'), ('red-gold', 'Red gold'), ('black-matte', 'Black matte')]
LED = [('aceso', 'LED aceso'), ('apagado', 'LED apagado')]
W = 540; H = round(W * 1350 / 1080); M = 16; T = 56
fonte = ImageFont.truetype('DejaVuSans.ttf', 28); fpeq = ImageFont.truetype('DejaVuSans.ttf', 22)
out = Image.new('RGB', (len(ACAB) * (W + M) + M + 150, len(LED) * (H + M) + M + T), 'white')
dr = ImageDraw.Draw(out)
for i, (cod, nome) in enumerate(ACAB):
    x = 150 + M + i * (W + M)
    dr.text((x + 6, 14), nome, fill=(0, 0, 0), font=fonte)
    for j, (led, rot) in enumerate(LED):
        y = T + M + j * (H + M)
        f = pasta / f'lumiere-{cod}-{led}.png'
        if f.exists():
            out.paste(Image.open(f).convert('RGB').resize((W, H), Image.LANCZOS), (x, y))
        if i == 0:
            dr.text((M, y + H // 2), rot, fill=(0, 0, 0), font=fpeq)
out.save(saida)
print('salvo', saida, out.size)
