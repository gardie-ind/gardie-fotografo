# -*- coding: utf-8 -*-
"""Logo a laser numa foto ambientada, sem IA (retoque g de guia/criterios.md).

O Gemini erra o logo dos LUX em cerca de metade das ambientadas: some, ou sai
com outra grafia ("garom", "garas"). Este script apaga o logo errado (se
houver) e grava o logo do desenho E-0001-V1 na posição real, pela mesma
geometria do `logo_laser.py`:

- a área espelhada é o furo do anel de luz (elipse interna); a escala vem do
  Ø do vidro do catálogo igualado ao eixo maior do anel (elipse externa);
- logo de 20 mm, topo a 8,71 mm da borda de baixo da área espelhada,
  centrado; a linha de base do logo fica horizontal na foto, e o "embaixo"
  do logo segue o diâmetro conjugado da elipse;
- ligado: cor do anel logo abaixo do logo, com o halo de 0,25 mm; desligado:
  cor do difusor apagado, sem halo;
- o logo errado sai por membrana (Laplace) a partir da borda dos traços, que
  segue as faixas do reflexo e a faixa da borda do vidro sem trazer luz de
  longe.

As elipses saem do anel aceso: com --centro e --rmax, por raios (borda interna =
maior subida de luz, externa = maior descida depois dela, ajuste robusto); ou
dentro de --caixa (pixels mais claros que o limiar, maior componente com furo).
Confira sempre a imagem de --conferir; se a elipse sair errada, passe
--interna e --externa à mão.

Uso:
  python3 logo_ambiente.py foto.png saida.png --vidro 203 --estado ligado
      (--centro cx,cy --rmax r | --caixa x0,y0,x1,y1 [--limiar 238]) [--apagar x0,y0,x1,y1]
      [--interna cx,cy,a,b,ang] [--externa cx,cy,a,b,ang] [--conferir conf.jpg]

Grava saida.png e saida.json (elipses, mm/px, cor e posição do logo).
"""
import argparse
import json
import os
import sys

import cv2
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from logo_laser import LOGO, LOGO_MM, LARG, ALT, TOPO, HALO, HALO_MM  # noqa: E402
from luz_anel import lin, srgb  # noqa: E402


def ajusta(mask):
    cs, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    (x, y), (d1, d2), ang = cv2.fitEllipse(max(cs, key=len))
    return [float(x), float(y), d1 / 2, d2 / 2, float(ang)]


def elipses_do_anel(Y, caixa, limiar):
    x0, y0, x1, y1 = caixa
    sub = Y[y0:y1, x0:x1] > limiar
    sub = ndi.binary_opening(sub, iterations=2)
    lab, n = ndi.label(sub)
    melhor = None
    for i in range(1, n + 1):
        c = lab == i
        furo = ndi.binary_fill_holes(c) & ~c
        if furo.sum() > (melhor[0] if melhor else 0):
            melhor = (furo.sum(), c, furo)
    if melhor is None or melhor[0] < 1000:
        raise SystemExit("Não achei anel aceso com furo na caixa; passe --interna e --externa.")
    _, anel, furo = melhor
    lf, _ = ndi.label(furo)
    furo = lf == np.argmax(np.bincount(lf.ravel())[1:]) + 1
    furo = ndi.binary_fill_holes(furo)
    cheio = ndi.binary_fill_holes(anel | furo)
    ei, eo = ajusta(furo), ajusta(cheio)
    ei[0] += x0; ei[1] += y0; eo[0] += x0; eo[1] += y0
    return ei, eo


def ajuste_robusto(pts, voltas=4, tol=3.0):
    pts = np.asarray(pts, np.float32)
    for _ in range(voltas):
        (x, y), (d1, d2), ang = cv2.fitEllipse(pts)
        e = [float(x), float(y), d1 / 2, d2 / 2, float(ang)]
        # distância aproximada: |r_ponto - r_elipse| na direção do ponto
        t = np.deg2rad(ang)
        dx, dy = pts[:, 0] - x, pts[:, 1] - y
        u = dx * np.cos(t) + dy * np.sin(t); v = -dx * np.sin(t) + dy * np.cos(t)
        r = np.hypot(u, v); th = np.arctan2(v, u)
        re = 1 / np.sqrt((np.cos(th) / e[2]) ** 2 + (np.sin(th) / e[3]) ** 2)
        res = np.abs(r - re)
        lim = max(tol, 2.5 * np.median(res))
        if (res <= lim).all() or (res <= lim).sum() < 20:
            break
        pts = pts[res <= lim]
    return e, len(pts)


def elipses_por_raios(Y, centro, rmax, n=180):
    """Anel aceso por raios: do centro para fora, a borda interna é a maior subida
    de luz e a externa, a maior descida depois dela."""
    Ys = ndi.gaussian_filter(Y, 1.5)
    cx, cy = centro
    rs = np.arange(5, rmax)
    pin, pout = [], []
    for t in np.linspace(0, 2 * np.pi, n, endpoint=False):
        xs = cx + rs * np.cos(t); ys = cy + rs * np.sin(t)
        ok = (xs >= 0) & (ys >= 0) & (xs < Y.shape[1] - 1) & (ys < Y.shape[0] - 1)
        if ok.sum() < 30:
            continue
        perf = ndi.map_coordinates(Ys, [ys[ok], xs[ok]], order=1)
        d = np.gradient(perf)
        i = int(np.argmax(d))
        if d[i] < 4 or i >= len(d) - 3:
            continue
        j = i + 2 + int(np.argmin(d[i + 2:]))
        if d[j] > -4:
            continue
        pin.append((xs[ok][i], ys[ok][i])); pout.append((xs[ok][j], ys[ok][j]))
    if len(pin) < 30:
        raise SystemExit("Poucos raios com anel; passe --interna e --externa.")
    ei, ni = ajuste_robusto(pin); eo, no = ajuste_robusto(pout)
    return ei, eo, (ni, no, len(pin))


def apagar_tangencial(R, msk, e):
    """Preenche a máscara ao longo das elipses concêntricas à área espelhada: perto
    da borda o vidro muda com a distância à borda (faixa escura do chanfro, luz do
    anel) e quase não muda ao longo dela. Interpola cada "anel" de raio
    normalizado entre os pixels fora da máscara dos dois lados; depois devolve o
    grão da vizinhança."""
    ys, xs = np.nonzero(msk)
    if not len(ys):
        return R
    t = np.deg2rad(e[4]); a, b = e[2], e[3]
    def polar(x, y):
        dx, dy = x - e[0], y - e[1]
        u = dx * np.cos(t) + dy * np.sin(t); v = -dx * np.sin(t) + dy * np.cos(t)
        return np.hypot(u / a, v / b), np.arctan2(v / b, u / a)
    rho, th = polar(xs.astype(np.float32), ys.astype(np.float32))
    ref = th.mean()
    th = np.angle(np.exp(1j * (th - ref)))
    r0, r1 = rho.min() - 0.01, rho.max() + 0.01
    t0, t1 = th.min() - 0.06, th.max() + 0.06
    nr = int(np.ceil((r1 - r0) * max(a, b) * 2)) + 2
    nt = int(np.ceil((t1 - t0) * max(a, b) * 2)) + 2
    RR, TT = np.meshgrid(np.linspace(r0, r1, nr), np.linspace(t0, t1, nt), indexing='ij')
    uu = RR * a * np.cos(TT + ref); vv = RR * b * np.sin(TT + ref)
    gx = e[0] + uu * np.cos(t) - vv * np.sin(t); gy = e[1] + uu * np.sin(t) + vv * np.cos(t)
    F = R.astype(np.float32)
    G = np.stack([ndi.map_coordinates(F[..., c], [gy, gx], order=1) for c in range(3)], -1)
    Gm = ndi.map_coordinates(msk.astype(np.float32), [gy, gx], order=1) > 0.01
    tt = np.linspace(t0, t1, nt)
    for i in range(nr):
        ok = ~Gm[i]
        if ok.sum() >= 2 and Gm[i].any():
            for c in range(3):
                G[i, Gm[i], c] = np.interp(tt[Gm[i]], tt[ok], G[i, ok, c])
    ri = (rho - r0) / (r1 - r0) * (nr - 1); ti = (th - t0) / (t1 - t0) * (nt - 1)
    out = F.copy()
    for c in range(3):
        out[ys, xs, c] = ndi.map_coordinates(G[..., c], [ri, ti], order=1)
    viz = ndi.binary_dilation(msk, iterations=12) & ~ndi.binary_dilation(msk, iterations=3)
    hp = F - np.stack([ndi.gaussian_filter(F[..., c], 1.2) for c in range(3)], -1)
    sd = 1.4826 * np.median(np.abs(hp[viz]), 0) * 1.6
    out[ys, xs] += np.random.default_rng(7).normal(0, 1, (len(ys), 1)) * sd
    return np.clip(out + 0.5, 0, 255).astype(np.uint8)


def apagar_harmonico(R, msk, voltas=3000):
    """Preenche a máscara pela membrana (Laplace) a partir da borda dela: num traço
    fino, segue tanto as faixas do reflexo quanto a faixa da borda do vidro, sem
    trazer luz de longe. Depois devolve o grão da vizinhança."""
    ys, xs = np.nonzero(msk)
    if not len(ys):
        return R
    y0, y1 = max(ys.min() - 2, 0), ys.max() + 3
    x0, x1 = max(xs.min() - 2, 0), xs.max() + 3
    F = R.astype(np.float32)
    sub = F[y0:y1, x0:x1].copy(); m = msk[y0:y1, x0:x1]
    sub[m] = sub[~m].mean(0)
    for _ in range(voltas):
        v = 0.25 * (np.roll(sub, 1, 0) + np.roll(sub, -1, 0) + np.roll(sub, 1, 1) + np.roll(sub, -1, 1))
        sub[m] = v[m]
    out = F.copy(); out[y0:y1, x0:x1] = sub
    viz = ndi.binary_dilation(msk, iterations=12) & ~ndi.binary_dilation(msk, iterations=3)
    hp = F - np.stack([ndi.gaussian_filter(F[..., c], 1.2) for c in range(3)], -1)
    sd = 1.4826 * np.median(np.abs(hp[viz]), 0) * 1.6
    out[ys, xs] += np.random.default_rng(7).normal(0, 1, (len(ys), 1)) * sd
    return np.clip(out + 0.5, 0, 255).astype(np.uint8)


def mascara_elipse(shape, e, escala=1.0):
    m = np.zeros(shape, np.uint8)
    cv2.ellipse(m, ((e[0], e[1]), (2 * e[2] * escala, 2 * e[3] * escala), e[4]), 1, -1)
    return m.astype(bool)


def principal(foto, saida, vidro_mm, estado, caixa=None, limiar=238, apagar_caixa=None,
              interna=None, externa=None, conferir=None, centro=None, rmax=None, margem=0.985):
    im = Image.open(foto).convert('RGB')
    R = np.asarray(im).copy()
    Y = R.astype(np.float32).mean(-1)
    raios = None
    if centro and (interna is None or externa is None):
        ei, eo, raios = elipses_por_raios(Y, centro, rmax)
        interna = interna or ei
        externa = externa or eo
    if interna is None or externa is None:
        ei, eo = elipses_do_anel(Y, caixa, limiar)
        interna = interna or ei
        externa = externa or eo
    C = np.array(interna[:2]); a, b = interna[2], interna[3]; phi = np.deg2rad(interna[4])
    mm_px = vidro_mm / (2 * max(externa[2], externa[3]))
    # 1. apaga o logo errado: traços que destoam da mediana local, dentro da caixa
    msk = np.zeros(Y.shape, bool)
    if apagar_caixa:
        x0, y0, x1, y1 = apagar_caixa
        Yc = Y[y0:y1, x0:x1]
        d = Yc - ndi.median_filter(Yc, 15)
        # aceso, o logo errado é mais claro que o vidro; apagado, mais escuro
        dev = d > 3 if estado == "ligado" else d < -3
        dentro = mascara_elipse(Y.shape, interna, margem)[y0:y1, x0:x1]
        msk[y0:y1, x0:x1] = ndi.binary_dilation(dev & dentro, iterations=3) & dentro
        R = apagar_harmonico(R, msk)
    # 2. moldura: círculo unitário -> elipse da área espelhada. A linha de base do
    # logo fica horizontal na foto; o "embaixo" do logo é o diâmetro conjugado
    # (num círculo em perspectiva, diâmetros perpendiculares viram conjugados)
    Rot = lambda t: np.array([[np.cos(t), -np.sin(t)], [np.sin(t), np.cos(t)]])
    M0 = Rot(phi) @ np.diag([a, b])
    q = np.linalg.solve(M0, np.array([1.0, 0.0]))
    psi = np.arctan2(q[1], q[0])
    M = M0 @ Rot(psi)               # det > 0: o eixo y do logo sai para baixo
    Rmm = max(a, b) * mm_px
    yc = (Rmm - (TOPO - ALT / 2)) / Rmm
    lg = np.asarray(Image.open(LOGO)).astype(np.float32) / 255
    h, w = lg.shape
    S = 4
    A_log = np.array([[LOGO_MM / Rmm, 0, -w / 2 * LOGO_MM / Rmm],
                      [0, LOGO_MM / Rmm, yc - h / 2 * LOGO_MM / Rmm]])
    A_img = np.c_[M, C]
    A = np.c_[A_img[:, :2] @ A_log[:, :2], A_img[:, :2] @ A_log[:, 2] + A_img[:, 2]]
    cant = A @ np.array([[0, w, 0, w], [0, 0, h, h], [1, 1, 1, 1]])
    bx0, by0 = np.floor(cant.min(1)).astype(int) - 4
    bx1, by1 = np.ceil(cant.max(1)).astype(int) + 4
    Wb, Hb = bx1 - bx0, by1 - by0
    Ash = A.copy(); Ash[:, 2] -= [bx0, by0]; Ash *= S
    f = np.linalg.norm(Ash[:, :2], axis=0).mean()
    pre = cv2.resize(lg, (max(int(w * f * 2), 1), max(int(h * f * 2), 1)), interpolation=cv2.INTER_AREA)
    Ap = Ash.copy(); Ap[:, 0] *= w / pre.shape[1]; Ap[:, 1] *= h / pre.shape[0]
    alfa = cv2.warpAffine(pre, Ap, (Wb * S, Hb * S), flags=cv2.INTER_LINEAR, borderValue=0)
    alfa = cv2.resize(alfa, (Wb, Hb), interpolation=cv2.INTER_AREA)
    # 3. cor: anel (difusor) logo abaixo da borda de baixo da área espelhada
    # (no meio do anel; se a foto corta o anel embaixo, abre o leque de ângulos)
    anel = mascara_elipse(Y.shape, externa, 0.97) & ~mascara_elipse(Y.shape, interna, 1.03)
    meio = (1 + max(externa[2], externa[3]) / max(a, b)) / 2
    for leque in (0.15, 0.4, 0.8, 1.4):
        amost = np.zeros(Y.shape, bool)
        for t in np.linspace(-leque, leque, 61):
            pr = C + M @ (Rot(t) @ np.array([0, 1.0]) * meio)
            yy, xx = int(round(pr[1])), int(round(pr[0]))
            if 4 <= yy < Y.shape[0] - 4 and 4 <= xx < Y.shape[1] - 4:
                amost[yy - 4:yy + 5, xx - 4:xx + 5] = True
        amost &= anel
        if amost.sum() >= 200:
            break
    L = lin(R.astype(np.float32) / 255)
    cor = np.median(L[amost], 0)
    sl = (slice(by0, by1), slice(bx0, bx1))
    al = alfa[..., None]
    L[sl] = L[sl] * (1 - al) + al * cor
    if estado == 'ligado' and HALO > 0:
        hal = ndi.gaussian_filter(alfa, HALO_MM / mm_px)
        hal = hal / max(hal.max(), 1e-6) * HALO
        L[sl] = L[sl] + (hal * (1 - alfa))[..., None] * cor
    out = (np.clip(srgb(L), 0, 1) * 255 + 0.5).astype(np.uint8)
    Image.fromarray(out).save(saida)
    centro = A @ np.array([w / 2, h / 2, 1])
    info = dict(interna=[round(v, 2) for v in interna], externa=[round(v, 2) for v in externa],
                mm_px=round(mm_px, 5), raio_espelhado_mm=round(Rmm, 2), psi=round(float(np.rad2deg(psi)), 2),
                logo_centro=centro.round(1).tolist(), logo_largura_px=round(LARG / mm_px, 1),
                cor=(srgb(cor) * 255).round().tolist(), apagado_px=int(msk.sum()), estado=estado,
                raios_usados=raios)
    json.dump(info, open(os.path.splitext(saida)[0] + '.json', 'w'), indent=1)
    if conferir:
        r = int(LARG / mm_px * 1.4); cx, cy = int(centro[0]), int(centro[1])
        bx = (slice(max(cy - r, 0), cy + r), slice(max(cx - r, 0), cx + r))
        antes = np.asarray(im)[bx]; depois = out[bx]
        g = np.concatenate([antes, depois], 1)
        g = Image.fromarray(g).resize((g.shape[1] * 3, g.shape[0] * 3), Image.LANCZOS)
        vis = np.asarray(im).copy()
        cv2.ellipse(vis, ((interna[0], interna[1]), (2 * interna[2], 2 * interna[3]), interna[4]), (255, 0, 0), 2)
        cv2.ellipse(vis, ((externa[0], externa[1]), (2 * externa[2], 2 * externa[3]), externa[4]), (0, 160, 255), 2)
        x0 = int(max(externa[0] - externa[3] * 1.15, 0)); x1 = int(externa[0] + externa[3] * 1.15)
        y0 = int(max(externa[1] - externa[3] * 1.15, 0)); y1 = int(externa[1] + externa[3] * 1.15)
        v = Image.fromarray(vis[y0:y1, x0:x1]); v.thumbnail((g.size[1], g.size[1]))
        c = Image.new('RGB', (g.size[0] + v.size[0] + 10, g.size[1]), 'white')
        c.paste(g, (0, 0)); c.paste(v, (g.size[0] + 10, 0)); c.save(conferir, quality=90)
    print(json.dumps(info))
    return info


def main():
    p = argparse.ArgumentParser()
    p.add_argument('foto'); p.add_argument('saida')
    p.add_argument('--vidro', type=float, required=True, help='Ø do vidro do catálogo em mm (Classique, Visage, Flex 203; Royale, Mobile 152)')
    p.add_argument('--estado', choices=['ligado', 'desligado'], required=True)
    p.add_argument('--caixa'); p.add_argument('--limiar', type=float, default=238)
    p.add_argument('--apagar'); p.add_argument('--interna'); p.add_argument('--externa')
    p.add_argument('--conferir')
    p.add_argument('--centro', help='cx,cy aproximado da cabeça: acha o anel por raios')
    p.add_argument('--rmax', type=int, help='raio máximo dos raios (px), um pouco além do aro')
    p.add_argument('--margem', type=float, default=0.985, help='só apaga dentro da elipse interna × margem (1.0 quando o logo errado encosta na borda)')
    a = p.parse_args()
    t = lambda s: [float(v) for v in s.split(',')] if s else None
    ti = lambda s: [int(v) for v in s.split(',')] if s else None
    principal(a.foto, a.saida, a.vidro, a.estado, ti(a.caixa), a.limiar, ti(a.apagar), t(a.interna), t(a.externa), a.conferir,
              t(a.centro), a.rmax, a.margem)


if __name__ == '__main__':
    main()
