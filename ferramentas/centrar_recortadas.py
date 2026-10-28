# -*- coding: utf-8 -*-
"""Recortadas LUX com o espelho no centro e o fio sem destaque, sem IA.

Thiago, 27/10/2026, sobre as cromadas recortadas: "Está com muito destaque
para o fio, não faça isso. O espelho deve ficar centralizado."

O PNG recortado vem na caixa da still, que vai até onde a foto corta o fio,
e o produto fica fora do centro. Aqui o quadro passa a ser quadrado (1:1, a
página de produto em guia/cena.md), centrado no corpo do produto (tudo menos
o fio), com o corpo ocupando 93% do lado maior, como a capa. O fio sai pela
borda do quadro.

- Corpo: o alfa sem as partes mais finas que 81 px (abertura morfológica); o
  fio tem 47 a 56 px. Só serve para achar o centro e o tamanho do quadro.
- Os pixels do recorte não mudam: o quadro é um deslocamento inteiro, sem
  reamostragem.
- Nos modelos de mesa, a foto corta o fio antes da borda do quadro (181 px no
  Classique, 285 px no Royale). O trecho que falta, reto, repete os últimos
  120 px do fio na direção em que ele corre. É o mesmo fio desenhado pelo
  cabo_real.py, sem IA.
- O alfa é o mesmo em todos os acabamentos e posições de um modelo, então o
  quadro é um só por modelo.
- Confere, em cada saída, que só o fio cruza a borda do quadro, numa faixa
  única da largura dele, e que o centro do corpo é o centro do quadro.

Uso: python centrar_recortadas.py [--acabamentos CR,GL,GL.RD,NK.BU,BL.MT] [--modelos 10202,...] [--saida DIR]
Sem --saida, regrava os PNG no lugar.
"""
import argparse
import glob
import math
import os

import numpy as np
from PIL import Image

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AP = os.path.join(RAIZ, "aprovadas")
BASES = ("10202", "10288", "10455", "10509", "10554")
OCUPACAO = 0.93
RAIO_CORPO = 40
FIO_MAX = 70


def corpo(alfa):
    import cv2
    m = (alfa > 128).astype(np.uint8)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * RAIO_CORPO + 1,) * 2)
    return cv2.morphologyEx(m, cv2.MORPH_OPEN, k) > 0


def quadro(alfa):
    """(esquerda, topo, lado) do quadro em coordenadas da caixa."""
    ys, xs = np.nonzero(corpo(alfa))
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    lado = math.ceil(max(x1 - x0, y1 - y0) / OCUPACAO)
    lado += (lado - (x1 - x0)) % 2  # folga par: centro exato na horizontal
    esq = (x0 + x1 - lado) // 2
    topo = (y0 + y1 - lado) // 2
    return esq, topo, lado, (x0, y0, x1, y1)


def saida_do_fio(alfa):
    """Borda da caixa por onde o fio sai: 'direita' ou 'baixo'."""
    bordas = {"direita": alfa[:, -1], "baixo": alfa[-1, :], "esquerda": alfa[:, 0], "topo": alfa[0, :]}
    com = [b for b, v in bordas.items() if (v > 0).any()]
    if com not in (["direita"], ["baixo"]):
        raise SystemExit("o fio devia sair por uma borda só, saiu por %s" % com)
    return com[0]


def estender_fio(rgba, n, bloco=120):
    """Acrescenta n colunas à direita, continuando o fio reto.

    Repete os últimos `bloco` px do fio em vaivém (espelhados na borda, sem
    degrau), cada coluna deslocada na vertical para seguir a inclinação dele.
    Assim o trecho novo leva o grão da foto, em vez de uma coluna só repetida.
    """
    a = rgba[..., 3]
    w = a.shape[1]
    cols = np.arange(w - 300, w)
    cent = []
    for c in cols:
        lin = np.nonzero(a[:, c] > 0)[0]
        peso = a[lin, c].astype(float)
        cent.append((lin * peso).sum() / peso.sum())
    incl = np.polyfit(cols, cent, 1)[0]
    ext = np.zeros((a.shape[0], n, 4), np.uint8)
    y = np.arange(a.shape[0], dtype=float)
    for j in range(1, n + 1):
        t = j % (2 * bloco)
        k = t if t <= bloco else 2 * bloco - t
        secao = rgba[:, w - 1 - k].astype(float)
        desl = incl * (j + k)
        for ch in range(4):
            ext[:, j - 1, ch] = np.clip(np.interp(y - desl, y, secao[:, ch], left=0, right=0) + 0.5, 0, 255)
    return np.concatenate([rgba, ext], axis=1)


def centrar(rgba):
    alfa = rgba[..., 3]
    saida = saida_do_fio(alfa)
    esq, topo, lado, caixa_corpo = quadro(alfa)
    h, w = alfa.shape
    if saida == "baixo":
        if topo + lado > h:
            raise SystemExit("o quadro passa da borda de baixo da foto (fio cortado no ar)")
    else:
        falta = esq + lado - w
        if falta > 0:
            rgba = estender_fio(rgba, falta)
    h2, w2 = rgba.shape[:2]
    tela = np.zeros((lado, lado, 4), np.uint8)
    sx0, sy0 = max(esq, 0), max(topo, 0)
    sx1, sy1 = min(esq + lado, w2), min(topo + lado, h2)
    tela[sy0 - topo:sy1 - topo, sx0 - esq:sx1 - esq] = rgba[sy0:sy1, sx0:sx1]
    return tela, {"saida": saida, "quadro": (esq, topo, lado), "corpo": caixa_corpo,
                  "fio_estendido": max(0, esq + lado - w) if saida == "direita" else 0}


def conferir(original, tela, info):
    esq, topo, lado = info["quadro"]
    h, w = original.shape[:2]
    # 1) pixels do recorte, onde caem no quadro, iguais
    sx0, sy0, sx1, sy1 = max(esq, 0), max(topo, 0), min(esq + lado, w), min(topo + lado, h)
    assert np.array_equal(tela[sy0 - topo:sy1 - topo, sx0 - esq:sx1 - esq], original[sy0:sy1, sx0:sx1])
    # 2) só o fio cruza a borda: uma faixa, numa borda só
    a = tela[..., 3] > 0
    bordas = {"topo": a[0], "baixo": a[-1], "esquerda": a[:, 0], "direita": a[:, -1]}
    com = {b: v for b, v in bordas.items() if v.any()}
    assert list(com) == [info["saida"]], com.keys()
    v = com[info["saida"]].astype(int)
    faixas = np.count_nonzero(np.diff(np.concatenate([[0], v, [0]])) == 1)
    assert faixas == 1 and v.sum() <= FIO_MAX, (faixas, v.sum())
    # 3) corpo centrado
    x0, y0, x1, y1 = info["corpo"]
    dx = (x0 + x1) / 2 - esq - lado / 2
    dy = (y0 + y1) / 2 - topo - lado / 2
    assert abs(dx) <= 1 and abs(dy) <= 1, (dx, dy)
    return {"largura_do_fio_na_borda": int(v.sum()), "desvio_centro_px": (dx, dy),
            "ocupacao": round(max(x1 - x0, y1 - y0) / lado, 3)}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--acabamentos", default="CR")
    ap.add_argument("--modelos", default=",".join(BASES))
    ap.add_argument("--saida", help="pasta de saída (espelha aprovadas/); sem ela, regrava no lugar")
    args = ap.parse_args()
    for base in args.modelos.split(","):
        for acab in args.acabamentos.split(","):
            for f in sorted(glob.glob(os.path.join(AP, base + acab, "*.png"))):
                im = Image.open(f)
                if im.mode != "RGBA" or im.size[0] == im.size[1]:
                    continue  # ambientada ou já quadrada
                original = np.asarray(im)
                tela, info = centrar(original)
                med = conferir(original, tela, info)
                destino = f if not args.saida else os.path.join(args.saida, base + acab, os.path.basename(f))
                os.makedirs(os.path.dirname(destino), exist_ok=True)
                Image.fromarray(tela, "RGBA").save(destino, optimize=True)
                print("%s%s %s  quadro %d px  fio sai por %s (%d px, +%d px estendidos)  ocupação %.3f" % (
                    base, acab, os.path.basename(f)[-6:], info["quadro"][2], info["saida"],
                    med["largura_do_fio_na_borda"], info["fio_estendido"], med["ocupacao"]))


if __name__ == "__main__":
    main()
