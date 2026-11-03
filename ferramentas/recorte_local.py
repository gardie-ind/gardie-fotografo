# -*- coding: utf-8 -*-
"""Recorte do produto sem API: BiRefNet (ONNX) rodando no próprio contêiner.

Substitui o `estudio_fal.py recortar` quando o fal está sem saldo. Grava
<base>-recorte.png no mesmo formato: RGB da foto e alfa = produto.

Numa foto ambientada o BiRefNet pega o objeto mais saliente, que pode ser a
torneira ou a cuba. Passe --caixa em volta do espelho: ele roda só no recorte
da caixa (com folga), e o alfa fora dela fica zero.

Uso:
  python3 recorte_local.py foto.png pasta_saida/ [--caixa x0,y0,x1,y1] [--folga 40]

Modelo: BiRefNet-general-epoch_244.onnx (~970 MB), baixado uma vez de
https://github.com/danielgatis/rembg/releases/download/v0.0.0/ para ~/.u2net/.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

MODELO = os.path.expanduser("~/.u2net/BiRefNet-general-epoch_244.onnx")
URL = ("https://github.com/danielgatis/rembg/releases/download/v0.0.0/"
       "BiRefNet-general-epoch_244.onnx")
LADO = 1024
MEDIA = np.array([0.485, 0.456, 0.406], np.float32)
DESVIO = np.array([0.229, 0.224, 0.225], np.float32)


def alfa_birefnet(img, sessao):
    w, h = img.size
    x = np.asarray(img.convert("RGB").resize((LADO, LADO), Image.BICUBIC), np.float32) / 255.0
    x = ((x - MEDIA) / DESVIO).transpose(2, 0, 1)[None]
    y = sessao.run(None, {sessao.get_inputs()[0].name: x})[0][0, 0]
    y = 1.0 / (1.0 + np.exp(-y))
    a = Image.fromarray((np.clip(y, 0, 1) * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
    return np.asarray(a)


def recortar(foto, pasta, caixa=None, folga=40):
    import onnxruntime as ort
    if not os.path.exists(MODELO):
        raise SystemExit("Falta o modelo %s. Baixe de %s" % (MODELO, URL))
    sessao = ort.InferenceSession(MODELO, providers=["CPUExecutionProvider"])
    im = Image.open(foto).convert("RGB")
    W, H = im.size
    alfa = np.zeros((H, W), np.uint8)
    if caixa:
        x0, y0, x1, y1 = caixa
        x0, y0 = max(0, x0 - folga), max(0, y0 - folga)
        x1, y1 = min(W, x1 + folga), min(H, y1 + folga)
        alfa[y0:y1, x0:x1] = alfa_birefnet(im.crop((x0, y0, x1, y1)), sessao)
    else:
        alfa[:] = alfa_birefnet(im, sessao)
    os.makedirs(pasta, exist_ok=True)
    base = os.path.splitext(os.path.basename(foto))[0]
    out = os.path.join(pasta, base + "-recorte.png")
    rgba = np.dstack([np.asarray(im), alfa])
    Image.fromarray(rgba, "RGBA").save(out)
    print("OK: %s (alfa > 0,5 em %d px)" % (out, int((alfa > 127).sum())))
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("foto")
    p.add_argument("pasta")
    p.add_argument("--caixa", help="x0,y0,x1,y1 em volta do produto")
    p.add_argument("--folga", type=int, default=40)
    a = p.parse_args()
    caixa = tuple(map(int, a.caixa.split(","))) if a.caixa else None
    recortar(a.foto, a.pasta, caixa, a.folga)


if __name__ == "__main__":
    sys.exit(main())
