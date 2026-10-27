# -*- coding: utf-8 -*-
"""Cromadas LUX no site: baixa as fotos certas e mede o que está no ar.

As cromadas novas (logo a laser, anel no padrão de 22/10) têm o MESMO nome de
arquivo que as cromadas antigas que estão na `main` (PR #2, logo impresso).
Quem pega a foto pelo nome, num clone da `main` ou num link sem commit fixo,
leva a antiga. Este script evita a troca pelos dois lados:

  baixar   baixa as cromadas a publicar pelo link de commit fixo, confere o MD5
           (recusa o MD5 da antiga) e grava o manifesto do upload_shopify.py.
  conferir lê o catálogo público da loja, baixa cada imagem dos produtos LUX e
           diz se ela é a cromada NOVA, a ANTIGA do repositório ou OUTRA foto,
           medindo, não olhando.

Uso:
  python conferir_cromadas_site.py baixar   --csv cromadas-site-2026-10-27.csv --saida cromadas
  python conferir_cromadas_site.py conferir --csv cromadas-site-2026-10-27.csv --saida conferencia
  python conferir_cromadas_site.py conferir --csv ... --json products.json   (catálogo salvo)

Como mede (calibrado em 27/10 com recompressão JPEG/WebP a 1200 px):
  1. família: miniatura de 200 px contra as referências do mesmo modelo; MAD
     < 4 diz que é a mesma foto de base (acesa ou apagada). Proporção
     diferente das referências = OUTRA.
  2. versão: a 1200 px, só nos pixels em que nova e antiga diferem (anel e
     logo), MAD contra cada referência. A certa dá 1,2 a 2,3; a errada, 5,3 ou
     mais. Decide se a melhor é < 4 e a segunda é pelo menos 2x a melhor.
"""
import argparse
import csv
import hashlib
import io
import json
import os
import re
import sys
import urllib.request

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

LARGURA = 1200
MINI = 200
LIMIAR_FAMILIA = 4.0
LIMIAR_VERSAO = 4.0
MARGEM = 2.0
UA = {"User-Agent": "gardie-fotografo/conferir-cromadas"}


def baixar_bytes(url, timeout=90):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def ler_csv(caminho):
    with open(caminho, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def abrir_rgb(dados):
    im = Image.open(io.BytesIO(dados))
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        fundo = Image.new("RGBA", im.size, (255, 255, 255, 255))
        fundo.alpha_composite(im)
        im = fundo
    return im.convert("RGB")


def redim(im, largura):
    return im.resize((largura, round(im.height * largura / im.width)), Image.LANCZOS)


def arr(im):
    return np.asarray(im, dtype=np.float32)


def mascara(a, b, limiar=12, dilata=9):
    d = np.abs(arr(a) - arr(b)).max(axis=2) > limiar
    m = Image.fromarray((d * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(dilata))
    return np.asarray(m) > 0


# ---------------------------------------------------------------- baixar

def cmd_baixar(args):
    linhas = [l for l in ler_csv(args.csv) if l["publicar"] == "sim"]
    lote = []
    for l in linhas:
        destino = os.path.join(args.saida, l["codigo"], l["arquivo"])
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        if os.path.exists(destino) and hashlib.md5(open(destino, "rb").read()).hexdigest() == l["md5_nova"]:
            dados = None
        else:
            dados = baixar_bytes(l["url_nova"])
            md5 = hashlib.md5(dados).hexdigest()
            if l["md5_antiga_mesmo_nome"] and md5 == l["md5_antiga_mesmo_nome"]:
                raise SystemExit("RECUSADA, é a cromada ANTIGA: %s" % l["url_nova"])
            if md5 != l["md5_nova"]:
                raise SystemExit("MD5 não confere em %s: %s (esperado %s)" % (l["arquivo"], md5, l["md5_nova"]))
            with open(destino, "wb") as f:
                f.write(dados)
        print("ok  %s posição %s  %s" % (l["codigo"], l["posicao"], l["arquivo"]))
        lote.append({"local": os.path.abspath(destino), "remoto": l["arquivo"], "alt": l["alt"]})
    manifesto = os.path.join(args.saida, "shopify-lote-cromadas.json")
    with open(manifesto, "w", encoding="utf-8") as f:
        json.dump(lote, f, ensure_ascii=False, indent=1)
    print("%d cromadas conferidas pelo MD5; manifesto: %s" % (len(lote), manifesto))


# ---------------------------------------------------------------- conferir

class Modelo:
    """Referências de um modelo: todas as cromadas novas e as antigas da main."""

    def __init__(self, base, linhas, cache):
        self.base = base
        self.refs = {}  # rótulo -> (família, imagem a LARGURA)
        for l in linhas:
            fam = "apagada" if "apagada" in l["conteudo"] else "acesa"
            self.refs["NOVA pos%s (%s)" % (l["posicao"], l["conteudo"])] = (fam, self._ref(l["url_nova"], cache))
            if l["url_antiga"]:
                self.refs["ANTIGA %s (main)" % l["arquivo"].rsplit("-", 1)[1].split(".")[0]] = (fam, self._ref(l["url_antiga"], cache))
        uma = next(iter(self.refs.values()))[1]
        self.proporcao = uma.height / uma.width
        self.mascaras = {}
        for fam in ("acesa", "apagada"):
            novas = [im for r, (f, im) in self.refs.items() if f == fam and r.startswith("NOVA")]
            antigas = [im for r, (f, im) in self.refs.items() if f == fam and r.startswith("ANTIGA")]
            m = np.zeros((uma.height, uma.width), bool)
            for a in antigas:
                for n in novas:
                    m |= mascara(n, a)
            if not antigas and len(novas) > 1:
                for n in novas[1:]:
                    m |= mascara(novas[0], n)
            self.mascaras[fam] = m

    @staticmethod
    def _ref(url, cache):
        nome = os.path.join(cache, hashlib.md5(url.encode()).hexdigest() + ".png")
        if os.path.exists(nome):
            return Image.open(nome).convert("RGB")
        im = redim(abrir_rgb(baixar_bytes(url)), LARGURA)
        im.save(nome)
        return im

    def medir(self, im):
        if abs(im.height / im.width - self.proporcao) > 0.01 * self.proporcao:
            return {"veredito": "OUTRA", "motivo": "proporção diferente das cromadas do repositório"}
        im = redim(im, LARGURA)
        if im.height != next(iter(self.refs.values()))[1].height:
            im = im.resize(next(iter(self.refs.values()))[1].size, Image.LANCZOS)
        mini = arr(redim(im, MINI))
        fam_dist = {r: float(np.abs(mini - arr(redim(ref, MINI))).mean()) for r, (f, ref) in self.refs.items()}
        melhor = min(fam_dist, key=fam_dist.get)
        if fam_dist[melhor] >= LIMIAR_FAMILIA:
            return {"veredito": "OUTRA", "motivo": "não é a mesma foto (MAD %.1f na miniatura)" % fam_dist[melhor]}
        fam = self.refs[melhor][0]
        m = self.mascaras[fam]
        a = arr(im)
        dist = {r: float(np.abs(a - arr(ref))[m].mean()) for r, (f, ref) in self.refs.items() if f == fam}
        ordem = sorted(dist, key=dist.get)
        r1 = ordem[0]
        r2 = ordem[1] if len(ordem) > 1 else None
        seguro = dist[r1] < LIMIAR_VERSAO and (r2 is None or dist[r2] >= MARGEM * dist[r1])
        return {
            "veredito": r1.split()[0] if seguro else "INCONCLUSIVA",
            "referencia": r1,
            "distancias": {k: round(v, 1) for k, v in sorted(dist.items(), key=lambda x: x[1])},
        }


def cmd_conferir(args):
    linhas = ler_csv(args.csv)
    cache = os.path.join(args.saida, "_referencias")
    os.makedirs(cache, exist_ok=True)
    por_base = {}
    for l in linhas:
        por_base.setdefault(l["codigo"][:5], []).append(l)

    if args.json:
        catalogo = json.load(open(args.json, encoding="utf-8"))
    else:
        catalogo = json.loads(baixar_bytes(args.loja.rstrip("/") + "/products.json?limit=250"))

    modelos = {}
    resultado = []
    for p in catalogo.get("products", []):
        skus = {v["id"]: (v.get("sku") or "", v.get("title") or "") for v in p.get("variants", [])}
        bases = {s[:5] for s, _ in skus.values() if s[:5] in por_base}
        if not bases:
            continue
        base = bases.pop()
        if base not in modelos:
            print("referências do %s..." % base, file=sys.stderr)
            modelos[base] = Modelo(base, por_base[base], cache)
        cr = {vid for vid, (s, _) in skus.items() if s.upper().endswith("CR")}
        img_cr = {}
        for v in p.get("variants", []):
            if v["id"] in cr and v.get("featured_image"):
                img_cr[v["featured_image"]["id"]] = v["sku"]
        for img in p.get("images", []):
            src = img["src"]
            url = src + ("&" if "?" in src else "?") + "width=%d" % LARGURA
            try:
                im = abrir_rgb(baixar_bytes(url))
            except Exception as e:  # noqa: BLE001 - relatório segue com as outras
                resultado.append({"produto": p["title"], "posicao": img["position"], "src": src, "veredito": "ERRO", "motivo": str(e)[:120]})
                continue
            med = modelos[base].medir(im)
            variantes = [skus[v][0] for v in img.get("variant_ids", []) if v in skus]
            linha = {
                "produto": p["title"], "base": base, "posicao": img["position"],
                "arquivo": src.split("/")[-1].split("?")[0], "src": src,
                "variantes": variantes, "imagem_da_variante_cromada": img["id"] in img_cr,
                "atualizada": img.get("updated_at"),
            }
            linha.update(med)
            resultado.append(linha)
            linha["_miniatura"] = redim(im, 240)
            print("%-14s pos %2s %-10s %s" % (p["title"][:14], img["position"], med["veredito"], linha["arquivo"]), file=sys.stderr)

    os.makedirs(args.saida, exist_ok=True)
    salvar_relatorio(resultado, modelos, args.saida)


def salvar_relatorio(resultado, modelos, saida):
    limpo = [{k: v for k, v in r.items() if not k.startswith("_")} for r in resultado]
    with open(os.path.join(saida, "conferencia.json"), "w", encoding="utf-8") as f:
        json.dump(limpo, f, ensure_ascii=False, indent=1)

    md = ["# Cromadas LUX no site: o que está no ar", "",
          "| Produto | Pos. | Variante cromada? | Veredito | Mais perto de | Arquivo |",
          "|---|---|---|---|---|---|"]
    for r in limpo:
        md.append("| %s | %s | %s | **%s** | %s | `%s` |" % (
            r.get("produto"), r.get("posicao"), "sim" if r.get("imagem_da_variante_cromada") else "",
            r.get("veredito"), r.get("referencia", r.get("motivo", "")), r.get("arquivo", r.get("src"))))
    resumo = {}
    for r in limpo:
        resumo[r.get("veredito")] = resumo.get(r.get("veredito"), 0) + 1
    md += ["", "Resumo: " + ", ".join("%s %d" % kv for kv in sorted(resumo.items()))]
    with open(os.path.join(saida, "conferencia.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")

    # prancha: só o que casou com uma cromada (nova, antiga ou inconclusiva)
    casadas = [r for r in resultado if r.get("referencia")]
    if not casadas:
        return
    cores = {"NOVA": (30, 140, 60), "ANTIGA": (200, 40, 40), "INCONCLUSIVA": (200, 140, 0)}
    alt = 240 * 16 // 10 + 40
    prancha = Image.new("RGB", (6 * 250, ((len(casadas) + 5) // 6) * alt), "white")
    d = ImageDraw.Draw(prancha)
    for i, r in enumerate(casadas):
        x, y = (i % 6) * 250, (i // 6) * alt
        mini = r["_miniatura"]
        mini.thumbnail((240, alt - 40))
        prancha.paste(mini, (x + 5, y + 36))
        cor = cores.get(r["veredito"], (90, 90, 90))
        d.rectangle([x, y, x + 245, y + 32], fill=cor)
        d.text((x + 6, y + 3), "%s pos %s" % (r["produto"][:16], r["posicao"]), fill="white")
        d.text((x + 6, y + 17), "%s  %s" % (r["veredito"], re.sub(r" \(.*", "", r["referencia"])), fill="white")
    prancha.save(os.path.join(saida, "prancha-conferencia.jpg"), quality=88)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("baixar")
    b.add_argument("--csv", required=True)
    b.add_argument("--saida", default="cromadas")
    c = sub.add_parser("conferir")
    c.add_argument("--csv", required=True)
    c.add_argument("--saida", default="conferencia")
    c.add_argument("--loja", default="https://gardie.com.br")
    c.add_argument("--json", help="products.json salvo, em vez de ler a loja")
    args = ap.parse_args()
    {"baixar": cmd_baixar, "conferir": cmd_conferir}[args.cmd](args)


if __name__ == "__main__":
    main()
