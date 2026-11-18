# Svelte 10479: tira os dois furos de parafuso da canopla (Thiago 02/11/2026: "a canopla não possui mais
# estes dois furos, é uma peça lisa"), sem IA, só com os pixels da própria foto.
# - Furo da direita (parafuso): elipse que cobre o parafuso e a borda clara do rebaixo, preenchida pelas
#   feições casadas das colunas limpas dos dois lados (detalhe abaixo), com a costura tirada por Laplace.
# - Furo da esquerda (rebaixo meio escondido pelo bloco do braço): membrana (Laplace) presa na canopla em volta.
# As máscaras saem do cromado (as outras cores são recolorações do mesmo quadro); o preenchimento usa os
# pixels de cada acabamento.
# uso: canopla_lisa.py entrada.png saida.png [--mascara-de cromado.png] [--salvar-mascara m.png]
import sys
import cv2
import numpy as np
from scipy.ndimage import binary_dilation
from PIL import Image

import argparse
ap = argparse.ArgumentParser()
ap.add_argument('entrada'); ap.add_argument('saida')
ap.add_argument('--mascara-de'); ap.add_argument('--salvar-mascara')
args = ap.parse_args()
ent, sai = args.entrada, args.saida
rgba = np.asarray(Image.open(ent).convert('RGBA')).copy()
rgb = rgba[..., :3].copy()
H, W = rgb.shape[:2]
assert (H, W) == (3365, 3365), (H, W)
L = np.asarray(Image.open(args.mascara_de or ent).convert('RGB')).astype(float).mean(-1)

# furo da direita
mD = np.zeros((H, W), np.uint8)
cv2.ellipse(mD, (1979, 958), (62, 54), 45, 0, 360, 255, -1)  # parafuso + borda clara do rebaixo
cv2.circle(mD, (2033, 938), 5, 255, -1)                        # brilho da borda do rebaixo, em cima à direita
# furo da esquerda: o rebaixo escuro entre a canopla clara e o bloco
caixa = (slice(770, 872), slice(1598, 1642))
escuro = np.zeros((H, W), bool)
escuro[caixa] = L[caixa] < 170
escuro = cv2.dilate(escuro.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
mE = np.zeros((H, W), bool)
for y in range(770, 872):
    xs = np.nonzero(escuro[y, 1598:1642])[0]
    if len(xs):
        mE[y, 1598 + xs[0]:1598 + xs[-1] + 1] = True

# furo da direita: interpolação entre duas colunas limpas da canopla, uma de cada lado do parafuso
# (x = XL e x = XR), com as feições casadas: as linhas do reflexo (fina clara, escura, grossa clara, borda
# da área clara de baixo) e a cunha escura de cima, que afina até sumir no lado direito. Para cada pixel do
# furo, acha onde ele cai entre as feições interpoladas naquela coluna, lê o ponto correspondente em cada
# coluna de referência e mistura pela distância. Depois, o resíduo na borda do furo (original menos
# preenchido) é espalhado para dentro por Laplace, para não deixar costura, e entra um grão igual ao da
# vizinhança.
XL, XR = 1918, 2042
# feições (y) em cada coluna de referência: topo, cunha (começo e fim da borda), linha fina (começo e pico),
# escuro, linha grossa (pico e fim), borda da área clara de baixo, base. Do lado direito não há cunha: as duas
# bordas dela coincidem com o começo da linha fina.
FEIT_L = [860, 881, 892, 946, 951, 957, 967, 972, 1007, 1030]
FEIT_R = [860, 937, 937, 937, 942, 948, 956, 962, 987.5, 1030]
SO_ESQ = (1, 2)    # borda e corpo da cunha: reflexo escuro, só existe do lado esquerdo
# a borda de cima da cunha segue reta com a inclinação medida na parte visível (x 1918-1934: y 886,8 -> 900,7)
# até encostar na linha fina (ponta perto de x = 1983, escondida pelo parafuso)
CUNHA_Y0, CUNHA_INCL = 881.0, 0.85
# ponta da cunha: onde a borda dela encontra o começo da linha fina
PONTA = XL + (FEIT_L[3] - CUNHA_Y0) / (CUNHA_INCL + (FEIT_L[3] - FEIT_R[3]) / (XR - XL))
src = rgb.astype(float)
refL = src[:, XL - 1:XL + 2].mean(1)
refR = src[:, XR - 1:XR + 2].mean(1)
def amostra(ref, y):
    y0 = int(np.floor(y)); f = y - y0
    return ref[y0] * (1 - f) + ref[y0 + 1] * f
def interp(y, x):
    t = (x - XL) / (XR - XL)
    F = [(1 - t) * a + t * b for a, b in zip(FEIT_L, FEIT_R)]
    F[1] = min(F[3], CUNHA_Y0 + CUNHA_INCL * (x - XL))
    F[2] = min(F[3], F[1] + (FEIT_L[2] - FEIT_L[1]))
    i = max(k for k in range(len(F) - 1) if F[k] <= y and F[k + 1] > F[k])
    s_ = (y - F[i]) / (F[i + 1] - F[i])
    yl = FEIT_L[i] + s_ * (FEIT_L[i + 1] - FEIT_L[i])
    yr = FEIT_R[i] + s_ * (FEIT_R[i + 1] - FEIT_R[i])
    if i in SO_ESQ:
        return amostra(refL, yl)
    if i == 3:
        # começo da linha fina: do lado esquerdo vem logo abaixo da cunha escura; depois da ponta da cunha
        # (x ~ 1988) só vale o lado direito, que tem luz em cima da linha. Rampa de 12 px na ponta.
        w = min(1.0, max(0.0, (x - (PONTA - 6)) / 12))
        return (1 - w) * amostra(refL, yl) + w * amostra(refR, yr)
    return (1 - t) * amostra(refL, yl) + t * amostra(refR, yr)
dentro = mD > 0
anel = binary_dilation(dentro, iterations=1) & ~dentro
fill = src.copy()
calc = np.zeros_like(src)
ys, xs = np.nonzero(dentro | anel)
assert xs.min() > XL and xs.max() < XR and ys.min() > FEIT_L[0] and ys.max() < FEIT_L[-1]
for y, x in zip(ys, xs):
    calc[y, x] = interp(y, x)
# resíduo no anel em volta do furo (original menos interpolado), espalhado para dentro por Laplace
res = np.zeros_like(src)
res[anel] = src[anel] - calc[anel]
bb = (slice(ys.min() - 1, ys.max() + 2), slice(xs.min() - 1, xs.max() + 2))
R = res[bb].copy(); D = dentro[bb]
for _ in range(6000):
    viz = (np.roll(R, 1, 0) + np.roll(R, -1, 0) + np.roll(R, 1, 1) + np.roll(R, -1, 1)) / 4
    R[D] = viz[D]
corr = np.zeros_like(src); corr[bb] = R
fill[dentro] = calc[dentro] + corr[dentro]
# grão: ruído fino medido numa área lisa da canopla (passa-alta 3x3), com a mesma força
def ruido(a):
    return (a - cv2.blur(a, (3, 3)))[1:-1, 1:-1].std(axis=(0, 1))
sig = (ruido(src[1012:1032, 1895:1925]) + ruido(src[875:900, 2040:2070])) / 2
puro = ruido(np.random.default_rng(0).normal(0, 1, (400, 400, 1)))[0]
rng = np.random.default_rng(10479)
g = rng.normal(0, 1, (H, W))[..., None] * (sig / puro)[None, None, :]
fill[dentro] += g[dentro]
print('residuo no anel (média abs):', np.abs(res[anel]).mean(axis=0).round(1), 'grão:', (sig / puro).round(2))
out = rgb.copy()
out[dentro] = np.clip(fill[dentro] + 0.5, 0, 255).astype(np.uint8)
# furo da esquerda: a máscara cresce 2 px para levar junto a borda escura antisserrilhada do rebaixo; o
# palpite inicial de cada linha vem da canopla logo à esquerda, e o furo vira uma membrana (Laplace) presa
# nos pixels em volta, que é como a canopla se comporta ali (só degradês suaves). Depois, o mesmo grão.
mE = cv2.dilate(mE.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
fE = out.astype(float)
for y in np.unique(np.nonzero(mE)[0]):
    xs = np.nonzero(mE[y])[0]
    fE[y, xs] = fE[y, xs[0] - 4]
yE, xE = np.nonzero(mE)
bbE = (slice(yE.min() - 1, yE.max() + 2), slice(xE.min() - 1, xE.max() + 2))
RE = fE[bbE].copy(); DE = mE[bbE]
for _ in range(6000):
    viz = (np.roll(RE, 1, 0) + np.roll(RE, -1, 0) + np.roll(RE, 1, 1) + np.roll(RE, -1, 1)) / 4
    RE[DE] = viz[DE]
fE[bbE] = RE
fE[mE] += rng.normal(0, 1, (int(mE.sum()), 1)) * (sig / puro)[None, :]
out[mE] = np.clip(fE[mE] + 0.5, 0, 255).astype(np.uint8)
rgba[..., :3] = out
Image.fromarray(rgba, 'RGBA').save(sai, optimize=True)
if args.salvar_mascara:
    Image.fromarray(((mD > 0) | mE).astype(np.uint8) * 255).save(args.salvar_mascara)
print(sai, 'px trocados:', int((mD > 0).sum() + mE.sum()))
