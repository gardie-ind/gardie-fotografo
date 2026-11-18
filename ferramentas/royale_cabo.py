# -*- coding: utf-8 -*-
"""Royale Lux 10288: o cabo saindo do niple aberto 0011-AL, sem IA (02/11/2026).

Thiago, 02/11/2026, 23:14, no niple do Classique: "Também precisa do cabo elétrico saindo".
Rota (guia/produto.md › Cabo e plug): sai do meio da traseira da cabeça, desce numa alça curta e
entra no pivô por cima; no Royale, o pivô é o niple aberto (furo Ø6,8), em cima do assento da alça.

Como:
- a linha de centro do cabo é traçada em 3D, na câmera da still (royale_alca.projetar): sai do furo
  do niple na vertical e dobra para trás e para cima, rumo à traseira da cabeça;
- o cabo é um cilindro de CABO_MM, com a luz do estúdio medida no cabo real da própria foto (o
  trecho que sai de trás da base): o perfil de lá dá o claro de cima e o escuro de baixo, e o
  modelo de Lambert com essa luz dá o perfil no ângulo novo; a cor vem do mesmo cabo (no black
  matte, o cabo preto);
- ele só aparece no fundo (alfa da foto) e por cima da metade de trás do topo do niple; a cabeça,
  o niple (metade da frente) e a alça ficam na frente dele.
"""
import os
import sys

import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import royale_alca as ra  # noqa: E402
import royale_assento as rs  # noqa: E402

CABO_MM = 4.7          # 54 px no cabo da base, a ≈ 11,4 px/mm (atrás da base, mais longe)
SS = 4
LUZ = np.array([0.0, -0.6, -0.8])   # de cima e da frente (x direita, y para baixo, z para longe)
TOPO_NIPLE = -ra.RI + 3.5           # aba 1 + calota 2,5
# linha de centro (x, y, z) em mm no referencial da alça: começa dentro do niple
ROTA = np.array([(0, TOPO_NIPLE - 1.5, 0), (0, TOPO_NIPLE, 0), (0, TOPO_NIPLE + 1.2, -0.5),
                 (0, TOPO_NIPLE + 2.2, -1.8), (0, TOPO_NIPLE + 3.1, -3.8), (0, TOPO_NIPLE + 4.0, -6.5),
                 (0, TOPO_NIPLE + 5.0, -10.0), (0, TOPO_NIPLE + 6.3, -14.0), (0, TOPO_NIPLE + 8.0, -18.0),
                 (0, TOPO_NIPLE + 11.0, -22.0), (0, TOPO_NIPLE + 15.0, -25.0)], float)


def perfil_da_base(rgba, x=3800):
    """Cor do cabo real (o que sai de trás da base) através dele, de cima para baixo, numa coluna."""
    a = rgba[3300:4000, x, 3].astype(float)
    ys = np.nonzero(a > 250)[0]
    corpo = rgba[3300 + ys[0]:3300 + ys[-1] + 1, x, :3].astype(float)
    return corpo


def calibrar(corpo):
    """amb + k * max(N.L, 0) no cabo da base (normal para baixo no plano da foto)."""
    n = len(corpo)
    u = (np.arange(n) + 0.5) / n * 2 - 1
    L = LUZ / np.linalg.norm(LUZ)
    NL = np.clip(L[1] * u + (-L[2]) * np.sqrt(1 - u * u), 0, 1)
    lum = corpo.mean(-1)
    A = np.stack([np.ones(n), NL], -1)
    amb, k = np.linalg.lstsq(A, lum, rcond=None)[0]
    tinta = corpo.mean(0) / max(lum.mean(), 1e-6)
    return amb, k, tinta


def _curva(n=400):
    t = np.linspace(0, 1, len(ROTA))
    tt = np.linspace(0, 1, n)
    from scipy.interpolate import CubicSpline
    P = CubicSpline(t, ROTA, axis=0)(tt)
    uv = ra.projetar(P)
    Z = P[:, 0] * np.sin(ra.PSI) + P[:, 2] * np.cos(ra.PSI)
    esc = ra.K * ra.DIST / (ra.DIST - Z)         # px/mm em cada ponto
    return uv, esc


def niple_mascara(shape, classique):
    """Onde ficou o niple do Classique (alfa 0-1) e a linha do furo (y na foto)."""
    nrgb, na, nb = rs.niple_classique(classique)
    bx, by = rs.posicao_base_niple()
    ox, oy = bx - nb[0], by - nb[1]
    M = np.float32([[1, 0, ox], [0, 1, oy]])
    m = cv2.warpAffine(na, M, (shape[1], shape[0]), flags=cv2.INTER_LINEAR)
    y_furo = ra.projetar(np.array([0.0, TOPO_NIPLE, 0.0]))[1]
    return m, y_furo


def por_cabo(rgba, classique):
    """rgba: uint8 do Royale com a alça nova (antes de centrar). Devolve uint8 com o cabo."""
    img = rgba.astype(np.float32) / 255
    H, W = img.shape[:2]
    amb, k, tinta = calibrar(perfil_da_base(rgba))
    uv, esc = _curva()
    larg = CABO_MM * esc
    m = int(larg.max()) + 6
    x0, x1 = int(uv[:, 0].min()) - m, int(uv[:, 0].max()) + m
    y0, y1 = int(uv[:, 1].min()) - m, int(uv[:, 1].max()) + m
    X, Y = np.meshgrid(x0 + (np.arange((x1 - x0) * SS) + 0.5) / SS, y0 + (np.arange((y1 - y0) * SS) + 0.5) / SS)
    # ponto mais perto da curva (curva densa)
    d2 = np.full(X.shape, np.inf); j = np.zeros(X.shape, int)
    for i in range(len(uv)):
        dd = (X - uv[i, 0]) ** 2 + (Y - uv[i, 1]) ** 2
        mm = dd < d2
        d2[mm] = dd[mm]; j[mm] = i
    tg = np.gradient(uv, axis=0); tg /= np.linalg.norm(tg, axis=1)[:, None]
    nrm = np.stack([-tg[:, 1], tg[:, 0]], -1)
    nrm[nrm[:, 1] < 0] *= -1                         # normal no plano da foto para baixo
    dsg = (X - uv[j, 0]) * nrm[j, 0] + (Y - uv[j, 1]) * nrm[j, 1]
    u = dsg / (larg[j] / 2)
    corpo = (np.abs(u) <= 1) & (j > 0) & (j < len(uv) - 1)
    uc = np.clip(u, -1, 1)
    L = LUZ / np.linalg.norm(LUZ)
    NL = np.clip(uc * (nrm[j, 0] * L[0] + nrm[j, 1] * L[1]) + (-L[2]) * np.sqrt(1 - uc * uc), 0, 1)
    val = amb + k * NL
    h, w = (y1 - y0), (x1 - x0)
    red = lambda a: a.reshape(h, SS, w, SS).mean((1, 3))
    A = red(corpo.astype(np.float32))
    V = red((corpo * val).astype(np.float32)) / np.maximum(A, 1e-6)
    A = cv2.GaussianBlur(A, (0, 0), 0.8)
    V = cv2.GaussianBlur(V * (A > 0), (0, 0), 0.8) / np.maximum(cv2.GaussianBlur((A > 0).astype(np.float32), (0, 0), 0.8), 1e-6)
    cor = np.clip(V[..., None] * tinta[None, None] / 255, 0, 1)
    # visível: fundo, e a metade de trás do topo do niple (acima da linha do furo)
    nm, y_furo = niple_mascara((H, W), classique)
    roi = (slice(y0, y1), slice(x0, x1))
    a_foto = img[roi][..., 3]
    yy = np.arange(y0, y1)[:, None] + 0.5
    sobre_niple = nm[roi] * (yy <= y_furo)
    vis = np.clip((1 - a_foto) + sobre_niple, 0, 1)
    a_c = A * vis
    out = img.copy()
    top = out[roi]
    a_novo = a_c + top[..., 3] * (1 - a_c)
    rgb = (cor * a_c[..., None] + top[..., :3] * top[..., 3:] * (1 - a_c[..., None])) / np.maximum(a_novo, 1e-6)[..., None]
    out[roi] = np.concatenate([rgb, a_novo[..., None]], -1)
    return np.clip(out * 255 + 0.5, 0, 255).astype(np.uint8), (amb, k, tinta)
