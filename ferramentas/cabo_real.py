# -*- coding: utf-8 -*-
"""Cabo real sem IA: retoque do item d2 de guia/criterios.md (Fotógrafo Gardie).

Desenha o cabo branco do espelho sobre a foto, na rota real do modelo
(guia/produto.md › Cabo e plug): sai de trás da base, rente à bancada, e corre
pela superfície até a borda do quadro. O corpo do cabo é opaco (os veios da
bancada somem sob ele); fora do corpo, só a sombra escurece a superfície real.
O produto fica intocado: o cabo passa por trás dele (alfa do recorte) e os
pixels do produto saem iguais aos da foto. A alça no ar, da traseira da
cabeça ao topo do pivô, usa o modo "suspenso" (abaixo).

O perfil transversal foi medido no cabo da A1 do lote 2026-10-11 (Classique
Lux cromado, publicaria): núcleo claro de ~5 px, +15,6 sobre o mármore, e
bordas escuras de -5 (lado do fundo) e -8 (lado da câmera), num cabo de 10 px.

Uso:
  python3 cabo_real.py foto.png recorte.png rota.json saida.png
      recorte.png: o <base>-recorte.png do `estudio_fal.py recortar` (alfa = produto).
      Grava saida.png, saida-mascara.png (área alterada, para o diff) e
      saida.json (parâmetros usados), e imprime a conferência.

rota.json:
  pontos     pontos de controle em px da foto. O 1º fica ESCONDIDO atrás do
             produto (dentro do recorte), na direção da saída do cabo; o
             último, fora do quadro (ou atrás de um objeto que o esconda).
  larg       largura do cabo, borda a borda, em px, em cada ponto. O cabo tem
             5 mm: com o Ø da base de guia/produto.md medido em px, a largura
             junto da base é 5 × (px por mm) e diminui para o fundo com a
             perspectiva.
  sigma      desfoque em px em cada ponto, acompanhando a profundidade de
             campo da foto (padrão 0,5).
  ganho_pos  multiplica o núcleo claro do perfil (padrão 1,35).
  ganho_neg  multiplica as bordas escuras (padrão 1,15).
  ondula     ondulação leve do cabo, em px (padrão 1,2).
  sombra     penumbra para o lado da câmera, em níveis (padrão 3).
  semente    sorteio da ondulação e das variações (padrão 7).
  grao       desvio do grão somado ao corpo do cabo, em níveis (padrão 0,35);
             use o ruído medido no fundo da foto (stills de estúdio: 1 a 3).
             Ou um valor por ponto de controle, quando o ruído do fundo muda
             ao longo da rota.
  grao_mono  true: o mesmo grão nos três canais. Use quando o fundo da foto é
             cinza neutro (R = G = B), como nas stills de estúdio; grão
             colorido ali aparece como ruído de cor no cabo.
  grao_depois  true: o grão entra depois do desfoque, como o ruído do sensor,
             e "grao" passa a ser o desvio medido na foto (passa-alta de 3 px).
             Sem isso, o desfoque amansa o grão a cerca de 1/3.
  base       desenha sobre esta imagem em vez da foto (opcional).
  janela     [xa, xb]: o cabo novo vai até xa e se funde à base até xb
             (opcional; serve para emendar um cabo que já existe na base).

Trecho no ar (da traseira da cabeça até o topo do sino), com "suspenso": true:
  o cabo vira um cilindro iluminado pela luz da cena, sem sombra numa
  superfície, e só aparece na janela "visivel". Os pontos de controle começam
  escondidos atrás da cabeça e terminam escondidos no pivô. Serve também para
  o cabo pendente dos modelos de parede e para o cabo deitado no chão de uma
  still de estúdio com câmera baixa (~7°): ali a sombra de contato fica
  escondida atrás do próprio cabo, e basta a luz de cima (luz [-0.2, -0.85,
  -0.3]).
  visivel    máscara PNG: branco = o cabo passa na frente. Padrão: o fundo do
             recorte (1 - alfa). Passe a máscara do vão quando o recorte o
             engolir (o BiRefNet preenche o vão entre a cabeça e o garfo): os
             pixels "do produto" alterados na janela têm de ser só fundo.
  borda_mista  true: nos pixels da máscara com valor entre 0 e 1 (a borda
             suave do objeto que esconde o cabo), o cabo entra só na parte de
             fundo do pixel: troca o fundo puro (estimado nos vizinhos
             visíveis) pelo cabo e mantém a parte do objeto. Sem isso, a borda
             fica um pouco mais clara onde o cabo passa atrás dela.
  luz        direção da luz [x, y, z] (x para a direita, y para baixo, z para
             longe da câmera). Padrão [-0.75, -0.35, -0.55]: janela à esquerda.
  brilho     [lado da sombra, lado da luz] em níveis (padrão [135, 205]). Ou um
             par por ponto de controle, interpolado ao longo do cabo, quando a
             luz do fundo cai ao longo da rota (cabo pendente numa still de
             estúdio: mantenha a mesma razão com o fundo medido em cada ponto).

Depois, rode `inspecao_imagem.py diff foto.png saida.png saida-mascara.png` e
leia os recortes do cabo (saída de trás da base, trajeto e borda do quadro).
"""
import json
import sys

import numpy as np
from PIL import Image

# perfil medido (d em px para um cabo de 10 px; + = lado da câmera)
PD = np.arange(-10, 10.01, 0.5)
PV = np.array([0.3, 0.3, 0.3, 0.3, 0.1, -0.5, -1.4, -2.2, -3.2, -4.5, -5.05, -4.65, -2.66, -0.37,
               3.33, 6.9, 10.1, 12.7, 14.3, 15.3, 15.6, 15.3, 14.1, 12.5, 9.9, 5.9, 0.77, -3.7,
               -6.3, -7.6, -7.95, -7.4, -5.2, -3.1, -2.0, -1.0, -0.4, 0.0, -0.1, 0.0, 0.0])
PADRAO = {'sigma': None, 'ganho_pos': 1.35, 'ganho_neg': 1.15, 'ondula': 1.2, 'sombra': 3.0, 'semente': 7}
SS = 4          # supersampling
PASSO = 0.5     # passo da curva em px


def catmull(pts, n=60):
    p = np.array(pts, float)
    p = np.vstack([2 * p[0] - p[1], p, 2 * p[-1] - p[-2]])
    out = []
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        for t in np.linspace(0, 1, n, endpoint=False):
            t2, t3 = t * t, t * t * t
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    out.append(p[-2])
    return np.array(out)


def gauss(a, s):
    if s <= 0:
        return a.astype(float)
    k = int(np.ceil(3.5 * s))
    g = np.exp(-0.5 * (np.arange(-k, k + 1) / s) ** 2)
    g /= g.sum()
    a = np.pad(a.astype(float), ((k, k), (k, k)), mode='edge')
    a = np.apply_along_axis(lambda v: np.convolve(v, g, mode='valid'), 0, a)
    return np.apply_along_axis(lambda v: np.convolve(v, g, mode='valid'), 1, a)


def ruido_suave(n, escala, semente):
    r = np.random.default_rng(semente)
    k = max(3, int(escala))
    v = r.normal(size=n + 6 * k)
    g = np.exp(-0.5 * (np.arange(-3 * k, 3 * k + 1) / (escala / 2.0)) ** 2)
    v = np.convolve(v, g / g.sum(), mode='same')[3 * k:3 * k + n]
    return v / (np.abs(v).max() + 1e-9)


def iluminacao(img, prod):
    """Luz da superfície sem veios e sem produto (convolução normalizada, sigma 10)."""
    lum = img @ [0.299, 0.587, 0.114]
    from PIL import ImageFilter
    med = np.asarray(Image.fromarray(np.clip(lum, 0, 255).astype(np.uint8)).filter(ImageFilter.MedianFilter(21))).astype(float)
    peso = ((~prod) & (lum > med - 5)).astype(float)
    den = gauss(peso, 10) + 1e-6
    m = np.stack([gauss(img[..., c] * peso, 10) / den for c in range(3)], -1)
    return np.where((den > 0.02)[..., None], m, 200.0)


def curva(rota):
    """Curva densa por comprimento de arco: pontos, normal (lado da câmera), s."""
    c = catmull(rota['pontos'])
    d = np.r_[0, np.cumsum(np.hypot(*np.diff(c, axis=0).T))]
    s = np.arange(0, d[-1], PASSO)
    x, y = np.interp(s, d, c[:, 0]), np.interp(s, d, c[:, 1])
    tx, ty = np.gradient(x), np.gradient(y)
    n = np.hypot(tx, ty)
    nx, ny = -ty / n, tx / n
    if ny.mean() < 0:  # positivo = para baixo na foto, lado da câmera
        nx, ny = -nx, -ny
    # largura e desfoque interpolados pelo comprimento entre os pontos de controle
    pc = np.array(rota['pontos'], float)
    dc = np.r_[0, np.cumsum(np.hypot(*np.diff(pc, axis=0).T))]
    f = s / s[-1] * dc[-1]
    larg = np.interp(f, dc, rota['larg'])
    sig = np.interp(f, dc, rota['sigma']) if rota.get('sigma') else np.full(len(s), 0.5)
    gr = rota.get('grao', 0.35)
    gs = np.interp(f, dc, gr) if isinstance(gr, (list, tuple)) else np.full(len(s), float(gr))
    br = np.array(rota.get('brilho', [135, 205]), float)
    if br.ndim == 2:   # um par [sombra, luz] por ponto de controle
        br = np.stack([np.interp(f, dc, br[:, 0]), np.interp(f, dc, br[:, 1])], -1)
    else:
        br = np.tile(br, (len(s), 1))
    return x, y, nx, ny, s, larg, sig, br, gs


def vizinhos(X, Y, x, y, k, m, lado=48):
    """Subpixels a até m px da curva decimada (passo k) e, para eles, o índice do ponto da
    curva mais próximo (no empate, o menor). Vai por ladrilhos de `lado` px e só compara
    com os pontos da curva a até m px do ladrilho: dá o mesmo resultado da busca em toda a
    curva, sem o custo dela nas stills grandes."""
    hs, ws = X.shape
    perto = np.zeros((hs, ws), bool)
    idx = np.full((hs, ws), -1)
    xd, yd = x[::k], y[::k]
    t = lado * SS
    for a in range(0, hs, t):
        for b in range(0, ws, t):
            qx, qy = X[a:a + t, b:b + t], Y[a:a + t, b:b + t]
            sh = qx.shape
            qx, qy = qx.ravel(), qy.ravel()
            caixa = lambda u, v: np.where((u >= qx[0] - m) & (u <= qx[-1] + m) & (v >= qy[0] - m) & (v <= qy[-1] + m))[0]
            cd = caixa(xd, yd)
            if not len(cd):
                continue
            i0 = cd[np.argmin((qx[:, None] - xd[cd]) ** 2 + (qy[:, None] - yd[cd]) ** 2, axis=1)]
            pt = np.hypot(qx - xd[i0], qy - yd[i0]) <= m
            if not pt.any():
                continue
            cf = caixa(x, y)
            dx = qx[pt, None] - x[None, cf]
            dy = qy[pt, None] - y[None, cf]
            ix = np.full(len(qx), -1)
            ix[pt] = cf[np.argmin(dx * dx + dy * dy, axis=1)]
            perto[a:a + t, b:b + t] = pt.reshape(sh)
            idx[a:a + t, b:b + t] = ix.reshape(sh)
    return perto.ravel(), idx.ravel()


def desenhar(foto, recorte, rota, saida):
    r = dict(PADRAO)
    r.update(rota)
    original = np.asarray(Image.open(foto).convert('RGB')).astype(float)
    base = np.asarray(Image.open(r['base']).convert('RGB')).astype(float) if r.get('base') else original.copy()
    H, W = original.shape[:2]
    rec = Image.open(recorte)
    alfa = np.asarray((rec.getchannel('A') if 'A' in rec.getbands() else rec.convert('L')).resize((W, H))).astype(float) / 255
    prod_duro = alfa > 60 / 255
    susp = bool(r.get('suspenso'))
    if susp:
        if r.get('visivel'):
            vis = np.asarray(Image.open(r['visivel']).convert('L').resize((W, H))).astype(float) / 255
        else:
            vis = 1 - alfa
    else:
        M = iluminacao(original, alfa > 0.2)
        Ml = np.where(M @ [0.299, 0.587, 0.114] > 50, M @ [0.299, 0.587, 0.114], 200.0)

    x, y, nx, ny, s, larg, sig, br, gs = curva(r)
    sem = int(r['semente'])
    on = r['ondula'] * ruido_suave(len(s), 70 / PASSO, sem + 3)
    x, y = x + nx * on, y + ny * on
    larg = larg * (1 + 0.03 * ruido_suave(len(s), 50 / PASSO, sem + 4))
    g1 = 1 + 0.10 * ruido_suave(len(s), 60 / PASSO, sem)       # brilho do núcleo ao longo do cabo
    g2 = 1 + 0.15 * ruido_suave(len(s), 45 / PASSO, sem + 1)   # força das bordas escuras

    m = int(np.ceil(larg.max() + 8))
    x0, x1 = max(0, int(x.min()) - m), min(W, int(np.ceil(x.max())) + m)
    y0, y1 = max(0, int(y.min()) - m), min(H, int(np.ceil(y.max())) + m)
    if x1 <= x0 or y1 <= y0:
        raise SystemExit('a rota não passa pela foto')
    # subpixels da região
    X, Y = np.meshgrid((np.arange(x0 * SS, x1 * SS) + 0.5) / SS, (np.arange(y0 * SS, y1 * SS) + 0.5) / SS)
    # só subpixels a até m px da curva (pré-filtro na curva decimada a 2 px)
    perto, idx = vizinhos(X, Y, x, y, max(1, int(2 / PASSO)), m)
    X, Y = X.ravel(), Y.ravel()
    perto &= (idx > 0) & (idx < len(x) - 1)  # sem tampa nas pontas (ficam escondidas ou fora do quadro)
    d = np.zeros(len(X))
    j = idx[perto]
    d[perto] = (X[perto] - x[j]) * nx[j] + (Y[perto] - y[j]) * ny[j]
    dn = np.where(perto, d * 10.0 / larg[np.maximum(idx, 0)], 99.0)
    p = np.interp(dn, PD, PV, left=0, right=0)
    p = p - r['sombra'] * np.exp(-0.5 * ((dn - 6.5) / 2.2) ** 2)   # penumbra (luz de trás)
    jj = np.maximum(idx, 0)
    p = np.where(p > 0, p * g1[jj] * r['ganho_pos'], p * g2[jj] * r['ganho_neg'])
    p[~perto] = 0
    corpo = ((np.abs(dn) <= 5.0) & perto).astype(float)

    hs, ws = (y1 - y0) * SS, (x1 - x0) * SS
    def reduz(a):
        return a.reshape(hs // SS, SS, ws // SS, SS).mean(axis=(1, 3))
    A = reduz(corpo.reshape(hs, ws))
    Pc = reduz((corpo * p).reshape(hs, ws))
    Ps = reduz(((1 - corpo) * p).reshape(hs, ws))
    sigmap = reduz(sig[jj].reshape(hs, ws))

    roi = (slice(y0, y1), slice(x0, x1))
    rg = np.random.default_rng(sem + 2)
    if isinstance(r.get('grao'), (list, tuple)):   # um desvio por ponto de controle
        z = rg.normal(0, 1, (y1 - y0, x1 - x0, 1 if r.get('grao_mono') else 3))
        grao = (np.repeat(z, 3, -1) if r.get('grao_mono') else z) * reduz(gs[jj].reshape(hs, ws))[..., None]
    elif r.get('grao_mono'):
        grao = np.repeat(rg.normal(0, float(r.get('grao', 0.35)), (y1 - y0, x1 - x0, 1)), 3, -1)
    else:
        grao = rg.normal(0, float(r.get('grao', 0.35)), (y1 - y0, x1 - x0, 3))
    if susp:
        # cilindro: normal = u * (normal no plano da foto) + componente para a câmera
        u = np.clip(np.where(perto, d / (larg[jj] / 2), 9), -1, 1)
        nz = -np.sqrt(np.clip(1 - u * u, 0, 1))
        Lv = np.array(r.get('luz', [-0.75, -0.35, -0.55]), float); Lv /= np.linalg.norm(Lv)
        Hv = Lv + np.array([0, 0, -1.0]); Hv /= np.linalg.norm(Hv)
        N = np.stack([u * nx[jj], u * ny[jj], nz], -1)
        lam = np.clip(N @ Lv, 0, 1); esp = np.clip(N @ Hv, 0, 1) ** 25
        b0, b1 = br[jj, 0], br[jj, 1]
        val = (b0 + (b1 - b0) * lam ** 0.8 + 15 * esp) * (0.88 + 0.12 * np.sqrt(np.clip(1 - u * u, 0, 1)))
        corpo_s = ((np.abs(np.where(perto, d / (larg[jj] / 2), 9)) <= 1) & perto).astype(float)
        A = reduz(corpo_s.reshape(hs, ws))
        Cv = reduz((corpo_s * val).reshape(hs, ws))
        F1 = Cv[..., None] * np.array(r.get('tinta', [1.0, 1.0, 1.0])) + (0 if r.get('grao_depois') else A[..., None] * grao)
        F2 = np.repeat((1 - A)[..., None], 3, -1)
    else:
        Mr, Mlr = M[roi], Ml[roi]
        tinta = np.array([1.06, 1.0, 0.97])  # branco do PVC, um pouco mais quente que o mármore
        Pc3 = np.where(Pc[..., None] > 0, Pc[..., None] * tinta, Pc[..., None])
        F1 = A[..., None] * Mr + Pc3 + (0 if r.get('grao_depois') else A[..., None] * grao)
        F2 = (1 - A)[..., None] * (1 + (Ps / Mlr)[..., None])   # quanto do fundo real fica, já com a sombra

    niveis = [0.3, 0.45, 0.6, 0.8, 1.0, 1.3, 1.7]
    def desfoca(a):
        if a.ndim == 3:
            return np.stack([desfoca(a[..., c]) for c in range(a.shape[2])], -1)
        pilha = [gauss(a, sg) for sg in niveis]
        out = np.zeros_like(a, dtype=float)
        sm = np.clip(sigmap, niveis[0], niveis[-1])
        for i, sg in enumerate(niveis):
            lo = niveis[i - 1] if i else sg - 1
            hi = niveis[i + 1] if i + 1 < len(niveis) else sg + 1
            w = np.where(sm <= sg, (sm - lo) / (sg - lo), (hi - sm) / (hi - sg))
            out += pilha[i] * np.clip(w, 0, 1)
        return out
    F1b, F2b = desfoca(F1), desfoca(F2 - 1) + 1
    bas = base[roi]
    comp = F1b + F2b * bas
    if r.get('grao_depois'):
        comp = comp + desfoca(A)[..., None] * grao
    if susp and r.get('borda_mista'):
        # pixel misto = v * fundo + (1 - v) * objeto: o cabo troca só a parte de fundo
        vr = vis[roi][..., None]
        cheio = (vis[roi] > 0.98).astype(float)
        den = gauss(cheio, 3) + 1e-6
        puro = np.stack([gauss(bas[..., c] * cheio, 3) / den for c in range(3)], -1)
        puro = np.where(cheio[..., None] > 0, bas, puro)
        comp = bas + vr * (comp - bas + F2b * (puro - bas) - (puro - bas))
    elif susp:
        vr = vis[roi][..., None]
        comp = vr * comp + (1 - vr) * bas   # fora da janela, o produto fica na frente
    else:
        ap = alfa[roi][..., None]
        comp = ap * bas + (1 - ap) * comp   # o cabo passa por trás do produto
    if r.get('janela'):
        xa, xb = r['janela']
        wx = np.clip((xb - (np.arange(x0, x1) + 0.5)) / (xb - xa), 0, 1)[None, :, None]
        comp = wx * comp + (1 - wx) * bas
    out = base.copy()
    out[roi] = comp
    fixo = prod_duro & (vis < 0.02) if susp else prod_duro
    out[fixo] = original[fixo]   # produto intocado (no ar, fora da janela em que o cabo passa na frente)
    res = np.clip(out + 0.5, 0, 255).astype(np.uint8)
    Image.fromarray(res).save(saida)

    mud = np.abs(res.astype(int) - original.astype(int)).max(-1) >= 1
    from PIL import ImageFilter
    mask = Image.fromarray((mud * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5))
    mp = saida[:-4] + '-mascara.png'
    mask.save(mp)
    reg = {k: v for k, v in r.items()}
    reg.update({'foto': foto, 'recorte': recorte})
    json.dump(reg, open(saida[:-4] + '.json', 'w'), indent=1, ensure_ascii=False)

    # conferência (a distância à rota se mede contra a imagem em que o cabo foi desenhado)
    dif = np.abs(res.astype(int) - original.astype(int)).max(-1)
    print(saida)
    print('produto (alfa > 60): %d px, alterados: %d' % (prod_duro.sum(), (dif[prod_duro] > 0).sum()))
    if susp:
        print('  dos quais na janela em que o cabo passa na frente: %d' % ((dif[prod_duro & (vis >= 0.02)] > 0).sum()))
    mud3 = np.abs(res.astype(int) - np.clip(base + 0.5, 0, 255).astype(int)).max(-1) >= 3
    if mud3.any():
        ys, xs = np.where(mud3)
        dist = np.full(len(xs), 1e9)
        for i in range(0, len(x), 4):
            dist = np.minimum(dist, np.hypot(xs - x[i], ys - y[i]))
        print('alterados por este cabo (>= 3 níveis): %.3f%% do quadro; a até %.1f px da rota' % (100 * mud3.mean(), dist.max()))
    print('máscara da área alterada: %s' % mp)
    return saida


if __name__ == '__main__':
    if len(sys.argv) != 5:
        print(__doc__)
        sys.exit(1)
    desenhar(sys.argv[1], sys.argv[2], json.load(open(sys.argv[3])), sys.argv[4])
