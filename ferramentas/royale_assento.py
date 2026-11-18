# -*- coding: utf-8 -*-
"""Royale Lux 10288: assento em degrau e niple do Classique Lux na alça de barra chata, sem IA.

Thiago, 02/11/2026: "O Royale Lux tem uma alça barra chata igual à do Classique Lux" (22:48) e, no
niple do Classique da comparação, "Replique este niple no Royale Lux" (23:14). A foto dourada do
Royale (referencias/royale-lux/royale-lux-cabo-da-base.jpeg) e a still do Classique mostram o mesmo
desenho: a barra desce num degrau até um assento reto, e o niple fica em cima do assento.

Roda como o royale_alca.py (depois do pescoço, na foto centrada de 4379 px), com duas mudanças:
- Forma da barra perto do fundo: assento reto de 2 × ASSENTO_MEIO mm na altura do fundo do arco
  (em cima da borda do foguetinho), degrau de DEGRAU mm em DOBRA mm e o braço voltando ao arco do
  desenho 0007-AL em X_JUNTA mm do eixo. Medidas do próprio Royale, no vídeo
  referencias/videos/video-royale-lux.mp4 (14 s, de frente; coluna Ø19,05 = 36,7 px): assento ≈ 26 mm,
  degrau ≈ 3 mm em ≈ 4 mm, braço quase encostado na borda da cabeça. O Classique tem o mesmo desenho
  com degrau maior (≈ 4,6 mm), porque a cabeça dele fica mais alta sobre a alça.
  Daí para cima a barra é a mesma do royale_alca.py (os pixels não mudam).
  A superfície da barra é amostrada em 3D e projetada na câmera da still, com z-buffer; o cromado
  vem do Classique como no royale_alca.py (mesma face, mesma fração da largura, trecho do braço com a
  mesma inclinação na foto).
- Niple: o do Classique, em pixels reais, no mesmo acabamento e estado de LED, na escala 1,30
  (12,1 ÷ 9,3 px/mm), com a base no centro da face de cima do assento.
"""
import os
import sys
import warnings

import cv2
import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import royale_alca as ra  # noqa: E402

ASSENTO_MEIO = 13.0   # mm, metade do assento reto
DOBRA = 4.0           # mm em x para subir o degrau
DEGRAU = 3.0          # mm
X_JUNTA = 62.0        # mm do eixo: daqui para fora é o arco do desenho
INCL_DEGRAU = 0.15    # inclinação do braço logo depois do degrau
ESCALA_NIPLE = 1.30
# niple na still do Classique (4138 px): contorno e centro da base
NIPLE_POLI = np.array([(2003, 2913), (2001, 2886), (2010, 2876), (2025, 2873), (2115, 2873), (2128, 2876),
                       (2138, 2884), (2140, 2913)], float)
NIPLE_BASE = (2070.5, 2912.5)
ZONA = (1750, 2480, 2750, 2775)   # x0, y0, x1, y1 onde a forma nova pode aparecer


def _hermite(p0, m0, p1, m1, n):
    t = np.linspace(0, 1, n)[:, None]
    h00, h10, h01, h11 = 2 * t ** 3 - 3 * t ** 2 + 1, t ** 3 - 2 * t ** 2 + t, -2 * t ** 3 + 3 * t ** 2, t ** 3 - t ** 2
    dx = p1[0] - p0[0]
    P0, P1 = np.array(p0, float), np.array(p1, float)
    T0, T1 = np.array([1, m0]) * dx, np.array([1, m1]) * dx
    return h00 * P0 + h10 * T0 + h01 * P1 + h11 * T1


def linha_central():
    """Metade direita da linha de centro (x >= 0) no plano do U, do eixo até o arco: (x, y) em mm."""
    RC = ra.RC
    a, b = ASSENTO_MEIO, ASSENTO_MEIO + DOBRA
    y0 = -RC
    seat = np.stack([np.linspace(0, a, 300), np.full(300, y0)], -1)
    # a dobra é um S: sai do assento na horizontal, é íngreme no meio e chega na inclinação do braço
    dobra = _hermite((a, y0), 0.0, (b, y0 + DEGRAU), INCL_DEGRAU, 200)
    phi1 = np.arcsin(X_JUNTA / RC)
    p1 = (X_JUNTA, -RC * np.cos(phi1))
    braco = _hermite((b, y0 + DEGRAU), INCL_DEGRAU, p1, np.tan(phi1), 600)
    arco_phi = np.linspace(phi1, np.radians(75), 800)
    arco = np.stack([RC * np.sin(arco_phi), -RC * np.cos(arco_phi)], -1)
    pts = np.concatenate([seat, dobra[1:], braco[1:], arco[1:]])
    return pts


def curva_completa():
    """Linha de centro inteira (esquerda e direita) com o comprimento de arco sigma (mm, 0 no eixo)."""
    d = linha_central()
    pts = np.concatenate([d[::-1][:-1] * [-1, 1], d])
    seg = np.hypot(*np.diff(pts, axis=0).T)
    sig = np.r_[0, np.cumsum(seg)]
    sig -= np.interp(0.0, pts[:, 0], sig)
    tang = np.gradient(pts, sig, axis=0)
    tang /= np.linalg.norm(tang, axis=1)[:, None]
    nrm_in = np.stack([-tang[:, 1], tang[:, 0]], -1)          # normal para dentro do U (para o pivô)
    # garantir que aponta para o pivô no fundo
    if nrm_in[np.argmin(np.abs(pts[:, 0])), 1] < 0:
        nrm_in = -nrm_in
    return pts, sig, nrm_in


def s_equivalente(sig, pts):
    """Para cada ponto da curva nova, o s (mm) do arco do desenho com a mesma inclinação na foto,
    do mesmo lado: é o que o royale_alca usa para achar o trecho do Classique."""
    P3 = np.stack([pts[:, 0], pts[:, 1], np.zeros(len(pts))], -1)
    uv = ra.projetar(P3)
    du, dv = np.gradient(uv[:, 0], sig), np.gradient(uv[:, 1], sig)
    # mesma convenção do royale_alca.linha_classique: ângulo de (-du, -dv) no lado do pivô à vista
    ang = np.degrees(np.arctan2(-dv, -du))
    ang = np.where(ang < 0, ang + 360, ang)
    ss = np.linspace(0, ra.RC * np.pi / 2, 400)
    al = ss / ra.RC
    uvA = ra.projetar(np.stack([ra.RC * np.sin(al), -ra.RC * np.cos(al), 0 * al], -1))
    tR = np.degrees(np.unwrap(np.arctan2(-np.gradient(uvA[:, 1]), -np.gradient(uvA[:, 0]))))
    tR = np.where(tR < 0, tR + 360, tR)
    # lado esquerdo (sig < 0): a convenção do arco usa |s|; espelha o ângulo do lado esquerdo
    angL = np.degrees(np.arctan2(dv, du))
    angL = np.where(angL < 0, angL + 360, angL)
    uvL = ra.projetar(np.stack([-ra.RC * np.sin(al), -ra.RC * np.cos(al), 0 * al], -1))
    tL = np.degrees(np.unwrap(np.arctan2(np.gradient(uvL[:, 1]), np.gradient(uvL[:, 0]))))
    tL = np.where(tL < 0, tL + 360, tL)
    oR, oL = np.argsort(tR), np.argsort(tL)
    sR = np.interp(ang, tR[oR], ss[oR])
    sL = np.interp(angL, tL[oL], ss[oL])
    seq = np.where(sig >= 0, sR, -sL)
    # na dobra, a inclinação na foto é a de um trecho alto do braço (outro reflexo, escuro): ali o
    # cromado vai do assento ao começo do braço, em rampa
    a, b = ASSENTO_MEIO, ASSENTO_MEIO + DOBRA + 2.0
    ax = np.abs(pts[:, 0])
    for lado in (1, -1):
        m = (np.sign(sig) == lado) | (sig == 0)
        s_a = np.interp(a, ax[m][np.argsort(ax[m])], np.abs(seq[m])[np.argsort(ax[m])])
        s_b = np.interp(b, ax[m][np.argsort(ax[m])], np.abs(seq[m])[np.argsort(ax[m])])
        r = m & (ax > a) & (ax < b)
        seq[r] = lado * (s_a + (s_b - s_a) * (ax[r] - a) / (b - a))
    return seq


def amostrar_superficie(dens=40.0):
    """Pontos 3D das quatro faces da barra nova no trecho |x| <= X_JUNTA + 8, com face, sigma, s
    equivalente e coordenada de través (como no royale_alca.tracar)."""
    pts, sig, nin = curva_completa()
    m = np.abs(pts[:, 0]) <= X_JUNTA + 8
    pts, sig, nin = pts[m], sig[m], nin[m]
    seq = s_equivalente(sig, pts)
    # reamostra uniformemente em sigma
    n = int((sig[-1] - sig[0]) * dens)
    S = np.linspace(sig[0], sig[-1], n)
    X = np.interp(S, sig, pts[:, 0]); Y = np.interp(S, sig, pts[:, 1])
    NX = np.interp(S, sig, nin[:, 0]); NY = np.interp(S, sig, nin[:, 1])
    SEQ = np.interp(S, sig, seq)
    h = (ra.RO - ra.RI) / 2
    out = []
    nz = int(2 * ra.MEIA * dens)
    zs = np.linspace(-ra.MEIA, ra.MEIA, nz)
    for face, off in ((ra.F_INT, +h), (ra.F_EXT, -h)):
        px = (X + NX * off)[:, None] + 0 * zs[None]
        py = (Y + NY * off)[:, None] + 0 * zs[None]
        pz = 0 * X[:, None] + zs[None]
        out.append((face, px, py, pz, np.broadcast_to(S[:, None], px.shape), np.broadcast_to(SEQ[:, None], px.shape),
                    np.broadcast_to(zs[None], px.shape)))
    nu = max(int(2 * h * dens * 2), 8)
    us = np.linspace(-h, h, nu)              # + para dentro
    for face, z in ((ra.F_FRENTE, ra.MEIA), (ra.F_TRAS, -ra.MEIA)):
        px = X[:, None] + NX[:, None] * us[None]
        py = Y[:, None] + NY[:, None] * us[None]
        pz = np.full(px.shape, z)
        r = ra.RC - us[None] + 0 * X[:, None]   # "raio" equivalente: RI por dentro, RO por fora
        out.append((face, px, py, pz, np.broadcast_to(S[:, None], px.shape), np.broadcast_to(SEQ[:, None], px.shape), r))
    return out


def geometria_nova():
    """F, S (s equivalente, para a cor), A e SIG (sigma real) nas subamostras da ZONA, por z-buffer."""
    x0, y0, x1, y1 = ZONA
    SS = ra.SS
    Hs, Ws = (y1 - y0) * SS, (x1 - x0) * SS
    prof = np.full(Hs * Ws, np.inf)
    F = np.zeros(Hs * Ws, np.int8); S = np.zeros(Hs * Ws, np.float32); A = np.zeros(Hs * Ws, np.float32)
    SIG = np.zeros(Hs * Ws, np.float32)
    c, s = np.cos(ra.PSI), np.sin(ra.PSI)
    for face, px, py, pz, S_, SEQ, atr in amostrar_superficie():
        P = np.stack([px.ravel(), py.ravel(), pz.ravel()], -1)
        uv = ra.projetar(P)
        Z = P[:, 0] * s + P[:, 2] * c
        d = ra.DIST - Z                     # distância à câmera ao longo do eixo óptico
        iu = np.floor((uv[:, 0] - x0) * SS).astype(int)
        iv = np.floor((uv[:, 1] - y0) * SS).astype(int)
        ok = (iu >= 0) & (iu < Ws) & (iv >= 0) & (iv < Hs)
        idx = iv[ok] * Ws + iu[ok]
        dd = d[ok]
        ordem = np.argsort(-dd)             # mais longe primeiro; o mais perto escreve por último
        idx, dd = idx[ordem], dd[ordem]
        sel = np.nonzero(ok)[0][ordem]
        perto = dd < prof[idx]
        # dentro do mesmo lote, a última escrita (mais perto) vence
        idx, sel, dd = idx[perto], sel[perto], dd[perto]
        prof[idx] = dd
        F[idx] = face
        S[idx] = SEQ.ravel()[sel]
        A[idx] = atr.ravel()[sel]
        SIG[idx] = S_.ravel()[sel]
    return (F.reshape(Hs, Ws), S.reshape(Hs, Ws), A.reshape(Hs, Ws), SIG.reshape(Hs, Ws))


# a CAIXA do royale_alca acaba em 2760; o assento visto de cima desce um pouco mais
ra.CAIXA = ra.CAIXA[:3] + (max(ra.CAIXA[3], ZONA[3]),)
_GEO = None
_GEO_RA = ra.geometria   # a original, antes da troca em trocar_alca


def geometria():
    """A do royale_alca na CAIXA, com o trecho do fundo trocado pela forma com assento."""
    global _GEO
    if _GEO is None:
        F, S, A = (v.copy() for v in _GEO_RA())
        Fn, Sn, An, SIGn = geometria_nova()
        cx0, cy0 = ra.CAIXA[:2]
        x0, y0, x1, y1 = ZONA
        SS = ra.SS
        r0, c0 = (y0 - cy0) * SS, (x0 - cx0) * SS
        sl = (slice(r0, r0 + Fn.shape[0]), slice(c0, c0 + Fn.shape[1]))
        # no trecho do fundo (arco com |x| < X_JUNTA + 8), vale só a forma nova
        s_lim = ra.RC * np.arcsin((X_JUNTA + 6) / ra.RC)
        Fo, So = F[sl], S[sl]
        velho_fundo = (Fo > 0) & (np.abs(So) < s_lim)
        Fo[velho_fundo] = 0
        novo = (Fn > 0) & ((Fo == 0) | (np.abs(SIGn) < s_lim))
        Fo[novo] = Fn[novo]
        So[novo] = Sn[novo]
        A[sl][novo] = An[novo]
        F[sl], S[sl] = Fo, So
        _GEO = (F, S, A)
    return _GEO


def niple_classique(classique):
    """Recorte RGBA do niple do Classique (float 0-1), na escala da still do Royale, e a posição da base."""
    x0, y0 = int(NIPLE_POLI[:, 0].min()) - 3, int(NIPLE_POLI[:, 1].min()) - 3
    x1, y1 = int(NIPLE_POLI[:, 0].max()) + 4, int(NIPLE_POLI[:, 1].max()) + 2
    rec = classique[y0:y1, x0:x1].astype(np.float32) / 255
    k = 8
    m = np.zeros(((y1 - y0) * k, (x1 - x0) * k), np.uint8)
    cv2.fillPoly(m, [np.round((NIPLE_POLI - [x0, y0]) * k).astype(np.int32)], 255)
    m = cv2.resize(m, (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    rgb = rec[..., :3]
    E = ESCALA_NIPLE
    W2, H2 = int(round((x1 - x0) * E)), int(round((y1 - y0) * E))
    rgb2 = cv2.resize(rgb, (W2, H2), interpolation=cv2.INTER_LANCZOS4)
    m2 = cv2.resize(m * rec[..., 3], (W2, H2), interpolation=cv2.INTER_LINEAR)
    base = ((NIPLE_BASE[0] - x0) * E, (NIPLE_BASE[1] - y0) * E)
    return np.clip(rgb2, 0, 1), np.clip(m2, 0, 1), base


def posicao_base_niple():
    """Onde fica, na foto, o ponto mais baixo da base do niple (Ø14,5) sobre a face de cima do assento."""
    t = np.linspace(0, 2 * np.pi, 720)
    P = np.stack([7.25 * np.cos(t), np.full_like(t, -ra.RI), 7.25 * np.sin(t)], -1)
    uv = ra.projetar(P)
    i = np.argmax(uv[:, 1])
    centro = ra.projetar(np.array([0.0, -ra.RI, 0.0]))
    return centro[0], uv[i, 1]


def trocar_alca(tela, classique):
    """Como royale_alca.trocar_alca, com a forma nova do fundo e o niple do Classique."""
    ra_geo = ra.geometria
    ra.geometria = geometria
    try:
        if tela.shape[:2] != (ra.LADO, ra.LADO):
            raise SystemExit("a foto do Royale devia ter %d px (depois do pescoço)" % ra.LADO)
        roy = tela.astype(np.float32) / 255
        x0, y0, x1, y1 = ra.CAIXA
        cob_c, rgb_c, s_c = ra.barra(classique.astype(np.float32))
        H, W = roy.shape[:2]
        cob = np.zeros((H, W), np.float32); cob[y0:y1, x0:x1] = cob_c
        rgb = np.zeros((H, W, 3), np.float32); rgb[y0:y1, x0:x1] = rgb_c / 255
        sp = np.full((H, W), -999, np.float32); sp[y0:y1, x0:x1] = np.nan_to_num(s_c, nan=-999)
        Y, X = np.mgrid[0:H, 0:W]
        alfa = roy[..., 3]
        zona = (X >= x0) & (X < x1) & (Y >= y0) & (Y < ra.Y_COLUNA)
        botao = ra._botao(X, Y)
        B = ra.B
        yB = np.interp(X, B[:, 0], B[:, 1])
        abaixoB = (X >= B[0, 0]) & (X <= B[-1, 0]) & (Y > yB)
        linhaB = (X >= B[0, 0]) & (X <= B[-1, 0]) & (np.abs(Y - yB) < 1.5)
        pegada = cv2.dilate((cob > 0).astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
        s = cv2.dilate(sp, np.ones((7, 7), np.uint8))
        frente = pegada & (s > ra.S_FRENTE)
        tras = pegada & ~frente
        Acab = (alfa > 0) & zona & ~frente & ~botao & ~abaixoB & ~linhaB
        _, lab = cv2.connectedComponents(Acab.astype(np.uint8), connectivity=4)
        cab = lab == lab[1400, 2100]
        base = roy.copy()
        base[(alfa > 0) & zona & ~frente & ~botao & ~cab] = 0
        cx = np.full(H, np.nan)
        for yy in range(y0, y1):
            xs = np.nonzero(frente[yy] & (cob[yy] > 0.5))[0]
            if len(xs):
                cx[yy] = (xs[0] + xs[-1]) / 2
        with np.errstate(invalid="ignore"):
            base[frente & (X > cx[:, None]) & ~botao] = 0
        out = ra._sobre(rgb, cob, base)
        # niple do Classique sobre o assento
        nrgb, na, nb = niple_classique(classique)
        bx, by = posicao_base_niple()
        ox, oy = bx - nb[0], by - nb[1]
        ix, iy = int(np.floor(ox)), int(np.floor(oy))
        fx, fy = ox - ix, oy - iy
        M = np.float32([[1, 0, fx], [0, 1, fy]])
        h2, w2 = na.shape
        nrgb = cv2.warpAffine(nrgb, M, (w2 + 1, h2 + 1), flags=cv2.INTER_LINEAR)
        na = cv2.warpAffine(na, M, (w2 + 1, h2 + 1), flags=cv2.INTER_LINEAR)
        sl = (slice(iy, iy + h2 + 1), slice(ix, ix + w2 + 1))
        out[sl] = ra._sobre(nrgb, na, out[sl])
        for m in (tras & cab, botao & (alfa > 0)):
            out[m] = ra._sobre(roy[m][None, :, :3], roy[m][None, :, 3], out[m][None])[0]
        return np.clip(out * 255 + 0.5, 0, 255).astype(np.uint8)
    finally:
        ra.geometria = ra_geo
