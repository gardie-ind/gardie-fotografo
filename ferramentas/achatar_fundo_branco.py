"""Achata no branco as fotos de produto com fundo transparente do site (03/11/2026).

Lê pela API Admin da Shopify todas as mídias PNG dos produtos, baixa o
original e grava em PASTA:
  produtos.json      os produtos, com variações e mídias, como estavam
  orig/<id>.png      o original baixado do CDN
  branco/<id>.png    a mesma foto sobre branco 255, sem transparência
  achatadas.json     uma linha por mídia PNG: produto, posição, URL e a fração
                     de pixels com transparência (`transp`; 0 = já era opaca)

Confere cada uma: pixel opaco idêntico ao original e pixel transparente = 255.
A troca no site é o `achatar_fundo_site.py`, com a mesma PASTA.

uso: python3 achatar_fundo_branco.py PASTA"""
import concurrent.futures as cf, json, os, sys, urllib.request
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("SHOPIFY_STORE", os.environ.get("SHOPIFY_FLAG_STORE", ""))
import shopify_auth as auth

Q = ('query($c:String){products(first:50,after:$c){pageInfo{hasNextPage endCursor} nodes{id title handle status '
     'featuredMedia{... on MediaImage{id image{url}}} variants(first:30){nodes{sku title image{url}}} '
     'media(first:100){nodes{... on MediaImage{id image{url width height}}}}}}}')


def produtos(store, token):
    out, cur = [], None
    while True:
        p = auth.gql(store, token, Q, {"c": cur})["products"]
        out += p["nodes"]
        if not p["pageInfo"]["hasNextPage"]:
            return out
        cur = p["pageInfo"]["endCursor"]


def achatar(pasta, it):
    mid = it["mid"].rsplit("/", 1)[1]
    o = os.path.join(pasta, "orig", mid + ".png"); b = os.path.join(pasta, "branco", mid + ".png")
    if not os.path.exists(o):
        urllib.request.urlretrieve(it["url"], o)
    im = Image.open(o); it["modo"] = im.mode; it["tam"] = im.size
    rgba = np.array(im.convert("RGBA")).astype(np.float32)
    a = rgba[..., 3:4] / 255.0
    it["transp"] = float((a < 0.996).mean())
    out = np.clip(np.rint(rgba[..., :3] * a + 255.0 * (1 - a)), 0, 255).astype(np.uint8)
    Image.fromarray(out, "RGB").save(b, compress_level=6)
    cheio = a[..., 0] >= 0.999; zero = a[..., 0] <= 0.001
    it["ok_opaco"] = bool((out[cheio] == rgba[..., :3][cheio].astype(np.uint8)).all())
    it["ok_fundo"] = bool((out[zero] == 255).all()) if zero.any() else True
    return it


def main():
    pasta = sys.argv[1]
    for sub in ("orig", "branco"):
        os.makedirs(os.path.join(pasta, sub), exist_ok=True)
    store, token = auth.get_token()
    ps = produtos(store, token)
    json.dump(ps, open(os.path.join(pasta, "produtos.json"), "w"), ensure_ascii=False, indent=1)
    itens = [{"produto": p["title"], "handle": p["handle"], "pid": p["id"], "mid": m["id"], "pos": pos, "url": m["image"]["url"]}
             for p in ps for pos, m in enumerate(p["media"]["nodes"], 1)
             if m.get("image") and ".png" in m["image"]["url"].lower()]
    with cf.ThreadPoolExecutor(6) as ex:
        res = list(ex.map(lambda it: achatar(pasta, it), itens))
    json.dump(res, open(os.path.join(pasta, "achatadas.json"), "w"), ensure_ascii=False, indent=1)
    t = [r for r in res if r["transp"] > 0]
    ruins = [r["url"] for r in res if not (r["ok_opaco"] and r["ok_fundo"])]
    print("%d PNG, %d com transparência, %d com erro na conferência" % (len(res), len(t), len(ruins)))
    for u in ruins:
        print("  ERRO:", u)


if __name__ == "__main__":
    main()
