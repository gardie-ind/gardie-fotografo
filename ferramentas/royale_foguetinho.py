# -*- coding: utf-8 -*-
"""Royale Lux 10288: troca o pescoço antigo pelo foguetinho 0014-AL, sem IA.

Thiago, 28/10/2026: as stills foram feitas com o pescoço antigo; o produto de
hoje usa o foguetinho. Medido na still (base Ø145 = 1788 px, área espelhada
Ø152,4 = 1827 px, 12,15 px/mm) e confirmado por ele:

- a coluna antiga já é Ø19, igual ao foguetinho, e o anel perto da base é da
  base (injetado nela): os dois ficam como estão;
- o topo muda: some a haste fina com cone e anel sob a alça; o corpo Ø19,05
  sobe até a alça e fecha num ombro arredondado (R6,65) com a borda Ø12 × 2;
- a cabeça ficou 7 mm mais baixa ("Ficou 7mm mais baixa sim"): da alça ao anel
  da base sobram os 81 mm visíveis do foguetinho (106 menos o pino de 25 que
  entra na base);
- a alça das fotos é vareta meia-cana, e a real é barra chata (Thiago, 20:36):
  depois do pescoço, royale_alca.py troca a alça e põe o niple 0011-AL.

Como (sem reamostrar o produto):
- cabeça e alça (linhas acima do fundo da alça) descem DESCE px, inteiras;
- corpo antigo, anel, base e fio (linhas a partir de Y_CORPO) não mudam;
- entre os dois, borda, ombro e o trecho que falta do corpo são desenhados com
  os pixels do próprio corpo: cada linha nova copia uma linha do corpo e a
  estreita até o raio daquela altura. Um cilindro cromado de pé tem o reflexo
  em faixas verticais, então a linha estreitada é o mesmo reflexo num raio menor;
- o alfa é o mesmo nos 20 PNG do Royale (5 acabamentos × 4 posições), então a
  geometria é uma só e a textura vem de cada foto;
- o quadro é refeito pelo centrar_recortadas.py (corpo no centro, 93% do lado,
  fio saindo por uma borda); a alça é trocada na foto centrada e o quadro é
  conferido de novo.

Uso: python royale_foguetinho.py --saida DIR [--acabamentos CR,...] [--posicoes 1,2,3,4]
"""
import argparse
import glob
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import centrar_recortadas as cr  # noqa: E402
import royale_alca  # noqa: E402

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AP = os.path.join(RAIZ, "aprovadas")

PX_MM = 12.15          # base Ø145 = 1788 px; área espelhada Ø152,4 = 1827 px
DESCE = round(7 * PX_MM)   # 85 px: a cabeça 7 mm mais baixa (Thiago, 28/10)
Y_CORTE = 2744         # fundo da alça no centro: acima, cabeça e alça
Y_CORPO = 2945         # fim do anel antigo sob a alça; abaixo, corpo Ø19, anel da base, base e fio
MISTURA = (2960, 2995)  # o trecho novo se funde com o corpo antigo nestas linhas
FONTE_DY = 170         # cada linha nova copia a linha 170 px abaixo, no corpo limpo
BORDA_MM = (2.0, 6.0)  # altura e raio da borda do topo (Ø12 × 2)
OMBRO_MM = (5.87, 6.65)  # altura e raio do ombro (estimados no rascunho 0014-AL)
CORPO_R_MM = 9.525     # Ø3/4"
SOMBRA_BORDA = 0.80    # a borda fica na sombra da alça
TAMANHO = 4469         # lado dos PNG do Royale hoje


def eixo_e_raio(alfa):
    """Centro e meio-largura do corpo por linha (ajuste linear), em px."""
    ys = np.arange(Y_CORPO + 5, 3700, 5)
    cs, rs = [], []
    for y in ys:
        xs = np.nonzero(alfa[y, 1900:2650] > 128)[0] + 1900
        cs.append((xs[0] + xs[-1]) / 2)
        rs.append((xs[-1] - xs[0] + 1) / 2)
    ce = np.polyfit(ys, cs, 1)
    re = np.polyfit(ys, rs, 1)
    return (lambda y: np.polyval(ce, y)), (lambda y: np.polyval(re, y))


def perfil(y_topo, px_h):
    """Raio (mm) em cada linha do trecho novo, de y_topo até Y_CORPO."""
    hb, rb = BORDA_MM
    ho, R = OMBRO_MM
    y1 = y_topo + hb * px_h          # fim da borda
    y2 = y1 + ho * px_h              # fim do ombro
    out = []
    for y in range(y_topo, Y_CORPO):
        yc = y + 0.5
        if yc < y1:
            r, f = rb, SOMBRA_BORDA
        elif yc < y2:
            z = ho - (yc - y1) / px_h    # altura acima do fim do ombro
            r = (CORPO_R_MM - R) + np.sqrt(max(R * R - z * z, 0.0))
            f = 1.0
        else:
            r, f = CORPO_R_MM, 1.0
        out.append((y, r, f))
    return out, y1, y2


def bordas(alfa_linha, x0=1900, x1=2650):
    """Bordas esquerda e direita (cruzamento de 50% do alfa, subpixel)."""
    a = alfa_linha[x0:x1].astype(float) / 255
    i = np.nonzero(a >= 0.5)[0]
    l, r = i[0], i[-1]
    xl = x0 + l - 1 + (0.5 - a[l - 1]) / (a[l] - a[l - 1]) + 0.5
    xr = x0 + r + (a[r] - 0.5) / (a[r] - a[r + 1]) + 0.5
    return xl, xr


def trocar(rgba, ax, rc):
    """Devolve a foto com o foguetinho (antes de refazer o quadro).

    Cada linha nova copia a linha s = y + FONTE_DY do corpo antigo (deslocada
    pela inclinação do eixo) e a estreita até o raio daquela altura. No trecho
    de corpo o raio é o do próprio corpo, então a linha é só deslocada; entre
    MISTURA[0] e MISTURA[1] ela se funde com o corpo antigo, sem costura.
    """
    w = rgba.shape[1]
    novo = rgba.copy()
    novo[:Y_CORTE + DESCE] = 0
    novo[DESCE:Y_CORTE + DESCE] = rgba[:Y_CORTE]
    y_topo = Y_CORTE + DESCE
    linhas, _, _ = perfil(y_topo, PX_MM)
    linhas += [(y, CORPO_R_MM, 1.0) for y in range(Y_CORPO, MISTURA[1])]
    xs = np.arange(w, dtype=float)
    for y, r_mm, f in linhas:
        s = y + FONTE_DY
        xl, xr = bordas(rgba[s, :, 3])
        cs, hs = (xl + xr) / 2, (xr - xl) / 2
        ct, ht = cs + ax(y) - ax(s), hs * r_mm / CORPO_R_MM
        xsrc = cs + (xs + 0.5 - ct) * hs / ht - 0.5
        lin = rgba[s].astype(float)
        px = np.stack([np.interp(xsrc, xs, lin[:, c], left=0, right=0) for c in range(4)], -1)
        px[:, :3] *= f
        if y >= MISTURA[0]:
            t = (y - MISTURA[0] + 0.5) / (MISTURA[1] - MISTURA[0])
            px = px * (1 - t) + rgba[y].astype(float) * t
        novo[y] = np.clip(px + 0.5, 0, 255).astype(np.uint8)
    return novo


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--acabamentos", default="CR,NK.BU,GL,GL.RD,BL.MT")
    ap.add_argument("--posicoes", default="1,2,3,4")
    ap.add_argument("--saida", required=True, help="pasta de saída (espelha aprovadas/)")
    args = ap.parse_args()
    for acab in args.acabamentos.split(","):
        for pos in args.posicoes.split(","):
            fs = glob.glob(os.path.join(AP, "10288" + acab, "*-%s.png" % pos))
            if len(fs) != 1:
                raise SystemExit("10288%s posição %s: %d arquivos" % (acab, pos, len(fs)))
            f = fs[0]
            rgba = np.asarray(Image.open(f).convert("RGBA")).copy()
            if rgba.shape[:2] != (TAMANHO, TAMANHO):
                raise SystemExit("%s não tem %d px: já foi trocado?" % (f, TAMANHO))
            ax, rc = eixo_e_raio(rgba[..., 3])
            novo = trocar(rgba, ax, rc)
            tela, info = cr.centrar(novo)
            cr.conferir(novo, tela, info)
            com_alca = royale_alca.trocar_alca(tela, royale_alca.classique_de(acab, pos))
            tela, info = cr.centrar(com_alca)
            med = cr.conferir(com_alca, tela, info)
            destino = os.path.join(args.saida, "10288" + acab, os.path.basename(f))
            os.makedirs(os.path.dirname(destino), exist_ok=True)
            Image.fromarray(tela, "RGBA").save(destino, optimize=True)
            print("10288%s -%s  quadro %d px  ocupação %.3f  fio %d px" % (
                acab, pos, info["quadro"][2], med["ocupacao"], med["largura_do_fio_na_borda"]))


if __name__ == "__main__":
    main()
