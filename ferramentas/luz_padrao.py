"""Padrão de iluminação do anel LUX aprovado pelo Thiago em 22/10/2026, 18:44
("O meio termo está perfeito. Vamos seguir com ele como padrão para todos os
outros espelhos."): brilho +80% (ganho 1,8), joelho 0,8 e mistura 0,5, com a
cor de Planck calibrada nas fotos reais (s 1,564, branco da câmera 5330K).

Os tons têm nome de divulgação (decisão de 22/10, 14:47):
  3000K = render 4500K · 4500K = render 5150K · 6000K = render 6000K

Entra o par de fotos ligada e apagada do mesmo espelho, na mesma pose (still
JPEG com fundo ou recorte PNG com alfa). Sai a versão ligada no tom pedido. O
método e as fórmulas estão em luz_anel.py.

uso: python3 luz_padrao.py <ligada> <apagada> <tom: 3000|4500|6000> <saida.png>"""
import sys
import numpy as np
from PIL import Image
from luz_anel import lin, srgb, cor, YW

GANHO, S, T_REF, JOELHO, MISTURA = 1.8, 1.564, 5330, 0.8, 0.5
RENDER = {'3000': 4500, '4500': 5150, '6000': 6000}


def ler(p):
    im = Image.open(p)
    a = np.asarray(im.convert('RGBA'))
    return lin(a[..., :3].astype(np.float32) / 255).astype(np.float32), a[..., 3]


def acender(L1, L2, T):
    E = np.clip(L1 - L2 - 0.004, 0, None)
    base = L1 - E
    led = (GANHO * (E @ YW.astype(np.float32)))[..., None] * cor(T, S, T_REF).astype(np.float32)
    out = base + led
    m = out.max(-1); mb = base.max(-1)
    alvo = np.where(m > JOELHO, JOELHO + (1 - JOELHO) * (1 - np.exp(-(m - JOELHO) / (1 - JOELHO))), m)
    k = np.clip((alvo - mb) / np.maximum(m - mb, 1e-6), 0, 1)
    comp = base + k[..., None] * led
    return (1 - MISTURA) * np.clip(out, 0, 1) + MISTURA * comp


if __name__ == '__main__':
    lig, apa, tom, saida = sys.argv[1:5]
    L1, A1 = ler(lig); L2, A2 = ler(apa)
    if L1.shape != L2.shape:
        sys.exit(f'tamanhos diferentes: {L1.shape} x {L2.shape}')
    out = acender(L1, L2, RENDER[tom])
    out = np.where((np.abs(A1.astype(int) - A2.astype(int)) <= 2)[..., None], out, L1)
    rgb = (srgb(out) * 255 + 0.5).astype(np.uint8)
    if (A1 < 255).any():
        Image.fromarray(np.dstack([rgb, A1])).save(saida, optimize=True)
    else:
        Image.fromarray(rgb).save(saida, optimize=True)
    print(saida, tom)
