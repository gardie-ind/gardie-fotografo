# -*- coding: utf-8 -*-
"""Prancha de comparação protótipo × CAD (23/10): frente na mesma escala da cabeça e verso.

Cada painel é um recorte quadrado em volta do centro da cabeça, com meia largura = k × raio
do aro (medido por ajuste de elipse na foto e por círculo na silhueta do render), então as
três frentes saem com a cabeça do mesmo tamanho.

Uso: python prancha_perfil.py saida.png quadro-video-6s.jpg [cx,cy,r do render de trás]
(rodar na pasta do estudo: prototipo/, renders/frontal-v2/ e renders/perfil/)
"""
import sys
from PIL import Image, ImageDraw, ImageFont

B = ''
LADO = 560
FONTE = ImageFont.truetype('DejaVuSans.ttf', 21)
FONTE_P = ImageFont.truetype('DejaVuSans.ttf', 17)
FONTE_T = ImageFont.truetype('DejaVuSans-Bold.ttf', 25)


def recorte(caminho, cx, cy, r, k=1.12, fundo=(20, 24, 28)):
    im = Image.open(caminho).convert('RGB')
    m = k * r
    caixa = (round(cx - m), round(cy - m), round(cx + m), round(cy + m))
    out = Image.new('RGB', (caixa[2] - caixa[0], caixa[3] - caixa[1]), fundo)
    out.paste(im.crop((max(caixa[0], 0), max(caixa[1], 0), min(caixa[2], im.width), min(caixa[3], im.height))),
              (max(-caixa[0], 0), max(-caixa[1], 0)))
    return out.resize((LADO, LADO), Image.LANCZOS)


def painel(img, titulo, linhas):
    alt = LADO + 40 + 26 * len(linhas) + 10
    p = Image.new('RGB', (LADO, alt), 'white'); d = ImageDraw.Draw(p)
    d.text((4, 8), titulo, font=FONTE, fill=(20, 20, 20))
    p.paste(img, (0, 40))
    for i, l in enumerate(linhas):
        d.text((4, LADO + 46 + 26 * i), l, font=FONTE_P, fill=(60, 60, 60))
    return p


def main(saida, quadro):
    # Frente. Foto: elipses ajustadas (aro 381,2 px de raio, centro 886,379).
    # Render: círculo da silhueta (312,8 px, centro 471,2,577,7), mesma câmera nos dois renders.
    f1 = painel(recorte(B + 'prototipo/lumiere-nk-bu-ligado-frontal.jpg', 886, 379, 381.2),
                'Protótipo (foto de frente)',
                ['aro ~10 mm, anel ~17 mm, espelho ~Ø150', '(medido, tomando o aro Ø204,5 do CAD)'])
    f2 = painel(recorte(B + 'renders/frontal-v2/lumiere-brushed-nickel-aceso.png', 471.2, 577.7, 312.8),
                'CAD V3, render atual',
                ['aro 12,8 mm, anel 10,1 mm, espelho Ø158,75', '(desenhos E-0004 e E-0001-V1)'])
    f3 = painel(recorte(B + 'renders/perfil/frente-prototipo-brushed-nickel-aceso.png', 471.2, 577.7, 312.8),
                'CAD com a frente do protótipo',
                ['aro 10 mm, anel 17,3 mm, espelho Ø150', '(só o aro e a prata mudam)'])
    # Verso: quadro de 6,0 s do vídeo e o CAD visto de trás, ~27° de inclinação.
    v1 = painel(recorte(quadro, 240, 290, 145, k=1.25),
                'Protótipo (vídeo, 6,0 s)',
                ['tampa traseira polida, coluna no centro,', 'articulação e braço lateral'])
    v2 = painel(recorte(B + 'renders/perfil/verso-brushed-nickel.png', *VERSO, k=1.25),
                'CAD V3 visto de trás (~27°)',
                ['mesma peça; braço longo e placa', 'escondidos (no vídeo o braço está aberto)'])
    W = 3 * LADO + 4 * 16
    H = 50 + f1.height + 50 + v1.height + 16
    o = Image.new('RGB', (W, H), 'white'); d = ImageDraw.Draw(o)
    d.text((16, 12), 'Frente: mesma escala da cabeça', font=FONTE_T, fill=(0, 0, 0))
    for i, p in enumerate((f1, f2, f3)):
        o.paste(p, (16 + i * (LADO + 16), 50))
    y = 50 + f1.height + 8
    d.text((16, y + 4), 'Verso', font=FONTE_T, fill=(0, 0, 0))
    for i, p in enumerate((v1, v2)):
        o.paste(p, (16 + i * (LADO + 16), y + 42))
    o.save(saida)
    print(saida, o.size)


VERSO = (539.5, 550.5, 367.8)   # elipse da cabeça no render de trás (semi-eixo 357,7 px, razão 0,89 como no vídeo)

if __name__ == '__main__':
    if len(sys.argv) > 3:
        VERSO = tuple(float(v) for v in sys.argv[3].split(','))
    main(sys.argv[1], sys.argv[2])
