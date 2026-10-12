# -*- coding: utf-8 -*-
"""Inspeção de imagens geradas — ferramentas do Fotógrafo da Gardie.

Uso:
  py inspecao_imagem.py diff  base.png nova.png [mascara.png]
      -> imprime % de pixels alterados. Se < 2%, a "edição" devolveu a
         mesma imagem (falhou) — trocar de estratégia, não reapresentar.
         Com mascara.png (branco = área editável), o % é relativo à ÁREA DA
         MÁSCARA — obrigatório em edição por máscara pequena (o % global é
         cego: máscara de 2% do quadro nunca passaria do limiar).
  py inspecao_imagem.py crops imagem.png pasta_saida/
      -> gera crops em resolução nativa: 4 quadrantes + centro ampliado.
         LER os crops das regiões críticas (aro/vidro, cabo, tomada).
  py inspecao_imagem.py grade imagem.png saida.png [passo] [zoom] [x0,y0,x1,y1]
      -> sobrepõe uma grade rotulada a cada `passo` px (padrão 50; linha forte a
         cada 5) para MEDIR proporções lendo coordenadas. `zoom` amplia antes de
         desenhar (padrão 1; os rótulos continuam em px da imagem original) e o
         recorte opcional limita a região (coordenadas originais).
  py inspecao_imagem.py colagem capa.png x0,y0,x1,y1 candidata.png x0,y0,x1,y1 escala [saida.png]
      -> procura o trecho cromado da capa (1ª caixa; no Classique Lux, o miolo
         do sino) só dentro do mesmo trecho da candidata (2ª caixa, com folga),
         em escalas de 0,8 a 1,2 × `escala` (Ø da base na candidata ÷ Ø da base
         na capa, lidos com `grade`), normal e espelhado, e imprime a
         correlação (NCC) do detalhe: as duas imagens passam por um filtro
         passa-alta (menos o desfoque gaussiano de 6% da largura do trecho),
         para comparar o desenho do reflexo e não a mancha escura que todo sino
         tem. NCC alto = o cromado repete o reflexo da capa: luz de estúdio
         colada na cena (item h2 de guia/criterios.md). saida.png põe os dois
         recortes lado a lado, para conferir.
"""
import sys, os
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
from PIL import Image, ImageChops, ImageDraw, ImageFont


def diff(base_p, nova_p, mascara_p=None, limiar=10):
    a = Image.open(base_p).convert("RGB")
    b = Image.open(nova_p).convert("RGB")
    if a.size != b.size:
        b = b.resize(a.size)
    d = ImageChops.difference(a, b).convert("L")
    if mascara_p:
        m = Image.open(mascara_p).convert("L").resize(a.size).point(lambda p: 255 if p > 127 else 0)
        area = sum(1 for p in m.getdata() if p)
        dd = d.getdata()
        alterados = sum(1 for p, mm in zip(dd, m.getdata()) if mm and p >= limiar)
        pct = 100.0 * alterados / max(area, 1)
        fora = sum(1 for p, mm in zip(dd, m.getdata()) if not mm and p >= limiar)
        print(f"pixels alterados DENTRO da mascara: {pct:.2f}% (area da mascara: {100.0*area/(a.size[0]*a.size[1]):.2f}% do quadro)")
        print(f"pixels alterados FORA da mascara: {100.0*fora/max(a.size[0]*a.size[1]-area,1):.3f}% (deve ser ~0 — vazamento)")
    else:
        h = d.histogram()
        total = a.size[0] * a.size[1]
        alterados = sum(h[limiar:])
        pct = 100.0 * alterados / total
        print(f"pixels alterados: {pct:.2f}%")
    if pct < 2.0:
        print("VEREDITO: edicao NAO alterou a imagem de forma relevante — FALHOU.")
    else:
        print("VEREDITO: houve alteracao real; inspecionar crops.")
    return pct


def crops(img_p, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    im = Image.open(img_p)
    w, h = im.size
    zonas = {
        "q1-topo-esq": (0, 0, w // 2, h // 2),
        "q2-topo-dir": (w // 2, 0, w, h // 2),
        "q3-baixo-esq": (0, h // 2, w // 2, h),
        "q4-baixo-dir": (w // 2, h // 2, w, h),
        "centro": (w // 4, h // 4, 3 * w // 4, 3 * h // 4),
    }
    base = os.path.splitext(os.path.basename(img_p))[0]
    for nome, box in zonas.items():
        c = im.crop(box)
        p = os.path.join(out_dir, f"{base}-{nome}.png")
        c.save(p)
        print(p)


def _fonte(tamanho):
    for n in ("arial.ttf", "DejaVuSans.ttf", "LiberationSans-Regular.ttf"):
        try:
            return ImageFont.truetype(n, tamanho)
        except OSError:
            continue
    try:
        return ImageFont.load_default(size=tamanho)
    except TypeError:
        return ImageFont.load_default()


def grade(img_p, out_p, passo=50, zoom=1.0, recorte=None):
    """Grade rotulada em px da imagem ORIGINAL, para medir proporções contra a referência."""
    im = Image.open(img_p).convert("RGB")
    x0, y0 = 0, 0
    if recorte:
        x0, y0, x1, y1 = recorte
        im = im.crop((x0, y0, x1, y1))
    if zoom != 1:
        im = im.resize((max(1, round(im.size[0] * zoom)), max(1, round(im.size[1] * zoom))), Image.LANCZOS)
    w, h = im.size
    margem = 44
    tela = Image.new("RGB", (w + margem, h + margem), (255, 255, 255))
    tela.paste(im, (margem, margem))
    camada = Image.new("RGBA", tela.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(camada)
    f = _fonte(12)
    primeiro_x = -(-x0 // passo) * passo
    primeiro_y = -(-y0 // passo) * passo
    for k, xv in enumerate(range(primeiro_x, x0 + int(w / zoom) + 1, passo)):
        x = margem + (xv - x0) * zoom
        forte = (xv // passo) % 5 == 0
        d.line([(x, margem), (x, margem + h)], fill=(255, 0, 0, 200 if forte else 110), width=2 if forte else 1)
        d.line([(x, 0), (x, margem)], fill=(0, 0, 0, 255), width=1)
        d.text((x + 2, 2 + (k % 2) * 16), str(xv), fill=(0, 0, 0, 255), font=f)
    for k, yv in enumerate(range(primeiro_y, y0 + int(h / zoom) + 1, passo)):
        y = margem + (yv - y0) * zoom
        forte = (yv // passo) % 5 == 0
        d.line([(margem, y), (margem + w, y)], fill=(0, 160, 255, 200 if forte else 110), width=2 if forte else 1)
        d.line([(0, y), (margem, y)], fill=(0, 0, 0, 255), width=1)
        d.text((2, y + 1), str(yv), fill=(0, 0, 0, 255), font=f)
    tela = Image.alpha_composite(tela.convert("RGBA"), camada).convert("RGB")
    tela.save(out_p)
    print(out_p, "(passo %d px, zoom %.2g)" % (passo, zoom))
    return out_p


# limiar do item h2 de guia/criterios.md (se divergir, vale o guia)
LIMIAR_COLAGEM = 0.32
PASSA_ALTA = 0.06   # sigma do desfoque subtraído, em fração da largura do trecho


def _ncc(I, T):
    """NCC de T em todas as posições válidas de I (FFT + imagens integrais)."""
    import numpy as np
    H, W = I.shape
    h, w = T.shape
    Tz = T - T.mean()
    nT = np.sqrt((Tz ** 2).sum())
    F = np.fft.rfft2(I, s=(H + h, W + w))
    G = np.fft.rfft2(Tz[::-1, ::-1], s=(H + h, W + w))
    c = np.fft.irfft2(F * G, s=(H + h, W + w))[h - 1:H, w - 1:W]
    S = np.pad(I, ((1, 0), (1, 0))).cumsum(0).cumsum(1)
    S2 = np.pad(I * I, ((1, 0), (1, 0))).cumsum(0).cumsum(1)
    soma = lambda A: A[h:, w:] - A[:-h, w:] - A[h:, :-w] + A[:-h, :-w]
    s1, s2 = soma(S), soma(S2)
    var = s2 - s1 * s1 / (h * w)
    r = c / (np.sqrt(np.maximum(var, 1e-6)) * nT + 1e-9)
    r[var < 4 * h * w] = -1    # trecho liso (desvio < 2 níveis no detalhe) não é cromado
    return r


def colagem(capa_p, caixa_capa, cand_p, janela, escala, out_p=None):
    """Quanto o cromado da candidata repete o reflexo da capa (item h2)."""
    import numpy as np
    from PIL import ImageFilter
    def passa_alta(im, s):
        return np.asarray(im).astype(float) - np.asarray(im.filter(ImageFilter.GaussianBlur(s))).astype(float)
    T0 = Image.open(capa_p).convert("L").crop(caixa_capa)
    cand = Image.open(cand_p).convert("RGB")
    Jl = cand.convert("L").crop(janela)
    melhor = None
    for e in np.arange(0.8, 1.2001, 0.01) * escala:
        w, h = int(round(T0.width * e)), int(round(T0.height * e))
        if w < 8 or h < 8 or w >= Jl.width or h >= Jl.height:
            continue
        s = max(1.0, PASSA_ALTA * w)
        I = passa_alta(Jl, s)
        for espelho in (False, True):
            Ti = (T0.transpose(Image.FLIP_LEFT_RIGHT) if espelho else T0).resize((w, h), Image.LANCZOS)
            c = _ncc(I, passa_alta(Ti, s))
            k = np.unravel_index(np.argmax(c), c.shape)
            if melhor is None or c[k] > melhor[0]:
                melhor = (float(c[k]), e / escala, janela[0] + int(k[1]), janela[1] + int(k[0]), w, h, espelho)
    if melhor is None:
        raise SystemExit("janela menor que o trecho da capa nessa escala: aumente a janela ou confira a escala")
    v, e, x, y, w, h, espelho = melhor
    print("NCC %.3f (escala %.2f x a esperada; em x=%d y=%d, %dx%d; espelhado: %s)" % (v, e, x, y, w, h, "sim" if espelho else "não"))
    if v >= LIMIAR_COLAGEM:
        print("VEREDITO: NCC >= %.2f: o cromado repete o reflexo da capa, luz de estúdio colada na cena (h2, VETO)." % LIMIAR_COLAGEM)
    else:
        print("VEREDITO: NCC < %.2f: o cromado reflete outra luz, não a da capa." % LIMIAR_COLAGEM)
    if e < 0.83 or e > 1.17:
        print("aviso: o melhor casamento ficou na borda das escalas; confira a escala e a janela no recorte.")
    if out_p:
        a = Image.open(capa_p).convert("RGB").crop(caixa_capa)
        b = cand.crop((x, y, x + w, y + h)).resize(a.size, Image.LANCZOS)
        if espelho:
            b = b.transpose(Image.FLIP_LEFT_RIGHT)
        tela = Image.new("RGB", (a.width * 2 + 10, a.height), (255, 255, 255))
        tela.paste(a, (0, 0))
        tela.paste(b, (a.width + 10, 0))
        tela.save(out_p)
        print(out_p, "(capa | candidata)")
    return v


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)
    if sys.argv[1] == "diff":
        diff(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else None)
    elif sys.argv[1] == "crops":
        crops(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == "grade":
        extra = sys.argv[4:]
        rec = None
        if extra and "," in extra[-1]:
            rec = [int(v) for v in extra.pop().split(",")]
            if len(rec) != 4:
                print(__doc__)
                sys.exit(1)
        grade(sys.argv[2], sys.argv[3],
              int(extra[0]) if len(extra) > 0 else 50,
              float(extra[1]) if len(extra) > 1 else 1.0, rec)
    elif sys.argv[1] == "colagem" and len(sys.argv) >= 7:
        caixa = lambda s: tuple(int(v) for v in s.split(","))
        colagem(sys.argv[2], caixa(sys.argv[3]), sys.argv[4], caixa(sys.argv[5]), float(sys.argv[6]),
                sys.argv[7] if len(sys.argv) > 7 else None)
    else:
        print(__doc__)
        sys.exit(1)
