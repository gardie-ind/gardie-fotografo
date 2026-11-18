# -*- coding: utf-8 -*-
"""Mede se o reflexo de uma peça lisa (canopla, base, aro) está liso: item q de guia/criterios.md.

Peça lisa reflete o estúdio em manchas largas e suaves; rechupe, amassado ou remendo aparece como ondulação
de média escala (dezenas de px) dentro do reflexo. A medida é uma passa-faixa da luminância (desfoque
gaussiano σ 4 px menos σ 16 px, na escala da still de catálogo, ~12 px/mm) numa caixa no miolo do reflexo,
longe das bordas da peça, dividida pelo nível médio da caixa. Ela ignora o grão e o escovado (finos demais)
e o degradê do reflexo (largo demais), e vale para todos os acabamentos.

Calibragem (placar.md › Calibragem, 2026-11-03, Svelte 10479, caixa 1975,775,2040,915): a -2, vetada pelo
Thiago por "rechupe do plástico e uma deformidade do reflexo", deu 0,036 (brushed nickel) a 0,070; a -3,
refeita lisa, 0,003 a 0,010.

uso: python3 medir_reflexo_liso.py img.png x0,y0,x1,y1 [mais imagens com a mesma caixa: img2.png ...]"""
import sys

import cv2
import numpy as np
from PIL import Image

LIMITE = 0.02    # ondulação relativa máxima (padrão — calibrar)


def medir(caminho, caixa):
    a = np.asarray(Image.open(caminho).convert("RGBA")).astype(float)
    L = a[..., :3].mean(-1)
    bp = cv2.GaussianBlur(L, (0, 0), 4) - cv2.GaussianBlur(L, (0, 0), 16)
    x0, y0, x1, y1 = caixa
    dentro = a[y0:y1, x0:x1, 3] > 250
    return float(bp[y0:y1, x0:x1][dentro].std() / max(L[y0:y1, x0:x1][dentro].mean(), 1.0))


if __name__ == "__main__":
    imgs = [sys.argv[1]] + sys.argv[3:]
    caixa = [int(v) for v in sys.argv[2].split(",")]
    for img in imgs:
        r = medir(img, caixa)
        print("%s  ondulação %.3f  -> %s" % (img.split("/")[-1], r, "VETO q" if r > LIMITE else "ok"))
