# -*- coding: utf-8 -*-
"""Cromadas LUX recortadas (PNG com alfa), sem IA.

O cromado aprovado é JPEG sobre o cinza do estúdio; os outros acabamentos são
PNG recortados. Para o site mostrar todos do mesmo jeito, a cromada recebe o
MESMO recorte já aprovado nos outros acabamentos: o alfa do PNG gold da mesma
posição, na mesma caixa. O RGB dentro do produto é o da cromada aprovada, pixel
a pixel; nada é redesenhado.

Uso: python recortar_cromadas.py
Grava aprovadas/<base>CR/<mesmo nome da cromada>.png ao lado do .jpg.
A caixa (posição do recorte na still) é achada pela medida: o deslocamento em
que as peças que não mudam de cor (vidro, carcaça branca, fio) batem com o
gold; precisa bater em pelo menos 99% dessas peças nas fotos apagadas.
"""
import argparse
import os

import numpy as np
from PIL import Image

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AP = os.path.join(RAIZ, "aprovadas")
MODELOS = {
    "10202": ("mesa-led-classique-lux", {1: 3, 2: 4, 3: 8, 4: 9}),
    "10288": ("mesa-led-royale-lux", {1: 1, 2: 2, 3: 3, 4: 4}),
    "10455": ("parede-led-mobile-lux", {1: 1, 2: 2, 3: 3, 4: 4}),
    "10509": ("parede-led-visage-lux", {1: 1, 2: 2, 3: 3, 4: 4}),
    "10554": ("parede-led-flex-lux", {1: 1, 2: 2, 3: 3, 4: 4}),
}


def caminhos(base, pos):
    nome, mapa = MODELOS[base]
    n = mapa[pos]
    cr = os.path.join(AP, base + "CR", "espelho-de-aumento-%s-cromado-gardie-%d.jpg" % (nome, n))
    gl = os.path.join(AP, base + "GL", "espelho-de-aumento-%s-dourado-gardie-%d.png" % (nome, pos))
    return cr, gl, cr[:-4] + ".png"


def recortar(base, pos):
    f_cr, f_gl, f_out = caminhos(base, pos)
    cr = np.asarray(Image.open(f_cr).convert("RGB"))
    gl = np.asarray(Image.open(f_gl).convert("RGBA"))
    h, w = gl.shape[:2]
    frac, x, y = achar_caixa(cr, gl)
    rgba = np.dstack([cr[y:y + h, x:x + w], gl[..., 3]])
    Image.fromarray(rgba, "RGBA").save(f_out, optimize=True)
    return f_out, frac, (x, y, x + w, y + h)


def achar_caixa(cr, gl):
    """Deslocamento (x, y) do PNG gold dentro da still cromada.

    Medida: fração das peças que não mudam de cor (vidro, carcaça branca, fio)
    em que cromada e gold diferem menos de 6 níveis. Grosso a 1/8 com
    matchTemplate, depois fino a ±12 px na resolução cheia.
    """
    import cv2
    alfa = gl[..., 3]
    h, w = alfa.shape
    neutro = (np.abs(gl[..., 0].astype(int) - gl[..., 2]) < 6) & (alfa == 255)
    f = 8
    pequeno = lambda a: cv2.resize(a, (a.shape[1] // f, a.shape[0] // f), interpolation=cv2.INTER_AREA)
    img = pequeno(cv2.cvtColor(np.ascontiguousarray(cr), cv2.COLOR_RGB2GRAY)).astype(np.float32)
    tpl = pequeno(cv2.cvtColor(np.ascontiguousarray(gl[..., :3]), cv2.COLOR_RGB2GRAY)).astype(np.float32)
    msk = (pequeno(neutro.astype(np.uint8) * 255) > 200).astype(np.float32)
    res = cv2.matchTemplate(img, tpl, cv2.TM_SQDIFF, mask=msk)
    _, _, (gx, gy), _ = cv2.minMaxLoc(res)
    ys, xs = np.nonzero(neutro)
    k = np.random.default_rng(7).choice(len(ys), size=min(20000, len(ys)), replace=False)
    ys, xs = ys[k], xs[k]
    ref = gl[ys, xs, :3].astype(int)
    melhor = (-1.0, 0, 0)
    for y in range(max(0, gy * f - 12), min(cr.shape[0] - h, gy * f + 12) + 1):
        for x in range(max(0, gx * f - 12), min(cr.shape[1] - w, gx * f + 12) + 1):
            frac = float((np.abs(cr[ys + y, xs + x].astype(int) - ref).max(1) < 6).mean())
            if frac > melhor[0]:
                melhor = (frac, x, y)
    return melhor


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.parse_args()
    for base in MODELOS:
        for pos in (1, 2, 3, 4):
            f_out, frac, caixa = recortar(base, pos)
            print("%sCR pos %d  caixa %s  peças neutras iguais %.4f  -> %s" % (base, pos, caixa, frac, os.path.relpath(f_out, RAIZ)))


if __name__ == "__main__":
    main()
