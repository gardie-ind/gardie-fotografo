# -*- coding: utf-8 -*-
"""Pranchas do lote v4 (24/10): uma por vista, uma coluna por acabamento (com cromado) e uma
linha por estado do anel: apagado e os três tons do padrão de 22/10 (3000K, 4500K, 6000K).
Mais a prancha "anel antes × agora": recorte da cabeça de frente, render de 23/10 contra o v4.

Uso: prancha_v4.py renders/v4 saida_dir
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ACAB = [('cromado', 'Cromado'), ('brushed-nickel', 'Brushed nickel'), ('gold', 'Gold'),
        ('red-gold', 'Red gold'), ('black-matte', 'Black matte')]
LINHAS = [('apagado', 'LED apagado'), ('3000', '3000K'), ('4500', '4500K'), ('6000', '6000K')]
VISTAS = [('frente', 'Frente'), ('tres-quartos', '3/4, braço fechado'), ('braco-aberto', 'Braço aberto')]
W = 360; H = round(W * 1350 / 1080); M = 12; T = 96; E = 150
F = ImageFont.truetype('DejaVuSans.ttf', 24); FP = ImageFont.truetype('DejaVuSans.ttf', 20)
FT = ImageFont.truetype('DejaVuSans-Bold.ttf', 30)


def arquivo(pasta, cod, linha):
    if linha == 'apagado':
        return pasta / f'lumiere-{cod}-apagado.png'
    return pasta / 'tons' / f'lumiere-{cod}-{linha}.png'


def prancha_vista(base, vista, titulo, saida):
    pasta = base / vista
    out = Image.new('RGB', (E + len(ACAB) * (W + M) + M, T + len(LINHAS) * (H + M) + M), 'white')
    d = ImageDraw.Draw(out)
    d.text((M, 12), f'Lumière 22005 · {titulo}', font=FT, fill=(0, 0, 0))
    for i, (cod, nome) in enumerate(ACAB):
        x = E + M + i * (W + M)
        d.text((x + 4, T - 34), nome, font=F, fill=(0, 0, 0))
        for j, (lin, rot) in enumerate(LINHAS):
            y = T + M + j * (H + M)
            f = arquivo(pasta, cod, lin)
            if f.exists():
                out.paste(Image.open(f).convert('RGB').resize((W, H), Image.LANCZOS), (x, y))
            if i == 0:
                d.text((M, y + H // 2 - 12), rot, font=FP, fill=(0, 0, 0))
    out.save(saida)
    print(saida, out.size)


def recorte(caminho, cx=471.2, cy=577.7, r=312.8, k=1.08, lado=620):
    im = Image.open(caminho).convert('RGB'); m = k * r
    return im.crop((round(cx - m), round(cy - m), round(cx + m), round(cy + m))).resize((lado, lado), Image.LANCZOS)


def prancha_anel(base, saida, cod='brushed-nickel'):
    lado = 620
    pares = [(Path('renders/frente-prototipo') / f'lumiere-{cod}-aceso.png', '23/10: luz vinda dos LEDs da placa'),
             (base / 'frente' / 'tons' / f'lumiere-{cod}-4500.png', '24/10: anel por igual + padrão 4500K')]
    out = Image.new('RGB', (M + 2 * (lado + M), 60 + lado + 50), 'white'); d = ImageDraw.Draw(out)
    d.text((M, 12), 'Anel aceso, antes × agora (brushed nickel, de frente)', font=FT, fill=(0, 0, 0))
    for i, (f, rot) in enumerate(pares):
        x = M + i * (lado + M)
        out.paste(recorte(f, lado=lado), (x, 56))
        d.text((x + 4, 56 + lado + 12), rot, font=FP, fill=(40, 40, 40))
    out.save(saida)
    print(saida, out.size)


if __name__ == '__main__':
    base, dest = Path(sys.argv[1]), Path(sys.argv[2]); dest.mkdir(parents=True, exist_ok=True)
    for v, t in VISTAS:
        if (base / v).exists():
            prancha_vista(base, v, t, dest / f'prancha-{v}.png')
    if (base / 'frente' / 'tons').exists():
        prancha_anel(base, dest / 'prancha-anel-antes-agora.png')
