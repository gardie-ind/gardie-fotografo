# -*- coding: utf-8 -*-
"""Curva o reflexo ORIGINAL do vidro por warp geométrico — ZERO IA.

Retoque opcional do vidro: pega o reflexo
que já existe na foto original e aplica uma distorção radial de lente
(centro ampliado, como espelho de aumento côncavo) SOMENTE dentro do
círculo do vidro. O anel de LED, o produto e a cena ficam com os pixels
originais — a edição do anel é BLOQUEADA por construção.

Uso:
  py curva_vidro.py entrada.png saida.png cx cy r k
    cx,cy,r = círculo do vidro em pixels · k = intensidade 0.0-0.9
    (k=0.25 sutil · k=0.45 média · k=0.65 forte)
"""
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


def curvar(entrada, saida, cx, cy, r, k):
    im = Image.open(entrada).convert("RGB")
    w, h = im.size
    box = (cx - r, cy - r, cx + r, cy + r)
    quad = np.asarray(im.crop(box)).astype(np.float32)
    D = 2 * r

    yy, xx = np.mgrid[0:D, 0:D].astype(np.float32)
    ux, uy = (xx - r) / r, (yy - r) / r
    rad = np.sqrt(ux**2 + uy**2)
    rad = np.clip(rad, 1e-6, None)

    # mapeamento: centro ampliado (1-k), borda inalterada — lente de aumento
    fator = (1.0 - k) + k * (rad**2)
    sx = np.clip(r + ux * fator * r, 0, D - 1)
    sy = np.clip(r + uy * fator * r, 0, D - 1)

    x0, y0 = sx.astype(np.int32), sy.astype(np.int32)
    x1, y1 = np.clip(x0 + 1, 0, D - 1), np.clip(y0 + 1, 0, D - 1)
    fx, fy = (sx - x0)[..., None], (sy - y0)[..., None]
    warp = (
        quad[y0, x0] * (1 - fx) * (1 - fy)
        + quad[y0, x1] * fx * (1 - fy)
        + quad[y1, x0] * (1 - fx) * fy
        + quad[y1, x1] * fx * fy
    )
    warp_im = Image.fromarray(warp.astype(np.uint8))

    # máscara circular com borda suave: warp só DENTRO do vidro
    m = Image.new("L", (D, D), 0)
    ImageDraw.Draw(m).ellipse([0, 0, D, D], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(3))

    out = im.copy()
    out.paste(Image.composite(warp_im, im.crop(box), m), box)
    out.save(saida)
    print("OK:", saida, f"(k={k})")


if __name__ == "__main__":
    if len(sys.argv) != 7:
        print(__doc__)
        sys.exit(1)
    curvar(
        sys.argv[1], sys.argv[2],
        int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]),
        float(sys.argv[6]),
    )
