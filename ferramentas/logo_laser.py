"""Logo a laser nos LUX (pedido do Thiago em 22/10/2026, 19:08: "Só a logomarca
da Gardie no espelho e não na borda jateada. Ele brilha na cor do anel fosco de
luz.").

1. Tira o logo impresso da borda jateada, nas fotos ligada e apagada. Os
   traços são achados onde a foto ligada fica mais escura que a apagada, mais
   o contorno deles; o buraco é preenchido pela vizinhança (convolução
   normalizada) e recebe o grão da foto.
2. Grava o logo do desenho E-0001-V1 no espelho: 20 mm de largura, topo a
   8,71 mm da borda de baixo da área espelhada, centrado. A borda espelhada é a
   elipse interna da borda jateada, medida na luz do LED. O "embaixo" do
   produto é a direção do logo impresso. A escala vem do Ø do vidro do
   catálogo, igualado ao Ø externo da borda jateada visível.
3. O logo gravado tem a cor da borda jateada no mesmo estado: claro na ligada
   (entra na luz do LED, então o padrão de luz dá a ele o tom do anel) e cinza
   escuro na apagada. O logo aceso ganha um halo (HALO, padrão 0,6, raio de
   0,25 mm): sem ele, o logo some contra o vidro claro do estúdio.

uso: python3 logo_laser.py <ligada> <apagada> <Ø vidro mm> <saida ligada> <saida apagada> [debug.jpg]"""
import sys, json
import os
import numpy as np, cv2
from PIL import Image
from scipy import ndimage as ndi
from luz_anel import lin, srgb, YW

LOGO = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logo-laser', 'logo-laser-frente-0.003528mm.png')
LOGO_MM = 0.003528
LARG, ALT, TOPO = 20.0, 2.98, 8.71
BRILHO_LOGO = 1.0            # logo aceso em relação à borda jateada ao lado
HALO = float(os.environ.get('HALO', '0.6'))   # brilho em volta dos traços acesos (0 = sem), fração da cor do logo
HALO_MM = 0.25               # raio do halo em mm


def abrir(p):
    im = Image.open(p); a = np.asarray(im.convert('RGBA'))
    return im, a[..., :3].copy(), a[..., 3].copy()


def apagar(R, msk, sig=6):
    """Preenche a máscara pela vizinhança (convolução normalizada, várias passadas) e devolve o grão da foto."""
    F = R.astype(np.float32); w = (~msk).astype(np.float32)
    out = F.copy()
    for s_ in (sig, sig * 2, sig * 4):
        num = np.stack([ndi.gaussian_filter(F[..., c] * w, s_) for c in range(3)], -1)
        den = ndi.gaussian_filter(w, s_)[..., None]
        fill = num / np.maximum(den, 1e-6)
        sel = msk & (den[..., 0] > 0.05) & (out == F).all(-1) if s_ == sig else msk & (den[..., 0] > 0.05)
        out[msk] = np.where((den[msk] > 0.05), fill[msk], out[msk])
        if (den[msk] > 0.05).all(): break
    viz = ndi.binary_dilation(msk, iterations=15) & ~ndi.binary_dilation(msk, iterations=3)
    hp = F - np.stack([ndi.gaussian_filter(F[..., c], 1.2) for c in range(3)], -1)
    sd = 1.4826 * np.median(np.abs(hp[viz]), 0) * 1.6
    rng = np.random.default_rng(7)
    out[msk] += rng.normal(0, 1, (int(msk.sum()), 1)) * sd
    return np.clip(out + 0.5, 0, 255).astype(np.uint8)


def elipse(mask):
    cs, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    (x, y), (d1, d2), ang = cv2.fitEllipse(max(cs, key=len))
    return np.array([x, y]), d1 / 2, d2 / 2, np.deg2rad(ang)


def principal(lig, apa, vidro_mm, s_lig, s_apa, dbg=None):
    im1, R1, A1 = abrir(lig); im2, R2, A2 = abrir(apa)
    L1 = lin(R1.astype(np.float32) / 255); L2 = lin(R2.astype(np.float32) / 255)
    YE = np.clip(L1 - L2 - 0.004, 0, None) @ YW.astype(np.float32)
    nivel = np.percentile(YE[YE > 0.3], 50)
    anel = ndi.binary_opening(YE > 0.5 * nivel, iterations=2)
    lab, _ = ndi.label(anel); anel = lab == np.argmax(np.bincount(lab.ravel())[1:]) + 1
    cheio = ndi.binary_fill_holes(anel)
    fur, _ = ndi.label(cheio & ~anel); vidro = fur == np.argmax(np.bincount(fur.ravel())[1:]) + 1
    C, a, b, phi = elipse(vidro)            # borda da área espelhada
    _, ao, bo, _ = elipse(cheio)            # borda externa visível da borda jateada
    mm_px = vidro_mm / (2 * max(ao, bo))
    # logo impresso: traços mais escuros com o LED ligado
    neg = (L2 - L1).max(-1) > 0.03
    lb, _ = ndi.label(ndi.binary_dilation(neg, iterations=6))
    cnt = np.bincount(lb.ravel()); cnt[0] = 0
    imp = neg & (lb == np.argmax(cnt))
    pimp = np.array(np.where(imp)[::-1], dtype=float).mean(1)
    # 1. apaga o logo impresso: máscara = traços + halo (desvio da versão suavizada, nas duas fotos)
    ys_, xs_ = np.where(imp); bx = (slice(max(ys_.min() - 20, 0), ys_.max() + 21), slice(max(xs_.min() - 20, 0), xs_.max() + 21))
    dev = np.zeros(imp.shape, bool)
    for L in (L1, L2):
        Y = L[bx] @ YW.astype(np.float32)
        dev[bx] |= np.abs(Y - ndi.median_filter(Y, 15)) > 0.006
    msk = ndi.binary_dilation(ndi.binary_dilation(imp, iterations=2) | (dev & ndi.binary_dilation(imp, iterations=8)), iterations=2)
    m = msk.astype(np.uint8) * 255
    R1i = apagar(R1, msk); R2i = apagar(R2, msk)
    # 2. moldura do produto: círculo da área espelhada -> elipse da foto
    Rot = lambda t: np.array([[np.cos(t), -np.sin(t)], [np.sin(t), np.cos(t)]])
    M0 = Rot(phi) @ np.diag([a, b])          # círculo unitário -> elipse (sem a rotação do produto)
    q = np.linalg.solve(M0, pimp - C)        # direção do logo impresso no círculo unitário
    psi = np.arctan2(q[1], q[0]) - np.pi / 2  # "embaixo" do produto = +90° (y para baixo)
    M = M0 @ Rot(psi)
    Rmm = max(a, b) * mm_px                  # raio da área espelhada em mm
    y0 = (Rmm - (TOPO - ALT / 2)) / Rmm      # centro do logo, em raios, abaixo do centro
    # mapa: pixel do logo (alta resolução) -> pixel da foto
    lg = np.asarray(Image.open(LOGO)).astype(np.float32) / 255
    h, w = lg.shape
    S = 4                                    # supersample
    A_log = np.array([[LOGO_MM / Rmm, 0, -w / 2 * LOGO_MM / Rmm],
                      [0, LOGO_MM / Rmm, y0 - h / 2 * LOGO_MM / Rmm]])   # logo px -> moldura (raios)
    A_img = np.c_[M, C]                      # moldura -> foto
    A = A_img[:, :2] @ A_log[:, :2], A_img[:, :2] @ A_log[:, 2] + A_img[:, 2]
    A = np.c_[A[0], A[1]]
    cant = A @ np.array([[0, w, 0, w], [0, 0, h, h], [1, 1, 1, 1]])
    x0, y0p = np.floor(cant.min(1)).astype(int) - 4; x1, y1p = np.ceil(cant.max(1)).astype(int) + 4
    Wb, Hb = x1 - x0, y1p - y0p
    Ash = A.copy(); Ash[:, 2] -= [x0, y0p]; Ash *= S
    # reduz o logo antes (evita serrilhado), depois aplica a afim no grid 4x
    f = np.linalg.norm(Ash[:, :2], axis=0).mean()
    pre = cv2.resize(lg, (max(int(w * f * 2), 1), max(int(h * f * 2), 1)), interpolation=cv2.INTER_AREA)
    sx, sy = w / pre.shape[1], h / pre.shape[0]
    Ap = Ash.copy(); Ap[:, 0] *= sx; Ap[:, 1] *= sy
    alfa = cv2.warpAffine(pre, Ap, (Wb * S, Hb * S), flags=cv2.INTER_LINEAR, borderValue=0)
    alfa = cv2.resize(alfa, (Wb, Hb), interpolation=cv2.INTER_AREA)
    # 3. cor do logo = borda jateada no mesmo estado, logo abaixo do logo novo
    cy_logo = A @ np.array([w / 2, h / 2, 1])
    dirb = M @ np.array([0, 1.0]); dirb /= np.linalg.norm(dirb)
    amost = np.zeros(anel.shape, bool)
    for t in np.linspace(-0.15, 0.15, 31):
        pr = C + M @ (Rot(t) @ np.array([0, 1.0]) * 1.08)    # dentro da borda jateada, perto do logo
        yy, xx = int(round(pr[1])), int(round(pr[0]))
        amost[yy - 6:yy + 7, xx - 6:xx + 7] = True
    amost &= anel & ~(m > 0)
    L1i = lin(R1i.astype(np.float32) / 255); L2i = lin(R2i.astype(np.float32) / 255)
    c_lig = np.median(L1i[amost], 0) * BRILHO_LOGO
    c_apa = np.median(L2i[amost], 0)
    sl = (slice(y0p, y1p), slice(x0, x1))
    al = alfa[..., None]
    L1i[sl] = L1i[sl] * (1 - al) + al * c_lig
    if HALO > 0:
        hal = ndi.gaussian_filter(alfa, HALO_MM / mm_px)
        hal = hal / max(hal.max(), 1e-6) * HALO
        L1i[sl] = L1i[sl] + (hal * (1 - alfa))[..., None] * c_lig
    L2i[sl] = L2i[sl] * (1 - al) + al * c_apa
    out = []
    for Li, A_, im, sp in ((L1i, A1, im1, s_lig), (L2i, A2, im2, s_apa)):
        rgb = (srgb(Li) * 255 + 0.5).astype(np.uint8)
        if sp.endswith('.jpg'):
            Image.fromarray(rgb).save(sp, quality=95, qtables=im.quantization, subsampling=0, exif=im.info.get('exif', b''))
        else:
            Image.fromarray(np.dstack([rgb, A_])).save(sp, optimize=True)
    info = dict(centro=C.tolist(), semi_eixos=[float(a), float(b)], phi=float(np.rad2deg(phi)), psi=float(np.rad2deg(psi)),
                mm_px=float(mm_px), raio_espelhado_mm=float(Rmm), logo_impresso_px=int(imp.sum()),
                logo_novo_centro=cy_logo.tolist(), logo_novo_largura_px=float(LARG / mm_px),
                cor_lig=(srgb(c_lig) * 255).round().tolist(), cor_apa=(srgb(c_apa) * 255).round().tolist())
    if dbg:
        cx, cy = int(cy_logo[0]), int(cy_logo[1]); r = int(LARG / mm_px * 1.3)
        L1o = (srgb(L1i) * 255 + 0.5).astype(np.uint8); L2o = (srgb(L2i) * 255 + 0.5).astype(np.uint8)
        caixa = (slice(max(cy - r, 0), cy + r), slice(max(cx - r, 0), cx + r))
        lin1 = np.concatenate([R1[caixa], L1o[caixa]], 1); lin2 = np.concatenate([R2[caixa], L2o[caixa]], 1)
        g = np.concatenate([lin1, lin2], 0)
        Image.fromarray(g).resize((g.shape[1] * 2, g.shape[0] * 2), Image.LANCZOS).save(dbg, quality=92)
    return info


if __name__ == '__main__':
    a = sys.argv
    print(json.dumps(principal(a[1], a[2], float(a[3]), a[4], a[5], a[6] if len(a) > 6 else None)))
