"""Recoloração aprovada no piloto do Flex Lux (Thiago, 21/10/2026): troca a cor
do cromado de um recorte pela do acabamento, sem IA.

O cromado da foto reflete o estúdio. Cada acabamento troca a cor desse
reflexo pela do acabamento, medida (em luz linear) nas referências Deca que o
Thiago mandou em 21/10:
- gold e red gold (polidos): a luminância de cada pixel é a da foto, com a
  exposição baixada para o brilho máximo cair no da referência; a cor é a da
  referência naquele nível de luminância.
- brushed nickel (escovado): o tom da referência, o reflexo um pouco
  espalhado e com menos contraste e um riscado fino no sentido de cada peça.
  Vetado em 22/10/2026 por ler polido; o brushed nickel sai de escovado.py,
  e este ramo fica só como registro do piloto.
- black matte: o reflexo borrado e comprimido para a faixa de tons da
  referência (24 a ~63 de 255); o fio fica preto.

`recolorir(R, w_met, w_fio, acab)` recebe o recorte RGBA e os pesos de metal e
de fio por pixel (0 a 1) e devolve o RGBA do acabamento, com o alfa do recorte.
Os números são os do piloto aprovado; não mude sem nova aprovação.
"""
import numpy as np
import scipy.ndimage as ndi

ACABAMENTOS = ('gold', 'red-gold', 'brushed-nickel', 'black-matte')

TONS = {  # (luminância, (R/Y, G/Y, B/Y)) por faixa da referência
    'gold': [(0.08, (1.445, 0.929, 0.355)), (0.18, (1.417, 0.942, 0.343)),
             (0.22, (1.433, 0.937, 0.337)), (0.32, (1.393, 0.950, 0.330)),
             (0.43, (1.348, 0.963, 0.338)), (0.51, (1.340, 0.966, 0.340)),
             (0.57, (1.332, 0.967, 0.347)), (0.61, (1.317, 0.972, 0.344)),
             (0.655, (1.307, 0.976, 0.341)), (0.75, (1.298, 0.977, 0.348))],
    'red-gold': [(0.035, (2.278, 0.705, 0.172)), (0.10, (1.981, 0.782, 0.294)),
                 (0.145, (1.639, 0.869, 0.403)), (0.19, (1.704, 0.851, 0.402)),
                 (0.24, (1.685, 0.859, 0.384)), (0.29, (1.666, 0.865, 0.375)),
                 (0.34, (1.668, 0.864, 0.381)), (0.39, (1.656, 0.867, 0.386)),
                 (0.47, (1.640, 0.873, 0.387)), (0.65, (1.563, 0.894, 0.413))],
    'brushed-nickel': [(0.1, (1.07, 0.995, 0.85)), (0.9, (1.07, 0.995, 0.85))],
}
# Exposição dos polidos: o cromado da foto estoura; a referência não (98% abaixo
# de 0,825 no gold e 0,745 no red gold).
EXPO = {'gold': 0.825, 'red-gold': 0.745}


def lin(c):
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def srgb(c):
    c = np.clip(c, 0, 1)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055)


def tingir(Yv, nome):
    tab = TONS[nome]
    ly = np.array([t[0] for t in tab])
    out = np.stack([Yv * np.interp(Yv, ly, [t[1][c] for t in tab]) for c in range(3)], -1)
    # acima do branco: mantém o tom (divide pelo maior canal) e clareia um
    # quarto do excesso, sem estourar como o cromado estoura
    m = out.max(-1, keepdims=True)
    exc = np.clip(m - 1, 0, None)
    out = np.where(m > 1, out / np.maximum(m, 1e-6), out)
    return out + (1 - out) * np.clip(exc * 0.25, 0, 0.35)


def borrar_mascarado(img, peso, s):
    num = np.stack([ndi.gaussian_filter(img[..., c] * peso, s) for c in range(img.shape[-1])], -1)
    den = ndi.gaussian_filter(peso, s)[..., None]
    return np.where(den > 1e-4, num / np.maximum(den, 1e-4), img)


def direcao_das_pecas(Ylum, peso):
    """Sentido de cada peça: o dos riscos do próprio reflexo (num tubo as faixas
    correm ao longo do eixo, no aro ao longo da volta), pelo tensor de
    estrutura em 1/4 da resolução, ~16 px; onde o reflexo é liso (face
    estourada) vale o das bordas da peça, ~24 px."""
    H, W = Ylum.shape
    q = 4
    def tensor(img, s):
        gx_, gy_ = ndi.sobel(img, 1), ndi.sobel(img, 0)
        return [ndi.gaussian_filter(v, s) for v in (gx_ * gx_, gy_ * gy_, gx_ * gy_)]
    lum = ndi.zoom(srgb(Ylum) * peso, 1 / q, order=1)
    msk = ndi.zoom(peso, 1 / q, order=1)
    a1, a2 = tensor(lum, 4), tensor(msk, 6)
    Jxx, Jyy, Jxy = [x + 0.5 * y for x, y in zip(a1, a2)]
    ang = 0.5 * np.arctan2(2 * Jxy, Jxx - Jyy) + np.pi / 2   # perpendicular ao gradiente
    c2, s2 = np.cos(2 * ang), np.sin(2 * ang)               # dobra o ângulo para interpolar
    zy, zx = H / c2.shape[0], W / c2.shape[1]
    c2 = ndi.zoom(c2, (zy, zx), order=1)[:H, :W]
    s2 = ndi.zoom(s2, (zy, zx), order=1)[:H, :W]
    a = 0.5 * np.arctan2(s2, c2)
    return np.cos(a).astype(np.float32), np.sin(a).astype(np.float32)


def ao_longo(campo, dx, dy, idx, passos, peso=None):
    """Média de `campo` (H x W x C) ao longo da direção (dx, dy) nos pixels idx."""
    iy, ix = idx
    acc = np.zeros((len(iy), campo.shape[-1]), np.float32)
    wac = np.zeros(len(iy), np.float32)
    ddx, ddy = dx[iy, ix], dy[iy, ix]
    for t in passos:
        py, px = iy + t * ddy, ix + t * ddx
        w = np.ones(len(iy), np.float32) if peso is None else ndi.map_coordinates(peso, [py, px], order=1, mode='nearest')
        for c in range(campo.shape[-1]):
            acc[:, c] += w * ndi.map_coordinates(campo[..., c], [py, px], order=1, mode='nearest')
        wac += w
    return acc / np.maximum(wac, 1e-6)[:, None]


def recolorir(R, w_met, w_fio, acab, semente=10554):
    """R: recorte RGBA uint8; w_met, w_fio: float32 (H, W). Devolve RGBA uint8."""
    H, W = R.shape[:2]
    alfa8 = R[..., 3]
    F = lin(R[..., :3].astype(np.float32) / 255)
    Y = F @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    peso_met = (w_met * alfa8 / 255).astype(np.float32)
    area = w_met > 0.001
    idx = np.nonzero(area)
    if acab in ('gold', 'red-gold'):
        metal = tingir(Y * EXPO[acab], acab)
    elif acab == 'brushed-nickel':
        # acetinado: reflexo um pouco espalhado (sigma 1,5 px) e com menos
        # contraste (faixa da referência: 0,10 a 0,72 de luminância)
        Yb = borrar_mascarado(Y[..., None], peso_met, 1.5)[..., 0]
        Yd = 0.10 + 0.62 * np.clip(Yb, 0, 1)
        # riscado fino no sentido da peça: ruído branco médio ao longo dele
        # (±10 px), 2,5% de amplitude
        dx, dy = direcao_das_pecas(Y, peso_met)
        rng = np.random.default_rng(semente)
        ruido = rng.standard_normal((H, W, 1)).astype(np.float32)
        risco = np.zeros((H, W), np.float32)
        risco[idx] = ao_longo(ruido, dx, dy, idx, np.arange(-10, 10.5, 1.0))[:, 0]
        risco /= max(risco[idx].std(), 1e-6)
        metal = tingir(Yd * (1 + 0.025 * risco), 'brushed-nickel')
        del Yb, ruido, risco, dx, dy
    elif acab == 'black-matte':
        # brilho largo: o reflexo borrado (sigma 3 px); vãos e filetes escuros
        # da peça ficam (mínimo com o borrado de 1 px, folga de 0,10). Faixa de
        # tons da referência: 24 a ~63 de 255 (luminância 0,010 a 0,050).
        Y3 = borrar_mascarado(Y[..., None], peso_met, 3.0)[..., 0]
        Y1 = borrar_mascarado(Y[..., None], peso_met, 1.0)[..., 0]
        Yb = np.clip(np.minimum(Y3, Y1 + 0.10), 0, 1)
        v = 0.010 + 0.040 * Yb ** 1.5
        metal = np.repeat(v[..., None], 3, -1)
        del Y3, Y1, Yb
    else:
        raise ValueError('acabamento desconhecido: ' + acab)
    out = F * (1 - w_met[..., None]) + metal * w_met[..., None]
    if acab == 'black-matte' and (w_fio > 0.9).any():
        # fio preto: o sombreado do fio branco vira o de um fio preto de PVC,
        # escuro e com um brilho estreito na faixa que recebe mais luz
        sel = w_fio > 0.9
        lo, hi = np.percentile(Y[sel], [5, 99.5])
        s = np.clip((Y - lo) / max(hi - lo, 1e-6), 0, 1)
        v = 0.010 + 0.022 * s + 0.07 * s ** 6
        out = out * (1 - w_fio[..., None]) + v[..., None] * w_fio[..., None]
    rgb = (srgb(out) * 255 + 0.5).astype(np.uint8)
    return np.dstack([rgb, alfa8])
