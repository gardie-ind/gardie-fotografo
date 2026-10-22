"""Tabela nova do red gold a partir da foto real do Thiago (22/10/2026): em cada
nó da tabela atual, o tom é girado em matiz e reduzido em croma (CIELAB, mesmo
L*) pela diferença medida entre os aros da foto e o nosso red gold, por faixa
de L*. 'meio' aplica metade da diferença. A tabela de partida é a Deca de
21/10/2026, que acabamentos.py usava antes; a saída 'meio', aprovada pelo
Thiago em 22/10/2026, é a de lá hoje.
Medidas: medir_acabamento.py tom (guia/criterios.md, item b).

uso: python3 novo_tom.py  (grava tons-red-gold.json na pasta atual)"""
import json, numpy as np
DECA = [(0.035, (2.278, 0.705, 0.172)), (0.10, (1.981, 0.782, 0.294)),
        (0.145, (1.639, 0.869, 0.403)), (0.19, (1.704, 0.851, 0.402)),
        (0.24, (1.685, 0.859, 0.384)), (0.29, (1.666, 0.865, 0.375)),
        (0.34, (1.668, 0.864, 0.381)), (0.39, (1.656, 0.867, 0.386)),
        (0.47, (1.640, 0.873, 0.387)), (0.65, (1.563, 0.894, 0.413))]
M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]]); W = M.sum(1)
Mi = np.linalg.inv(M)
f = lambda t: np.where(t > 0.008856, np.cbrt(t), 7.787 * t + 16 / 116)
fi = lambda t: np.where(t > 0.20689, t ** 3, (t - 16 / 116) / 7.787)
def lab(rgb):
    X = M @ rgb / W; fx, fy, fz = f(X)
    return np.array([116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)])
def rgb(Lab):
    fy = (Lab[0] + 16) / 116; fx = fy + Lab[1] / 500; fz = fy - Lab[2] / 200
    return Mi @ (np.array([fi(fx), fi(fy), fi(fz)]) * W)
# medido em 22/10 (medir_acabamento.py tom): centro da faixa de L*, foto (aros) e nosso (Mobile)
Lc = [30, 47.5, 62.5, 77.5]
h_foto, C_foto = [69.2, 71.6, 72.9, 74.2], [12.4, 18.0, 23.3, 27.1]
h_nos, C_nos = [58.8, 64.8, 67.2, 70.6], [29.3, 27.6, 34.2, 36.9]
dh = np.array(h_foto) - h_nos; s = np.array(C_foto) / C_nos
out = {}
for nome, k in (('foto', 1.0), ('meio', 0.5)):
    tab = []
    for Y, c in DECA:
        L, a, b = lab(Y * np.array(c))
        d = np.interp(L, Lc, dh) * k; sc = 1 + (np.interp(L, Lc, s) - 1) * k
        h = np.arctan2(b, a) + np.radians(d); C = np.hypot(a, b) * sc
        v = rgb(np.array([L, C * np.cos(h), C * np.sin(h)]))
        tab.append((Y, tuple(np.round(v / Y, 3).tolist())))
        print(nome, Y, round(float(L), 1), c, '->', tab[-1][1], 'Y=', round(float(M[1] @ v / Y), 3))
    out[nome] = tab
json.dump(out, open('tons-red-gold.json', 'w'), indent=1)
