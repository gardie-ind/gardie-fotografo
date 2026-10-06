# -*- coding: utf-8 -*-
"""Retoque local SEM IA: apaga um defeito pequeno em área lisa (vidro, parede).

Preenche a área branca da máscara por interpolação harmônica a partir da borda
(cada pixel vira a média dos vizinhos, até estabilizar) e devolve o grão medido
por passa-alta numa faixa logo acima da máscara. Os pixels fora da máscara não
mudam. Não inventa conteúdo: serve só para área lisa (ex.: botão touch
inventado no vidro). Em área com textura ou borda, use o FLUX Fill.

Uso:
  python3 retoque_local.py original.png mascara.png saida.png
  (máscara: branco = área a apagar; mesmo tamanho da original)

Depois: inspecao_imagem.py diff original.png saida.png mascara.png
"""
import sys
import numpy as np
from PIL import Image


def retocar(original, mascara, saida, iteracoes=4000, semente=0):
    a = np.asarray(Image.open(original).convert("RGB")).astype(float)
    m = np.asarray(Image.open(mascara).convert("L")) > 127
    if m.shape != a.shape[:2]:
        raise SystemExit("A máscara precisa ter o tamanho da imagem.")
    if not m.any():
        raise SystemExit("Máscara vazia.")
    ys, xs = np.where(m)
    H, W = m.shape
    y0, y1 = max(0, ys.min() - 3), min(H, ys.max() + 4)
    x0, x1 = max(0, xs.min() - 3), min(W, xs.max() + 4)

    # grão: desvio do passa-alta numa faixa acima da máscara
    fy0 = max(0, y0 - 20)
    faixa = a[fy0:max(fy0 + 3, y0 - 2), x0:x1]
    if faixa.shape[0] >= 3 and faixa.shape[1] >= 3:
        hp = faixa[1:-1, 1:-1] - (faixa[:-2, 1:-1] + faixa[2:, 1:-1] + faixa[1:-1, :-2] + faixa[1:-1, 2:]) / 4
        grao = float(np.std(hp)) * 0.9
    else:
        grao = 0.0

    sub = a[y0:y1, x0:x1].copy()
    mm = m[y0:y1, x0:x1]
    for c in range(3):
        ch = sub[..., c]
        ch[mm] = ch[~mm].mean()
        for _ in range(iteracoes):
            p = np.pad(ch, 1, mode="edge")
            ch[mm] = ((p[:-2, 1:-1] + p[2:, 1:-1] + p[1:-1, :-2] + p[1:-1, 2:]) / 4)[mm]
    ruido = np.random.default_rng(semente).normal(0, grao, mm.shape)
    for c in range(3):
        sub[..., c][mm] += ruido[mm]
    out = a.copy()
    out[y0:y1, x0:x1] = sub
    Image.fromarray(np.clip(out + 0.5, 0, 255).astype(np.uint8)).save(saida)
    print("OK: %s (grão %.2f)" % (saida, grao))


if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise SystemExit(__doc__)
    retocar(*sys.argv[1:4])
