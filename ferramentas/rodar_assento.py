# -*- coding: utf-8 -*-
"""Royale Lux 10288: pescoço foguetinho, alça barra chata com assento e niple do Classique, e o cabo
saindo do niple (02/11/2026), sem IA.

Mesmo caminho do royale_foguetinho.main, com a alça do royale_assento.py.
Uso: python rodar_assento.py --saida DIR [--origem DIR] [--acabamentos CR,...] [--posicoes 1,...]

A entrada são as stills antigas (-5/-2/-6/-4, ver royale_foguetinho.ARQUIVO), que
saíram de aprovadas/ quando entraram as novas (-7/-8/-9/-10, 03/11/2026). Para
refazer, extraia-as do histórico do git (commit d7b8c77) numa pasta com a mesma
estrutura de aprovadas/ e passe essa pasta em --origem.
"""
import argparse, glob, os, sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import centrar_recortadas as cr
import royale_foguetinho as rf
import royale_alca as ra
import royale_assento as rs
import royale_cabo as rcabo

AP = os.path.join(ra.RAIZ, "aprovadas")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--acabamentos", default="CR,NK.BU,GL,GL.RD,BL.MT")
    ap.add_argument("--posicoes", default="1")
    ap.add_argument("--saida", required=True)
    ap.add_argument("--origem", default=AP, help="pasta com as stills antigas (estrutura de aprovadas/)")
    a = ap.parse_args()
    for acab in a.acabamentos.split(","):
        for pos in a.posicoes.split(","):
            fs = glob.glob(os.path.join(a.origem, "10288" + acab, "*-%s.png" % rf.ARQUIVO[pos]))
            assert len(fs) == 1, fs
            rgba = np.asarray(Image.open(fs[0]).convert("RGBA")).copy()
            ax, rc = rf.eixo_e_raio(rgba[..., 3])
            novo = rf.trocar(rgba, ax, rc)
            tela, info = cr.centrar(novo)
            cl = ra.classique_de(acab, pos)
            com = rs.trocar_alca(tela, cl)
            com, cal = rcabo.por_cabo(com, cl)
            tela, info = cr.centrar(com)
            med = cr.conferir(com, tela, info)
            d = os.path.join(a.saida, "10288" + acab, os.path.basename(fs[0]))
            os.makedirs(os.path.dirname(d), exist_ok=True)
            Image.fromarray(tela, "RGBA").save(d, optimize=True)
            print("10288%s -%s ocupação %.3f" % (acab, pos, med["ocupacao"]), flush=True)


if __name__ == "__main__":
    main()
