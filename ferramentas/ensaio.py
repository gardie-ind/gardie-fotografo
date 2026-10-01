# -*- coding: utf-8 -*-
"""Ensaio no estilo Mercado Livre — Fotógrafo da Gardie.

Replica o processo do "Gerar fotos com IA" do ML com os nossos motores:
  1 referência padronizada tipo capa (fundo branco, quadrada, produto ~93%)
  + moldura curta que NÃO descreve o produto ({produto} + {cena})
  + várias opções por pedido (--n por motor por receita)
  + prancha CEGA por receita (rótulos embaralhados) para filtro e escolha.

Uso (Windows: PYTHONUTF8=1 py ensaio.py ... | Linux: python3 ensaio.py ...):
  py ensaio.py --produto "Espelho de Aumento 5x com Luz LED de Mesa Gardie Classique Lux Cromado" ^
      --ref ../referencias/catalogo/espelho-de-aumento-com-ring-light-5X-cromado-gardie-classique-lux-ligado-em-fundo-cinza.jpg
  py ensaio.py --produto "..." --ref capa.jpg --so-preparo      só prepara e confere a referência (sem API)
  py ensaio.py --produto "..." --ref capa.jpg --simular         fluxo inteiro SEM API (imagens fictícias)
  py ensaio.py --listar-modelos                                 modelos Gemini que geram imagem

Opções principais:
  --produto TEXTO      nome/tipo como no título do anúncio (vira o {produto} da moldura)
  --ref IMG            repetível; a 1ª é a principal (kontext usa só ela)
  --receitas ...       pastas e/ou arquivos .txt com a {cena}; ignora nomes iniciados por "_";
                       linhas iniciadas por "#" são comentário (padrão: receitas/ do repositório)
  --moldura TXT        precisa conter {produto} e {cena} (padrão: o _moldura.txt da 1ª pasta
                       de receitas, ou da pasta do 1º .txt, que o tiver; senão receitas/_moldura.txt)
  --motores LISTA      "gemini:<model-id>", "kontext", "seedream", separados por vírgula
  --n N                gerações por motor por receita (padrão 4)
  --aspecto W:H        proporção pedida pelo PARÂMETRO da API, nunca no texto (padrão 1:1)
  --saida PASTA        padrão: ensaios/_versoes/<data>-<slug-do-produto>/
  --sem-preparo        manda as referências cruas (sem padronizar como capa)
  --recorte local|birefnet   como separar o produto do fundo no preparo (padrão local, sem API)
  --paralelo N         chamadas simultâneas (padrão 4)

Saída: refs/ (capa preparada + conferência), <receita>/A1.png..., prancha-<receita>.png,
mapa.json (rótulo -> motor; NÃO abrir antes do veredito) e manifesto.json (prompts, refs,
parâmetros). Credenciais: GEMINI_API_KEY / FAL_KEY ou ~/.config/gardie/gemini.json / fal.json.
"""
import os
import re
import sys
import json
import math
import time
import uuid
import random
import argparse
import datetime
import warnings
import threading
import unicodedata
import urllib.request
import urllib.error
import concurrent.futures

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

AQUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(AQUI)
sys.path.insert(0, AQUI)
sys.dont_write_bytecode = True  # não deixa __pycache__ em ferramentas/

import gerar_imagem  # noqa: E402
import estudio_fal  # noqa: E402

MOTORES_PADRAO = "gemini:gemini-2.5-flash-image,gemini:gemini-3-pro-image,kontext,seedream"
KONTEXT_ASPECTOS = ["21:9", "16:9", "4:3", "3:2", "1:1", "2:3", "3:4", "9:16", "9:21"]
GEMINI_ASPECTOS = ["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"]
# Preço aproximado por imagem (US$). Conferir a tabela do dia antes de um lote grande.
CUSTO_FAL = {"kontext": 0.08, "seedream": 0.03}
LADO_CAPA = 1536
OCUPACAO_CAPA = 0.93

_rand = random.SystemRandom()


# ---------------------------------------------------------------- utilidades

def slug(txt, maximo=60):
    t = unicodedata.normalize("NFKD", txt).encode("ascii", "ignore").decode().lower()
    t = re.sub(r"[^a-z0-9]+", "-", t).strip("-")
    return (t[:maximo].rstrip("-")) or "sem-nome"


def rotulo_letra(i):
    """0 -> A, 25 -> Z, 26 -> AA ..."""
    s = ""
    i += 1
    while i:
        i, r = divmod(i - 1, 26)
        s = chr(65 + r) + s
    return s


def ler_texto(path):
    """Lê .txt ignorando linhas de comentário (#) e espaços nas pontas."""
    with open(path, encoding="utf-8-sig") as f:
        linhas = [ln.rstrip() for ln in f if not ln.lstrip().startswith("#")]
    return "\n".join(linhas).strip()


def razao(aspecto):
    w, h = aspecto.split(":")
    return int(w) / int(h)


def mais_proximo(aspecto, opcoes):
    r = math.log(razao(aspecto))
    return min(opcoes, key=lambda o: abs(math.log(razao(o)) - r))


def custo_unit(motor):
    if motor["tipo"] == "gemini":
        m = motor["modelo"].lower()
        if "flash" in m:
            return 0.039, True
        if "pro" in m:
            return 0.134, True
        return 0.10, False
    return CUSTO_FAL[motor["tipo"]], True


def tamanho_seedream(aspecto, curto=1280):
    r = razao(aspecto)
    if r >= 1:
        w, h = round(curto * r / 16) * 16, curto
    else:
        w, h = curto, round(curto / r / 16) * 16
    return {"width": min(w, 4096), "height": min(h, 4096)}


def fonte(tamanho, negrito=False):
    nomes = (["arialbd.ttf", "DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf"] if negrito else []) + \
            ["arial.ttf", "DejaVuSans.ttf", "LiberationSans-Regular.ttf"]
    for n in nomes:
        try:
            return ImageFont.truetype(n, tamanho)
        except OSError:
            continue
    try:
        return ImageFont.load_default(size=tamanho)
    except TypeError:
        return ImageFont.load_default()


def abrir_imagem(path):
    """Abre respeitando a orientação EXIF e converte para sRGB quando houver perfil ICC.
    Devolve (rgb, alfa_ou_None)."""
    im = Image.open(path)
    im = ImageOps.exif_transpose(im)
    icc = im.info.get("icc_profile")
    if icc and im.mode in ("RGB", "RGBA", "CMYK"):
        try:
            import io
            from PIL import ImageCms
            src = ImageCms.ImageCmsProfile(io.BytesIO(icc))
            dst = ImageCms.createProfile("sRGB")
            modo = "RGBA" if im.mode == "RGBA" else "RGB"
            im = ImageCms.profileToProfile(im, src, dst, outputMode=modo)
        except Exception:
            pass
    alfa = None
    if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
        im = im.convert("RGBA")
        a = im.getchannel("A")
        if a.getextrema()[0] < 250:  # há transparência de verdade
            alfa = a
    return im.convert("RGB"), alfa


class FiltroSaida:
    """Silencia as linhas 'OK: .../_tmp-...' que as bibliotecas imprimem nas threads
    (deixa o console limpo e não expõe a ordem das gerações)."""

    def __init__(self, alvo):
        self.alvo = alvo
        self.trava = threading.Lock()
        self.buf = ""

    def write(self, s):
        with self.trava:
            self.buf += s
            while "\n" in self.buf:
                linha, self.buf = self.buf.split("\n", 1)
                if "_tmp-" in linha:
                    continue
                self.alvo.write(linha + "\n")
        return len(s)

    def flush(self):
        self.alvo.flush()


# ------------------------------------------------- preparo da referência (capa)

def _dilatar_eixo(m, k, eixo):
    """Dilatação binária 1D de largura k (ímpar) por soma acumulada — O(n), qualquer k."""
    r = k // 2
    pad = [(0, 0), (0, 0)]
    pad[eixo] = (r + 1, r)
    c = np.cumsum(np.pad(m.astype(np.int32), pad), axis=eixo)
    n = m.shape[eixo]
    if eixo == 0:
        return (c[k:k + n] - c[:n]) > 0
    return (c[:, k:k + n] - c[:, :n]) > 0


def _filtro(mask, tamanho, maximo):
    """Dilatação (maximo=True) ou erosão binária com janela quadrada tamanho x tamanho."""
    m = mask if maximo else ~mask
    m = _dilatar_eixo(_dilatar_eixo(m, tamanho, 0), tamanho, 1)
    return m if maximo else ~m


def _propagar(semente, passavel):
    """Inundação: espalha 'semente' por trechos contínuos de 'passavel' (linhas e colunas)
    até estabilizar. Equivale a um flood fill 4-conexo, só com numpy."""
    def linhas(R, P):
        H, W = P.shape
        z = np.zeros((H, 1), bool)
        Pp = np.concatenate([z, P], 1).ravel()
        Rp = np.concatenate([z, R], 1).ravel()
        inicio = Pp & ~np.concatenate([[False], Pp[:-1]])
        rid = np.cumsum(inicio) * Pp
        tem = np.bincount(rid[Rp & Pp], minlength=int(rid.max()) + 1) > 0
        tem[0] = False
        return tem[rid].reshape(H, W + 1)[:, 1:]

    R = semente & passavel
    n = int(R.sum())
    for _ in range(1000):
        R = linhas(R, passavel)
        R = linhas(R.T, passavel.T).T
        m = int(R.sum())
        if m == n:
            break
        n = m
    return R


def _grade_norm(x0, y0, w, h, escala, W, H):
    """Centros dos pixels de uma grade reduzida, em coordenadas normalizadas (-1..1)
    da imagem ORIGINAL — o modelo de fundo vale nas duas passadas."""
    xs = x0 + (np.arange(w) + 0.5) / escala - 0.5
    ys = y0 + (np.arange(h) + 0.5) / escala - 0.5
    X = (xs / max(W - 1, 1) * 2 - 1).astype(np.float32)
    Y = (ys / max(H - 1, 1) * 2 - 1).astype(np.float32)
    return np.meshgrid(X, Y)


_GRAU = 4
_TERMOS = [(i, j) for i in range(_GRAU + 1) for j in range(_GRAU + 1 - i)]


def _avaliar_fundo(coef, X, Y):
    px, py = [np.ones_like(X)], [np.ones_like(Y)]
    for _ in range(_GRAU):
        px.append(px[-1] * X)
        py.append(py[-1] * Y)
    B = np.zeros(X.shape + (3,), np.float32)
    for k, (i, j) in enumerate(_TERMOS):
        termo = px[i] * py[j]
        for c in range(3):
            B[..., c] += np.float32(coef[k, c]) * termo
    return B


def _ajustar_fundo(a, X, Y):
    """Modelo suave do fundo de estúdio (polinômio 2D de grau 4 por canal), ajustado
    primeiro nas bordas e refinado excluindo o que difere dele."""
    h, w, _ = a.shape
    b = max(3, int(0.03 * min(h, w)))
    fundo = np.zeros((h, w), bool)
    fundo[:b] = fundo[-b:] = True
    fundo[:, :b] = fundo[:, -b:] = True
    coef = None
    t = sig = 0.0
    for _ in range(4):
        idx = np.flatnonzero(fundo.ravel())
        if idx.size < 50:
            break
        if idx.size > 60000:
            idx = idx[:: idx.size // 60000]
        A = np.stack([(X.ravel()[idx] ** i) * (Y.ravel()[idx] ** j) for i, j in _TERMOS], -1)
        coef = np.stack([np.linalg.lstsq(A, a[..., c].ravel()[idx], rcond=None)[0] for c in range(3)], -1)
        B = _avaliar_fundo(coef, X, Y)
        D = np.abs(a - B).max(-1)
        sig = float(np.median(D[fundo]) * 1.4826 + 0.5)
        t = max(7.0, 3.0 * sig)
        fundo = ~_filtro(D > t, 7, True)
    return coef, t, sig


def _segmentar(a, B, t, glim=12.0):
    """Produto = o que a inundação a partir da borda NÃO alcança, menos as sombras.
    (1) A inundação anda por fundo (cor igual ao modelo); o que fica cercado pelo
        produto (vãos, vidro) continua sendo produto — nada é apagado por dentro.
    (2a) Sombra na parede (modelos de parede): a inundação continua só por regiões
        largas e muito lisas, mais escuras que o fundo e neutras.
    (2b) Sombra no chão: em cada coluna, de baixo para cima, sai o trecho contínuo mais
        escuro que o fundo, neutro e suave; para no primeiro pixel que não é sombra
        (borda nítida, preto do pé de borracha, cor). Aqui não anda de lado, para não
        entrar no cromado claro, que localmente parece sombra.
    Sombra de contorno nítido (projetada perto do produto) pode ficar: conferir sempre.
    Calibrado para o produto com ~720 px no maior lado (glim em níveis por pixel)."""
    L = a.mean(-1)
    Lb = np.maximum(B.mean(-1), 1.0)
    D = np.abs(a - B).max(-1)
    croma = a.max(-1) - a.min(-1)
    p = np.pad(L, 1, mode="edge")
    Ls = sum(p[1 + dy:p.shape[0] - 1 + dy, 1 + dx:p.shape[1] - 1 + dx]
             for dy in (-1, 0, 1) for dx in (-1, 0, 1)) / 9.0
    g = np.maximum(np.abs(np.diff(Ls, axis=0, prepend=Ls[:1])),
                   np.abs(np.diff(Ls, axis=1, prepend=Ls[:, :1])))
    fundo = D <= t
    sem = np.zeros_like(fundo)
    sem[0] = sem[-1] = True
    sem[:, 0] = sem[:, -1] = True
    R = _propagar(sem, _filtro(fundo, 3, False))  # vedação: frestas de 1 px não deixam passar
    for _ in range(2):  # devolve à inundação a borda que a vedação tirou
        R = _filtro(R, 3, True) & fundo
    r = L / Lb
    # (2a) sombra projetada no fundo (modelos de parede): só regiões LARGAS e muito lisas;
    # corredores estreitos (< 9 px) não deixam passar, então o cromado claro não é invadido
    lisa = (r < 0.99) & (r > 0.25) & (croma < 15) & (g < 4.5)
    R2 = _propagar(R, _filtro(R | lisa, 9, False) | R)
    for _ in range(4):
        R2 = _filtro(R2, 3, True) & (R | lisa)
    R = R | R2
    sombra = (r < 0.99) & (r > 0.20) & (croma < 20) & (g < glim)
    livre = R | sombra
    corrida = np.flipud(np.cumprod(np.flipud(livre), axis=0)).astype(bool)
    return ~(R | _suavizar_chao(corrida, R))


def _suavizar_chao(corrida, R, janela=9):
    """Tira os 'entalhes' que a varredura por coluna pode abrir no contorno de baixo: na
    zona do chão (12% de baixo do produto), se a varredura de uma coluna subiu mais que a
    mediana das vizinhas, o trecho a mais volta a ser produto. Só devolve, nunca tira
    (na dúvida, fica o produto)."""
    H, W = corrida.shape
    prod = ~(R | corrida)
    linhas = np.flatnonzero(prod.any(1))
    if linhas.size < 2:
        return corrida
    y_chao = linhas[-1] - 0.12 * (linhas[-1] - linhas[0])
    topo = (H - corrida.sum(0)).astype(np.float32)
    topo[(topo <= y_chao) | (topo >= H)] = np.nan  # coluna fora do chão: não mexe
    if np.all(np.isnan(topo)):
        return corrida
    h = janela // 2
    jan = np.lib.stride_tricks.sliding_window_view(np.pad(topo, h, constant_values=np.nan), janela)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        med = np.nanmedian(jan, axis=1)
    novo = corrida.copy()
    for x in np.flatnonzero(~np.isnan(topo) & ((~np.isnan(jan)).sum(1) > h)):
        m, t = int(round(med[x])), int(topo[x])
        if m > t:
            novo[t:m, x] = False
    return novo


def _componentes(mask, frac_min=0.02):
    """Mantém as partes grandes do produto (descarta pontinhos soltos no fundo)."""
    aberto = _filtro(_filtro(mask, 5, False), 5, True)
    restante = aberto.copy()
    comps = []
    for _ in range(200):
        if not restante.any():
            break
        semente = np.zeros_like(restante)
        semente.flat[int(np.argmax(restante))] = True
        c = _propagar(semente, restante)
        comps.append((int(c.sum()), c))
        restante &= ~c
    if not comps:
        return mask
    maior = max(a for a, _ in comps)
    manter = np.zeros_like(mask)
    for a_, c in comps:
        if a_ >= frac_min * maior:
            manter |= c
    # devolve as partes finas (abertura as remove) que encostam nas partes mantidas
    return mask & _filtro(manter, 13, True)


def _bbox(mask):
    ys = np.flatnonzero(mask.any(1))
    xs = np.flatnonzero(mask.any(0))
    if ys.size == 0:
        return None
    return int(xs[0]), int(ys[0]), int(xs[-1]) + 1, int(ys[-1]) + 1


def _ruido_faixa(D, t_min):
    faixa = np.zeros(D.shape, bool)
    b = max(3, int(0.02 * min(D.shape)))
    faixa[:b] = faixa[-b:] = True
    faixa[:, :b] = faixa[:, -b:] = True
    return float(np.clip(3.0 * (np.median(D[faixa]) * 1.4826 + 0.5), t_min, 3 * t_min))


def _alfa_local(im, alvo_lado):
    """Sem API. (1) passada grossa: modelo do fundo de estúdio + caixa do produto;
    (2) segmentação com o produto a ~720 px (escala em que a inundação foi calibrada);
    (3) escala final: a máscara é ampliada e só a faixa da borda é aparada contra o fundo.
    Devolve (rgb_fino, alfa_fino, info) ou levanta ValueError."""
    W, H = im.size
    s0 = min(1.0, 900.0 / max(W, H))
    peq = im.resize((max(1, round(W * s0)), max(1, round(H * s0))), Image.LANCZOS)
    a0 = np.asarray(peq).astype(np.float32)
    X0, Y0 = _grade_norm(0, 0, a0.shape[1], a0.shape[0], s0, W, H)
    coef, t0, sig = _ajustar_fundo(a0, X0, Y0)
    if coef is None or sig > 12:
        raise ValueError("fundo não é liso (ruído %.1f): não dá para separar o produto localmente" % sig)
    m0 = _componentes(_segmentar(a0, _avaliar_fundo(coef, X0, Y0), t0))
    bb = _bbox(m0)
    if bb is None or m0.mean() > 0.9:
        raise ValueError("produto não encontrado contra o fundo")
    x0, y0, x1, y1 = [v / s0 for v in bb]
    longo = max(x1 - x0, y1 - y0)
    margem = 0.05 * longo + 8 / s0
    cx0, cy0 = max(0, int(x0 - margem)), max(0, int(y0 - margem))
    cx1, cy1 = min(W, int(math.ceil(x1 + margem))), min(H, int(math.ceil(y1 + margem)))
    caixa = (cx0, cy0, cx1, cy1)
    regiao = im.crop(caixa)

    # (2) segmentação na escala de trabalho
    sw = 720.0 / longo
    ww, wh = max(1, round((cx1 - cx0) * sw)), max(1, round((cy1 - cy0) * sw))
    aw = np.asarray(regiao.resize((ww, wh), Image.LANCZOS)).astype(np.float32)
    Xw, Yw = _grade_norm(cx0, cy0, ww, wh, sw, W, H)
    Bw = _avaliar_fundo(coef, Xw, Yw)
    tw = _ruido_faixa(np.abs(aw - Bw).max(-1), t0)
    mw = _componentes(_segmentar(aw, Bw, tw))
    bbw = _bbox(mw)
    if bbw is None:
        raise ValueError("produto não encontrado na passada de trabalho")

    # (3) escala final + aparo da borda (só remove fundo; nunca acrescenta)
    s1 = alvo_lado / (max(bbw[2] - bbw[0], bbw[3] - bbw[1]) / sw)
    fw, fh = max(1, round((cx1 - cx0) * s1)), max(1, round((cy1 - cy0) * s1))
    fino = regiao.resize((fw, fh), Image.LANCZOS)
    a1 = np.asarray(fino).astype(np.float32)
    X1, Y1 = _grade_norm(cx0, cy0, fw, fh, s1, W, H)
    D1 = np.abs(a1 - _avaliar_fundo(coef, X1, Y1)).max(-1)
    t1 = _ruido_faixa(D1, t0)
    # alfa suave: a máscara de trabalho, desfocada e ampliada, anti-serrilha o contorno
    A = np.asarray(Image.fromarray(mw.astype(np.uint8) * 255).filter(ImageFilter.GaussianBlur(1.0))
                   .resize((fw, fh), Image.BILINEAR)).astype(np.float32) / 255.0
    M = A > 0.5
    # faixa interna da borda: só aqui a escala final pode tirar pixels (nunca no miolo)
    k = 2 * int(math.ceil(s1 / sw)) + 1
    faixa = M & ~_filtro(M, 2 * k + 1, False)
    fora = ~M
    R = _propagar(fora, fora | (faixa & (D1 <= t1)))
    m1 = M & ~R
    if not m1.any():
        raise ValueError("produto não encontrado na escala final")
    # Em foto de estúdio o produto nunca encosta na borda da foto. Se encosta, a inundação não
    # separou o fundo (mesa, parede, sombra, produto claro no fundo claro) ou o produto está
    # cortado pelo quadro: a capa sairia com pedaços de cenário ou do produto faltando.
    lados = [n for n, t in (("esquerda", cx0 == 0 and m1[:, 0].any()), ("topo", cy0 == 0 and m1[0].any()),
                            ("direita", cx1 == W and m1[:, -1].any()), ("base", cy1 == H and m1[-1].any())) if t]
    if lados:
        raise ValueError("o recorte encosta na borda da foto (%s): fundo que não é de estúdio liso "
                         "(mesa, parede, sombra) ou produto cortado pelo quadro" % ", ".join(lados))
    # fora da máscara, o que é fundo vira branco puro (sem auréola cinza); o resto suaviza
    alfa = np.where((R & ~fora) | (fora & (D1 <= t1)), 0.0, np.clip((A - 0.5) * 3.0 + 0.5, 0.0, 1.0))
    alfa = Image.fromarray((alfa * 255 + 0.5).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.5))
    bx0, by0, bx1, by1 = _bbox(m1)
    info = {"ruido_fundo": round(sig, 2), "limiar": round(t1, 1),
            "bbox_original": [int(cx0 + bx0 / s1), int(cy0 + by0 / s1),
                              int(cx0 + bx1 / s1), int(cy0 + by1 / s1)]}
    avisos = []
    if s1 > 1.5:
        avisos.append("referência de baixa resolução (ampliada %.1fx)" % s1)
    # espelho inteiro ocupa >= ~37% da própria caixa; bem menos que isso = a inundação comeu
    # partes do produto (típico de produto branco em fundo claro)
    preenchimento = m1.sum() / float((bx1 - bx0) * (by1 - by0))
    info["preenchimento"] = round(float(preenchimento), 3)
    if preenchimento < 0.2:
        avisos.append("recorte suspeito: o produto ocupa só %.0f%% da própria caixa (partes podem ter "
                      "sido apagadas); conferir, ou usar --recorte birefnet" % (100 * preenchimento))
    if avisos:
        info["aviso"] = "; ".join(avisos)
    return fino, alfa, info


def _alfa_birefnet(im, pasta):
    """Recorte por IA (BiRefNet v2 no fal). Devolve o alfa na resolução original."""
    entrada = os.path.join(pasta, "_birefnet-%s.png" % uuid.uuid4().hex[:8])
    peq = im.copy()
    peq.thumbnail((2048, 2048), Image.LANCZOS)
    peq.save(entrada)
    try:
        saida = estudio_fal.recortar(entrada, pasta)
        alfa = Image.open(saida).convert("RGBA").getchannel("A").resize(im.size, Image.BILINEAR)
        os.remove(saida)
    finally:
        os.remove(entrada)
    return alfa


def _escalar_por_alfa(im, alfa, alvo_lado):
    m = np.asarray(alfa) > 127
    bb = _bbox(m)
    if bb is None:
        raise ValueError("alfa vazio: nenhum pixel de produto")
    x0, y0, x1, y1 = bb
    s1 = alvo_lado / max(x1 - x0, y1 - y0)
    caixa = (x0, y0, x1, y1)
    fw, fh = max(1, round((x1 - x0) * s1)), max(1, round((y1 - y0) * s1))
    info = {"bbox_original": list(bb)}
    avisos = []
    if s1 > 1.5:
        avisos.append("referência de baixa resolução (ampliada %.1fx)" % s1)
    W, H = alfa.size
    lados = [n for n, t in (("esquerda", x0 == 0), ("topo", y0 == 0), ("direita", x1 == W), ("base", y1 == H)) if t]
    if lados:  # ex.: cabo que sai do quadro; na capa ele terminaria no ar
        avisos.append("o produto encosta na borda da foto (%s): pode estar cortado pelo quadro "
                      "ou com fundo junto; conferir" % ", ".join(lados))
    if avisos:
        info["aviso"] = "; ".join(avisos)
    return im.crop(caixa).resize((fw, fh), Image.LANCZOS), alfa.crop(caixa).resize((fw, fh), Image.LANCZOS), info


def _compor_capa(rgb, alfa, lado, ocupacao):
    """Produto inteiro, centrado, sobre branco puro, maior lado = ocupacao x lado."""
    m = np.asarray(alfa) > 127
    x0, y0, x1, y1 = _bbox(m)
    rgb, alfa = rgb.crop((x0, y0, x1, y1)), alfa.crop((x0, y0, x1, y1))
    alvo = round(lado * ocupacao)
    longo = max(rgb.size)
    if abs(longo - alvo) > 0.01 * alvo:
        k = alvo / longo
        novo = (max(1, round(rgb.size[0] * k)), max(1, round(rgb.size[1] * k)))
        rgb, alfa = rgb.resize(novo, Image.LANCZOS), alfa.resize(novo, Image.LANCZOS)
    a = np.asarray(alfa).astype(np.float32)[..., None] / 255.0
    px = np.asarray(rgb).astype(np.float32) * a + 255.0 * (1.0 - a)
    prod = Image.fromarray(np.clip(px + 0.5, 0, 255).astype(np.uint8))
    capa = Image.new("RGB", (lado, lado), (255, 255, 255))
    mascara = Image.new("L", (lado, lado), 0)
    pos = ((lado - prod.size[0]) // 2, (lado - prod.size[1]) // 2)
    capa.paste(prod, pos)
    mascara.paste(alfa, pos)
    return capa, mascara, round(max(prod.size) / lado, 3)


def _conferencia(original, capa, bbox, out, altura=900):
    """Original (com a caixa detectada em vermelho) ao lado da capa preparada."""
    o = original.copy()
    k = altura / o.size[1]
    o = o.resize((max(1, round(o.size[0] * k)), altura), Image.LANCZOS)
    if bbox:
        ImageDraw.Draw(o).rectangle([v * k for v in bbox], outline=(230, 0, 0), width=3)
    c = capa.resize((altura, altura), Image.LANCZOS)
    folha = Image.new("RGB", (o.size[0] + c.size[0] + 30, altura + 50), (200, 200, 200))
    folha.paste(o, (10, 40))
    folha.paste(c, (o.size[0] + 20, 40))
    d = ImageDraw.Draw(folha)
    f = fonte(22, True)
    d.text((10, 8), "ORIGINAL (caixa detectada)", fill=(0, 0, 0), font=f)
    d.text((o.size[0] + 20, 8), "CAPA PREPARADA (fundo branco, 1:1)", fill=(0, 0, 0), font=f)
    folha.save(out)


def preparar_ref(path, pasta, idx, lado=LADO_CAPA, ocupacao=OCUPACAO_CAPA, recorte="local"):
    """Padroniza uma referência como capa do ML. Nunca retoca pixels do produto:
    só troca o fundo por branco, recorta, escala e centraliza."""
    os.makedirs(pasta, exist_ok=True)
    im, alfa_arquivo = abrir_imagem(path)
    alvo = round(lado * ocupacao)
    info = {"original": os.path.abspath(path), "tamanho_original": list(im.size),
            "lado": lado, "ocupacao_alvo": ocupacao}
    if alfa_arquivo is not None:
        info["metodo"] = "alfa do arquivo"
        rgb, alfa, extra = _escalar_por_alfa(im, alfa_arquivo, alvo)
    elif recorte == "birefnet":
        info["metodo"] = "birefnet (fal)"
        rgb, alfa, extra = _escalar_por_alfa(im, _alfa_birefnet(im, pasta), alvo)
    else:
        info["metodo"] = "local (modelo de fundo + inundação)"
        rgb, alfa, extra = _alfa_local(im, alvo)
    info.update(extra)
    capa, mascara, ocup = _compor_capa(rgb, alfa, lado, ocupacao)
    info["ocupacao_medida"] = ocup
    base = "ref-%d" % idx
    info["usada"] = os.path.abspath(os.path.join(pasta, base + "-capa.png"))
    capa.save(info["usada"], optimize=True)
    mascara.save(os.path.join(pasta, base + "-mascara.png"))
    info["conferencia"] = os.path.abspath(os.path.join(pasta, base + "-conferencia.png"))
    vista = im
    if alfa_arquivo is not None:  # transparente aparece branco na conferência
        vista = Image.composite(im, Image.new("RGB", im.size, (255, 255, 255)), alfa_arquivo)
    _conferencia(vista, capa, info.get("bbox_original"), info["conferencia"])
    return info


# ----------------------------------------------------------------- geração

def parse_motores(txt):
    motores, vistos = [], set()
    for item in [x.strip() for x in txt.split(",") if x.strip()]:
        if item.startswith("gemini:"):
            modelo = item.split(":", 1)[1].strip()
            if not modelo:
                raise SystemExit("Motor sem modelo: use gemini:<model-id> (veja --listar-modelos).")
            m = {"id": "gemini:" + modelo, "tipo": "gemini", "modelo": modelo}
        elif item == "kontext":
            m = {"id": "kontext", "tipo": "kontext", "modelo": estudio_fal.MODELO_KONTEXT}
        elif item == "seedream":
            m = {"id": "seedream", "tipo": "seedream", "modelo": estudio_fal.MODELO_SEEDREAM}
        else:
            raise SystemExit("Motor desconhecido: %r (use gemini:<model-id>, kontext ou seedream)" % item)
        if m["id"] not in vistos:
            vistos.add(m["id"])
            motores.append(m)
    if not motores:
        raise SystemExit("Nenhum motor em --motores.")
    return motores


def parametros_motor(motor, aspecto, n_refs):
    p = {}
    if motor["tipo"] == "gemini":
        p["aspect_ratio"] = aspecto
        if aspecto not in GEMINI_ASPECTOS:
            p["aviso"] = "aspecto %s pode não ser aceito pelo Gemini" % aspecto
        p["refs_enviadas"] = n_refs
        p["ordem"] = "imagens antes do texto"
    elif motor["tipo"] == "kontext":
        p["aspect_ratio"] = aspecto if aspecto in KONTEXT_ASPECTOS else mais_proximo(aspecto, KONTEXT_ASPECTOS)
        if p["aspect_ratio"] != aspecto:
            p["aviso"] = "Kontext não aceita %s; pedido %s" % (aspecto, p["aspect_ratio"])
        p["refs_enviadas"] = 1
    else:
        p["image_size"] = tamanho_seedream(aspecto)
        p["refs_enviadas"] = n_refs
    return p


def checar_credenciais(motores):
    erros = []
    if any(m["tipo"] == "gemini" for m in motores):
        try:
            gerar_imagem.load_cfg()
        except SystemExit as e:
            erros.append(str(e))
    if any(m["tipo"] in ("kontext", "seedream") for m in motores):
        try:
            estudio_fal.chave()
        except SystemExit as e:
            erros.append(str(e))
    if erros:
        raise SystemExit("Credenciais ausentes (nada foi gerado):\n- " + "\n- ".join(erros))


def simular_imagem(job, out):
    """Imagem fictícia: a referência preparada na proporção pedida, com um rótulo.
    Mostra o motor de propósito, para conferir o mapa.json no teste do fluxo."""
    r = razao(job["aspecto"])
    w, h = (1024, max(1, round(1024 / r))) if r >= 1 else (max(1, round(1024 * r)), 1024)
    cores = [(232, 240, 250), (250, 236, 228), (232, 248, 234), (246, 232, 246), (248, 246, 226)]
    tela = Image.new("RGB", (w, h), cores[job["motor_idx"] % len(cores)])
    base = Image.open(job["refs"][0]).convert("RGB")
    base.thumbnail((int(w * 0.8), int(h * 0.75)), Image.LANCZOS)
    tela.paste(base, ((w - base.size[0]) // 2, int(h * 0.04)))
    d = ImageDraw.Draw(tela)
    d.rectangle([0, h - 110, w, h], fill=(30, 30, 30))
    d.text((20, h - 100), "SIMULACAO (sem API)", fill=(255, 210, 0), font=fonte(30, True))
    d.text((20, h - 58), "%s | %s | #%d" % (job["motor"]["id"], job["receita"], job["k"]),
           fill=(255, 255, 255), font=fonte(26))
    tela.save(out)


def executar(job, out, simular):
    m = job["motor"]
    if simular:
        simular_imagem(job, out)
    elif m["tipo"] == "gemini":
        gerar_imagem.gerar(job["prompt"], out, job["refs"], job["aspecto"], m["modelo"])
    elif m["tipo"] == "kontext":
        estudio_fal.rerender_kontext(job["refs"][0], out, job["prompt"],
                                     aspect_ratio=job["params"]["aspect_ratio"], seed=job["seed"])
    else:
        estudio_fal.rerender_seedream(job["refs"], out, job["prompt"],
                                      image_size=job["params"]["image_size"], seed=job["seed"])
    with Image.open(out) as im:
        im.load()
        if im.mode in ("RGBA", "LA", "P"):
            im = im.convert("RGBA")
            fundo = Image.new("RGB", im.size, (255, 255, 255))
            fundo.paste(im, mask=im.getchannel("A"))
            im = fundo
        im = im.convert("RGB")
    im.save(out, "PNG")
    return im.size


_TRANSITORIO = re.compile(r"\b(429|500|502|503|504)\b|timed out|timeout|UNAVAILABLE|RESOURCE_EXHAUSTED|"
                          r"temporar|Connection|reset by peer", re.I)


def rodar_job(job, out, simular):
    t0 = time.time()
    for tentativa in (1, 2):
        try:
            tam = executar(job, out, simular)
            return {"ok": True, "tamanho": list(tam), "segundos": round(time.time() - t0, 1)}
        except (Exception, SystemExit) as e:
            msg = " ".join((str(e) or e.__class__.__name__).split())
            if os.path.exists(out):
                try:
                    os.remove(out)
                except OSError:
                    pass
            if tentativa == 1 and _TRANSITORIO.search(msg):
                time.sleep(8 + _rand.random() * 4)
                continue
            return {"ok": False, "erro": msg[:600], "segundos": round(time.time() - t0, 1)}


# ------------------------------------------------------------------ prancha

def montar_prancha(itens, ref, titulo, aspecto, out, cel=400):
    """itens: [(rótulo, caminho)]. A 1ª célula é a REF (mesma escala), sem nome de motor."""
    r = razao(aspecto)
    cw, ch = (cel, max(1, round(cel / r))) if r >= 1 else (max(1, round(cel * r)), cel)
    celulas = ([("REF", ref)] if ref else []) + list(itens)
    n = len(celulas)
    cols = max(1, min(5, math.ceil(math.sqrt(n))))
    linhas = math.ceil(n / cols)
    pad, faixa, topo = 14, 46, 78
    W = pad + cols * (cw + pad)
    W = max(W, 900)
    H = topo + linhas * (faixa + ch + pad) + pad + 30
    folha = Image.new("RGB", (W, H), (226, 226, 226))
    d = ImageDraw.Draw(folha)
    ft, fr, fp = fonte(22, True), fonte(34, True), fonte(16)
    t = titulo
    while d.textlength(t, font=ft) > W - 2 * pad and len(t) > 10:
        t = t[:-2]
    if t != titulo:
        t = t.rstrip() + "..."
    d.text((pad, 14), t, fill=(20, 20, 20), font=ft)
    d.text((pad, 46), "%s  |  Rótulos embaralhados. O mapa (mapa.json) só se abre depois do veredito."
           % datetime.date.today().isoformat(), fill=(70, 70, 70), font=fp)
    for i, (rot, p) in enumerate(celulas):
        c, l = i % cols, i // cols
        x0 = pad + c * (cw + pad)
        y0 = topo + l * (faixa + ch + pad)
        d.rectangle([x0, y0 + faixa, x0 + cw - 1, y0 + faixa + ch - 1], fill=(255, 255, 255))
        with Image.open(p) as im:
            im = im.convert("RGB")
            im.thumbnail((cw, ch), Image.LANCZOS)
            folha.paste(im, (x0 + (cw - im.size[0]) // 2, y0 + faixa + (ch - im.size[1]) // 2))
        d.text((x0 + 4, y0 + 4), rot, fill=(170, 0, 0) if rot == "REF" else (0, 0, 0), font=fr)
    folha.save(out)
    return out


# --------------------------------------------------------------- receitas

def achar_receitas(itens):
    arquivos = []
    for it in itens:
        if os.path.isdir(it):
            for nome in sorted(os.listdir(it)):
                if nome.startswith("_") or not nome.lower().endswith(".txt"):
                    continue
                arquivos.append(os.path.join(it, nome))
        elif os.path.isfile(it):
            if os.path.basename(it).startswith("_"):
                print("  (ignorado: %s começa com '_')" % it)
                continue
            arquivos.append(it)
        else:
            raise SystemExit("Receita não encontrada: %s" % it)
    vistos, out = set(), []
    for a in arquivos:
        k = os.path.abspath(a)
        if k not in vistos:
            vistos.add(k)
            out.append(k)
    if not out:
        raise SystemExit("Nenhuma receita .txt encontrada em: %s" % ", ".join(itens))
    return out


def achar_moldura(arg, receitas_args):
    if arg:
        return arg
    for it in receitas_args:  # pasta passada, ou a pasta do .txt passado
        pasta = it if os.path.isdir(it) else os.path.dirname(os.path.abspath(it))
        if os.path.isfile(os.path.join(pasta, "_moldura.txt")):
            return os.path.join(pasta, "_moldura.txt")
    return os.path.join(REPO, "receitas", "_moldura.txt")


def pasta_padrao(produto, hoje):
    """ensaios/_versoes/<data>-<slug-do-produto>/, com -2, -3... se já existir."""
    base = os.path.join(REPO, "ensaios", "_versoes", "%s-%s" % (hoje, slug(produto)))
    saida, k = base, 2
    while os.path.exists(saida):
        saida, k = "%s-%d" % (base, k), k + 1
    return saida


# ------------------------------------------------------------------ listar

def listar_modelos():
    key, padrao = gerar_imagem.load_cfg()
    url = "https://generativelanguage.googleapis.com/v1beta/models?pageSize=1000"
    modelos, token = [], None
    while True:
        req = urllib.request.Request(url + ("&pageToken=%s" % token if token else ""))
        req.add_header("x-goog-api-key", key)
        try:
            data = json.loads(urllib.request.urlopen(req, timeout=60).read().decode())
        except urllib.error.HTTPError as e:
            raise SystemExit("Erro HTTP %s: %s" % (e.code, e.read().decode(errors="replace")[:400]))
        modelos += data.get("models", [])
        token = data.get("nextPageToken")
        if not token:
            break
    achados = [m for m in modelos if "image" in m.get("name", "").lower()
               and "generateContent" in m.get("supportedGenerationMethods", [])]
    if not achados:
        print("Nenhum modelo Gemini de imagem com generateContent nesta chave.")
        return
    print("Modelos Gemini que geram imagem (use em --motores como gemini:<id>):")
    for m in sorted(achados, key=lambda m: m["name"]):
        mid = m["name"].split("/", 1)[-1]
        print("  gemini:%-40s %s%s" % (mid, m.get("displayName", ""), "  [padrão do config]" if mid == padrao else ""))


# -------------------------------------------------------------------- main


LADO_CEGO = 1024  # todas as candidatas saem com o mesmo lado curto e sem metadados


def _cegar_arquivo(origem, destino):
    """Padroniza a candidata para o julgamento cego: o Seedream devolve 1280 px
    e os outros motores 1024, e o tamanho ou os metadados do arquivo
    revelariam o motor. O tamanho original fica só no mapa.json."""
    im = Image.open(origem)
    im.load()
    curto = min(im.size)
    if curto != LADO_CEGO:
        k = LADO_CEGO / float(curto)
        im = im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.LANCZOS)
    im.convert("RGB").save(destino, "PNG")
    os.remove(origem)

def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--produto")
    ap.add_argument("--ref", action="append", default=[])
    ap.add_argument("--receitas", nargs="+", default=[os.path.join(REPO, "receitas")])
    ap.add_argument("--moldura")
    ap.add_argument("--motores", default=MOTORES_PADRAO)
    ap.add_argument("--n", type=int, default=4)
    ap.add_argument("--aspecto", default="1:1")
    ap.add_argument("--saida")
    ap.add_argument("--sem-preparo", action="store_true")
    ap.add_argument("--recorte", choices=["local", "birefnet"], default="local")
    ap.add_argument("--lado", type=int, default=LADO_CAPA, help=argparse.SUPPRESS)
    ap.add_argument("--ocupacao", type=float, default=OCUPACAO_CAPA, help=argparse.SUPPRESS)
    ap.add_argument("--so-preparo", action="store_true")
    ap.add_argument("--simular", action="store_true")
    ap.add_argument("--paralelo", type=int, default=4)
    ap.add_argument("--listar-modelos", action="store_true")
    a = ap.parse_args()

    if a.listar_modelos:
        listar_modelos()
        return
    if not a.produto or not a.produto.strip():
        ap.error("--produto é obrigatório")
    if not a.ref:
        ap.error("informe ao menos uma --ref")
    for r in a.ref:
        if not os.path.isfile(r):
            raise SystemExit("Referência não encontrada: %s" % r)
    if not re.fullmatch(r"\d+:\d+", a.aspecto) or razao(a.aspecto) <= 0:
        ap.error("--aspecto no formato W:H (ex.: 1:1, 4:5, 9:16)")
    if a.n < 1:
        ap.error("--n precisa ser >= 1")
    if not 0.5 <= a.ocupacao <= 1.0:
        ap.error("--ocupacao entre 0.5 e 1.0")

    produto = " ".join(a.produto.split())
    motores = parse_motores(a.motores)
    if a.simular and a.recorte == "birefnet":
        print("  (--simular não chama API: recorte local no lugar do birefnet)")
        a.recorte = "local"
    if not a.so_preparo:
        receitas = achar_receitas(a.receitas)
        moldura_path = achar_moldura(a.moldura, a.receitas)
        if not os.path.isfile(moldura_path):
            raise SystemExit("Moldura não encontrada: %s" % moldura_path)
        moldura = ler_texto(moldura_path)
        faltam = [m for m in ("{produto}", "{cena}") if m not in moldura]
        if faltam:
            raise SystemExit("Moldura %s sem os marcadores %s — abortado." % (moldura_path, " e ".join(faltam)))
        cenas = {}
        for rp in receitas:
            txt = " ".join(ler_texto(rp).split())
            if not txt:
                raise SystemExit("Receita vazia: %s" % rp)
            cenas[rp] = txt
        if not a.simular:
            checar_credenciais(motores)

    # pasta de saída
    hoje = datetime.date.today().isoformat()
    if a.saida:
        saida = os.path.abspath(a.saida)
        if os.path.isdir(saida) and os.listdir(saida):
            raise SystemExit("A pasta de saída já existe e não está vazia: %s" % saida)
    else:
        saida = pasta_padrao(produto, hoje)
    os.makedirs(saida, exist_ok=True)
    pasta_refs = os.path.join(saida, "refs")
    os.makedirs(pasta_refs, exist_ok=True)

    # referências
    print("Saída: %s" % saida)
    refs_info = []
    for i, r in enumerate(a.ref, 1):
        if a.sem_preparo:
            refs_info.append({"original": os.path.abspath(r), "usada": os.path.abspath(r), "metodo": "sem preparo"})
            print("  ref %d: %s (sem preparo)" % (i, r))
            continue
        try:
            info = preparar_ref(r, pasta_refs, i, a.lado, a.ocupacao, a.recorte)
        except ValueError as e:
            if not a.simular:
                raise SystemExit("Preparo da ref %d falhou (%s): %s\n"
                                 "Tente --recorte birefnet ou --sem-preparo." % (i, r, e))
            # --simular não roda o birefnet: segue com a ref crua só para testar o fluxo
            aviso = ("preparo local falhou (%s); o ensaio real pararia aqui: use --recorte birefnet "
                     "ou um PNG recortado" % e)
            refs_info.append({"original": os.path.abspath(r), "usada": os.path.abspath(r),
                              "metodo": "sem preparo (só na simulação)", "aviso": aviso})
            print("  ref %d: %s (SEM PREPARO, só na simulação)\n         AVISO: %s" % (i, r, aviso))
            continue
        refs_info.append(info)
        print("  ref %d preparada: %s (ocupação %.0f%%, método %s)"
              % (i, info["usada"], 100 * info["ocupacao_medida"], info["metodo"]))
        print("         conferir: %s" % info["conferencia"])
        if info.get("aviso"):
            print("         AVISO: %s" % info["aviso"])
    refs_usadas = [x["usada"] for x in refs_info]

    manifesto = {
        "ferramenta": "ferramentas/ensaio.py",
        "criado_em": datetime.datetime.now().isoformat(timespec="seconds"),
        "simulado": bool(a.simular),
        "produto": produto,
        "referencias": refs_info,
        "aspecto": a.aspecto,
        "n_por_motor": a.n,
        "saida": saida,
    }
    if a.so_preparo:
        manifesto["so_preparo"] = True
        with open(os.path.join(saida, "manifesto.json"), "w", encoding="utf-8") as f:
            json.dump(manifesto, f, ensure_ascii=False, indent=2)
        print("Só preparo: confira as referências acima antes de gerar.")
        return

    for m in motores:
        m["params"] = parametros_motor(m, a.aspecto, len(refs_usadas))
        m["custo_unit_usd"], m["custo_conhecido"] = custo_unit(m)
        if m["params"].get("aviso"):
            print("  AVISO %s: %s" % (m["id"], m["params"]["aviso"]))
        if m["tipo"] == "kontext" and len(refs_usadas) > 1:
            print("  AVISO kontext: usa só a 1ª referência.")
    total = len(receitas) * len(motores) * a.n
    previsto = sum(m["custo_unit_usd"] for m in motores) * a.n * len(receitas)
    print("Receitas: %d | motores: %d | n: %d | gerações: %d | custo estimado: ~US$ %.2f%s%s"
          % (len(receitas), len(motores), a.n, total, previsto,
             "" if all(m["custo_conhecido"] for m in motores) else " (há modelo com preço genérico)",
             " [SIMULAÇÃO: US$ 0]" if a.simular else ""))

    manifesto.update({
        "moldura": {"arquivo": os.path.abspath(moldura_path), "texto": moldura},
        "motores": [{k: m[k] for k in ("id", "tipo", "modelo", "params", "custo_unit_usd")} for m in motores],
        "receitas": [],
        "custo_estimado_usd": {"previsto": round(previsto, 2)},
        "aviso": "Rótulos -> motor estão em mapa.json; abrir só depois do veredito.",
    })
    mapa = {}
    pranchas = []
    gerado_usd = 0.0
    stdout_orig = sys.stdout
    sys.stdout = FiltroSaida(stdout_orig)
    nomes_usados = set()
    try:
        for ri, rp in enumerate(receitas):
            nome = base_nome = slug(os.path.splitext(os.path.basename(rp))[0])
            k_nome = 2
            while nome in nomes_usados:  # mesmo nome de arquivo em pastas diferentes
                nome, k_nome = "%s-%d" % (base_nome, k_nome), k_nome + 1
            nomes_usados.add(nome)
            letra = rotulo_letra(ri)
            pasta = os.path.join(saida, nome)
            os.makedirs(pasta, exist_ok=True)
            prompt = moldura.replace("{produto}", produto).replace("{cena}", cenas[rp])
            jobs = []
            for k in range(1, a.n + 1):  # intercalado por motor: APIs diferentes em paralelo
                for mi, m in enumerate(motores):
                    jobs.append({
                        "motor": m, "motor_idx": mi, "k": k, "receita": nome, "prompt": prompt,
                        "refs": refs_usadas[:1] if m["tipo"] == "kontext" else refs_usadas,
                        "aspecto": a.aspecto, "params": m["params"],
                        "seed": _rand.randrange(1, 2 ** 31 - 1) if m["tipo"] != "gemini" else None,
                        "tmp": os.path.join(pasta, "_tmp-%s.png" % uuid.uuid4().hex[:12]),
                    })
            print("[%s] %s: %d gerações..." % (letra, nome, len(jobs)))
            feitos = [0]
            trava = threading.Lock()

            def tarefa(job):
                res = rodar_job(job, job["tmp"], a.simular)
                with trava:
                    feitos[0] += 1
                    if not res["ok"]:
                        print("   falha (%s #%d): %s" % (job["motor"]["id"], job["k"], res["erro"][:300]))
                    if feitos[0] % max(1, len(jobs) // 4) == 0 or feitos[0] == len(jobs):
                        print("   %d/%d concluídas" % (feitos[0], len(jobs)))
                return res

            with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, a.paralelo)) as ex:
                resultados = list(ex.map(tarefa, jobs))

            ok = [(j, r) for j, r in zip(jobs, resultados) if r["ok"]]
            _rand.shuffle(ok)
            itens = []
            agora = time.time()
            for pos, (j, r) in enumerate(ok, 1):
                rot = "%s%d" % (letra, pos)
                final = os.path.join(pasta, rot + ".png")
                _cegar_arquivo(j["tmp"], final)
                os.utime(final, (agora, agora))  # a hora de término (ls -t) revelaria o motor
                mapa[rot] = {"motor": j["motor"]["id"], "modelo": j["motor"]["modelo"], "receita": nome,
                             "arquivo": os.path.relpath(final, saida).replace(os.sep, "/"),
                             "tentativa": j["k"], "seed": j["seed"], "tamanho": r["tamanho"]}
                itens.append((rot, final))
                if not a.simular:
                    gerado_usd += j["motor"]["custo_unit_usd"]
            if itens:
                titulo = "%s  |  receita: %s  |  %d candidatas" % (produto, nome, len(itens))
                pr = montar_prancha(itens, refs_usadas[0], titulo, a.aspecto,
                                    os.path.join(saida, "prancha-%s.png" % nome))
                pranchas.append(pr)
            manifesto["receitas"].append({
                "rotulos": letra, "nome": nome, "arquivo": rp, "cena": cenas[rp],
                "prompts": {m["id"]: prompt for m in motores},
                "geracoes": [{"motor": j["motor"]["id"], "tentativa": j["k"], "ok": r["ok"],
                              "erro": r.get("erro"), "segundos": r["segundos"], "seed": j["seed"],
                              "refs": j["refs"]} for j, r in sorted(zip(jobs, resultados),
                                                                     key=lambda x: (x[0]["motor_idx"], x[0]["k"]))],
                "candidatas": len(itens),
            })
            manifesto["custo_estimado_usd"]["gerado"] = round(gerado_usd, 2)
            with open(os.path.join(saida, "mapa.json"), "w", encoding="utf-8") as f:
                json.dump(mapa, f, ensure_ascii=False, indent=2)
            with open(os.path.join(saida, "manifesto.json"), "w", encoding="utf-8") as f:
                json.dump(manifesto, f, ensure_ascii=False, indent=2)
            print("   %d/%d candidatas -> %s" % (len(itens), len(jobs),
                                                 pranchas[-1] if itens else "(sem prancha: nenhuma geração ok)"))
    finally:
        sys.stdout = stdout_orig

    print("\nPronto.%s Custo estimado das gerações feitas: ~US$ %.2f"
          % (" (SIMULAÇÃO, nada foi cobrado.)" if a.simular else "", gerado_usd))
    print("Pranchas (%d):" % len(pranchas))
    for p in pranchas:
        print("  %s" % p)
    print("Manifesto: %s" % os.path.join(saida, "manifesto.json"))
    print("Mapa (abrir só depois do veredito): %s" % os.path.join(saida, "mapa.json"))
    if not pranchas:
        raise SystemExit("Nenhuma candidata gerada: veja as falhas acima e no manifesto.")


if __name__ == "__main__":
    main()
