"""Temperatura e brilho do anel de luz de um LUX, sem IA (teste pedido pelo
Thiago em 22/10/2026: 3000K, 4500K e 6000K, e mais brilho).

A luz do LED é a diferença entre a still ligada e a apagada (mesma pose, mesma
câmera): E = ligada − apagada, em luz linear, só onde ela soma luz. Ela
inclui o anel, o halo no vidro e os reflexos do LED no metal. A versão nova é
(ligada − E) + ganho · Y(E) · cor(T), o que mantém a still ligada onde o LED
não soma luz (o logo impresso no difusor, cinza com o LED aceso) e dá cor(T) com cor(T) no lugar geométrico de Planck, relativa ao branco da câmera
(T_ref) e com a saturação s ajustada para o halo bater com as fotos reais de
4500K e 6000K (B/R do halo ÷ branco neutro 0,78 e 1,16).

Com mais brilho, o difusor passa do branco da câmera e estoura canal por canal
(vira branco puro, ou amarelo-limão no tom quente). Com [joelho], a luz do LED
acima do joelho (luz linear) é comprimida sem mudar a cor: o pixel inteiro é
escalado, e o difusor fica claro, mas com o tom (pedido de 22/10, 15:58: "a
4500K e 3000K precisam de um pouco mais de contraste"). O fundo e o metal sem
reflexo do LED não mudam.

Com [mistura] (0 a 1), o resultado é a média, em luz linear, entre a versão
estourada (peso 1 − mistura) e a comprimida (peso mistura). Ela foi pedida em
22/10, 17:07 ("um meio termo entre os dois") e usa mistura 0,5.

uso: python3 luz_anel.py <pasta do recorte> <aro-raio.npy> <T> <ganho> <saida.png> [s] [T_ref] [joelho] [mistura]"""
import sys, json
import numpy as np
from PIL import Image

def lin(c): return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
def srgb(c):
    c = np.clip(c, 0, 1); return np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055)

def planck_xy(T):
    if T <= 4000: x = -0.2661239e9 / T**3 - 0.2343589e6 / T**2 + 0.8776956e3 / T + 0.179910
    else: x = -3.0258469e9 / T**3 + 2.1070379e6 / T**2 + 0.2226347e3 / T + 0.240390
    if T <= 2222: y = -1.1063814 * x**3 - 1.34811020 * x**2 + 2.18555832 * x - 0.20219683
    elif T <= 4000: y = -0.9549476 * x**3 - 1.37418593 * x**2 + 2.09137015 * x - 0.16748867
    else: y = 3.0817580 * x**3 - 5.87338670 * x**2 + 3.75112997 * x - 0.37001483
    return x, y

M = np.array([[3.2406, -1.5372, -0.4986], [-0.9689, 1.8758, 0.0415], [0.0557, -0.2040, 1.0570]])
YW = np.array([0.2126, 0.7152, 0.0722])

def cor(T, s=1.0, T_ref=6504):
    def rgb(t):
        x, y = planck_xy(t); c = M @ np.array([x / y, 1, (1 - x - y) / y]); return c / (c @ YW)
    c = (rgb(T) / rgb(T_ref)) ** s
    return c / (c @ YW)

def raio_vidro(R2, cx, cy, th, rb):
    """Borda vidro/difusor por ângulo, na still apagada: o difusor apagado é a
    faixa escura logo por dentro do aro; a borda é onde a luminância cai."""
    Y = (R2[..., :3].astype(np.float32) / 255) @ YW
    out = []
    for t, r0 in zip(th, rb):
        s = np.linspace(0.6, 0.99, 400)
        xs = np.clip(cx + np.cos(t) * s * r0, 0, Y.shape[1] - 1).astype(int)
        ys = np.clip(cy + np.sin(t) * s * r0, 0, Y.shape[0] - 1).astype(int)
        p = Y[ys, xs]
        escuro = np.median(p[-60:-10])           # difusor apagado
        dentro = p < escuro + 0.35 * (np.median(p[:80]) - escuro) if np.median(p[:80]) > escuro else p < escuro + 0.05
        # primeiro ponto a partir do qual tudo até o aro é difusor
        i = len(p) - 1
        while i > 0 and dentro[i - 1]: i -= 1
        out.append(s[i] * r0)
    out = np.array(out)
    from scipy.ndimage import median_filter
    return median_filter(out, 15, mode='wrap')

if __name__ == '__main__':
    D, aro, T, g, saida = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), sys.argv[5]
    s = float(sys.argv[6]) if len(sys.argv) > 6 else 1.0
    T_ref = float(sys.argv[7]) if len(sys.argv) > 7 else 6504
    ox, oy = json.load(open(f'{D}/caixa-produto.json'))['caixa'][:2]
    R1 = np.asarray(Image.open(f'{D}/recorte-1.png')); R2 = np.asarray(Image.open(f'{D}/recorte-2.png'))
    L1 = lin(R1[..., :3].astype(np.float32) / 255); L2 = lin(R2[..., :3].astype(np.float32) / 255)
    E = np.clip(L1 - L2 - 0.004, 0, None)
    YE = E @ YW
    c = cor(T, s, T_ref).astype(np.float32)
    base = L1 - E
    led = g * YE[..., None] * c
    out = base + led
    if len(sys.argv) > 8:                       # compressão das altas luzes, sem mudar a cor
        j = float(sys.argv[8])
        m = out.max(-1); mb = base.max(-1)
        alvo = np.where(m > j, j + (1 - j) * (1 - np.exp(-(m - j) / (1 - j))), m)
        k = np.clip((alvo - mb) / np.maximum(m - mb, 1e-6), 0, 1)
        comp = base + k[..., None] * led
        w = float(sys.argv[9]) if len(sys.argv) > 9 else 1.0
        out = (1 - w) * np.clip(out, 0, 1) + w * comp
    same = np.abs(R1[..., 3].astype(int) - R2[..., 3].astype(int)) <= 2
    out = np.where(same[..., None], out, L1)
    rgb = (srgb(out) * 255 + 0.5).astype(np.uint8)
    Image.fromarray(np.dstack([rgb, R1[..., 3]])).save(saida, optimize=True)
    print('T %d ganho %.2f cor lin %s' % (T, g, np.round(c, 3)))
