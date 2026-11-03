"""Troca no site as fotos de fundo transparente pela mesma foto achatada no branco (03/11/2026).

Pedido do Thiago (03/11/2026): no Merchant Center, as fotos recortadas dos
produtos claros aparecem com fundo preto, e a galeria pisca preto ao carregar.
O Google escolhe sozinho o fundo de uma foto transparente: preto para
produto claro. No cartão, ele escolheu "Todas as 145 transparentes".

Entrada: `achatadas.json` (feito por `achatar_fundo_branco.py`), com uma linha por mídia
PNG dos produtos, e a pasta `branco/<id da mídia>.png`. Cada foto foi
achatada sobre branco 255: pixel opaco idêntico, pixel transparente = 255.

Para cada mídia com transparência:
1. sobe a versão branca com nome novo (`<nome antigo>-fundo-branco.png`) e o
   mesmo alt, que leva a hashtag da variante;
2. põe a nova na mesma posição da galeria;
3. liga a nova às variações que mostravam a antiga;
4. troca o campo "Foto da amostra" (`gardie.foto_amostra`) que apontava
   para a antiga;
5. tira a antiga do produto. A antiga continua no Shopify Files (dá para
   desfazer); apagar é outro passo (`--apagar`), depois de conferir no CDN.

O registro vai para `achatar_fundo_site.log.json`, ao lado da entrada (cópia
da troca de 03/11/2026 nesta pasta).

`--apagar` lê `refs-depois.json` na PASTA: id da mídia antiga → lugares fora
da galeria que ainda a citam (tema, páginas, metafields). Só apaga a antiga
conferida no CDN e sem nenhuma citação. Em 03/11/2026 ficaram 20: a página
"Sobre nós" usa uma, e o Judge.me guarda a foto antiga no widget das
avaliações até sincronizar de novo. O `craftshift.variantImages` não conta:
é do app Rubik, que o `gardie.foto_amostra` substituiu em 16/10/2026.

uso: python3 achatar_fundo_site.py PASTA             # só confere
     python3 achatar_fundo_site.py PASTA --trocar    # troca
     python3 achatar_fundo_site.py PASTA --conferir  # compara pixels do CDN com o arquivo branco
     python3 achatar_fundo_site.py PASTA --apagar    # apaga as antigas sem nenhuma outra referência"""
import io, json, os, re, sys, time, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("SHOPIFY_STORE", os.environ.get("SHOPIFY_FLAG_STORE", ""))
import shopify_auth as auth
from trocar_4500k_site import staged_upload, Q_ADD, Q_REORDER, Q_VAR, Q_SOLTA

Q_PROD = ('query($id:ID!){product(id:$id){id title status '
          'variants(first:40){nodes{id sku media(first:1){nodes{id}} amostra:metafield(namespace:"gardie",key:"foto_amostra"){value}}} '
          'media(first:100){nodes{id alt status ... on MediaImage{image{url width height}}}}}}')
Q_MF = ('mutation($m:[MetafieldsSetInput!]!){metafieldsSet(metafields:$m){metafields{id} userErrors{field message}}}')
Q_DEL = 'mutation($ids:[ID!]!){fileDelete(fileIds:$ids){deletedFileIds userErrors{field message}}}'
Q_FILE = 'query($id:ID!){node(id:$id){... on MediaImage{id fileStatus image{url}}}}'


def nome_cdn(url):
    return url.rsplit("/files/", 1)[-1].split("?")[0]


def nome_novo(url):
    stem = nome_cdn(url).rsplit(".", 1)[0]
    stem = re.sub(r"_[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", "", stem)
    return stem + "-fundo-branco.png"


def produto(store, token, pid):
    return auth.gql(store, token, Q_PROD, {"id": pid})["product"]


def trocar_uma(store, token, it, arquivo, log, logpath):
    pid, mid = it["pid"], it["mid"]
    p = produto(store, token, pid)
    midias = p["media"]["nodes"]
    idx = [i for i, m in enumerate(midias) if m["id"] == mid]
    if len(idx) != 1:
        raise SystemExit("%s pos %d: mídia %s não está mais no produto" % (p["title"], it["pos"], mid))
    i = idx[0]; velha = midias[i]
    if nome_cdn(velha["image"]["url"]) != nome_cdn(it["url"]):
        raise SystemExit("%s: mídia %s mudou de arquivo" % (p["title"], mid))
    novo = nome_novo(it["url"])
    stem = novo[:-4]
    vars_ = [v["id"] for v in p["variants"]["nodes"] if v["media"]["nodes"] and v["media"]["nodes"][0]["id"] == mid]
    amostras = [v["id"] for v in p["variants"]["nodes"] if v["amostra"] and v["amostra"]["value"] == mid]
    src = staged_upload(store, token, arquivo, novo)
    d = auth.gql(store, token, Q_ADD, {"p": {"id": pid}, "m": [{"originalSource": src, "alt": velha["alt"],
                                                                 "mediaContentType": "IMAGE"}]})["productUpdate"]
    if d["userErrors"]:
        raise SystemExit("productUpdate %s: %s" % (novo, d["userErrors"]))
    nova = None
    for _ in range(120):
        ms = produto(store, token, pid)["media"]["nodes"]
        cand = [m for m in ms if m.get("image") and nome_cdn(m["image"]["url"]).startswith(stem)
                and m["id"] != mid and m["id"] not in [x["midia_nova"] for x in log.values()]]
        if cand and cand[-1]["status"] in ("READY", "FAILED"):
            nova = cand[-1]; break
        time.sleep(3)
    if not nova or nova["status"] != "READY":
        raise SystemExit("processamento falhou: " + novo)
    d = auth.gql(store, token, Q_REORDER, {"id": pid, "moves": [{"id": nova["id"], "newPosition": str(i)}]})["productReorderMedia"]
    if d["mediaUserErrors"]:
        raise SystemExit("reorder %s: %s" % (novo, d["mediaUserErrors"]))
    for _ in range(60):
        ms = produto(store, token, pid)["media"]["nodes"]
        if ms[i]["id"] == nova["id"]:
            break
        time.sleep(2)
    else:
        raise SystemExit("reorder não aplicou: " + novo)
    if vars_:
        d = auth.gql(store, token, Q_VAR, {"p": pid, "v": [{"id": v, "mediaId": nova["id"]} for v in vars_]})["productVariantsBulkUpdate"]
        if d["userErrors"]:
            raise SystemExit("variações %s: %s" % (novo, d["userErrors"]))
    if amostras:
        d = auth.gql(store, token, Q_MF, {"m": [{"ownerId": v, "namespace": "gardie", "key": "foto_amostra",
                                                  "type": "file_reference", "value": nova["id"]} for v in amostras]})["metafieldsSet"]
        if d["userErrors"]:
            raise SystemExit("amostra %s: %s" % (novo, d["userErrors"]))
    d = auth.gql(store, token, Q_SOLTA, {"f": [{"id": mid, "referencesToRemove": [pid]}]})["fileUpdate"]
    if d["userErrors"]:
        raise SystemExit("tirar a antiga %s: %s" % (nome_cdn(it["url"]), d["userErrors"]))
    log[mid] = {"produto": p["title"], "pid": pid, "posicao_galeria": i + 1, "nome_novo": novo,
                "midia_nova": nova["id"], "url_nova": nova["image"]["url"], "midia_antiga": mid,
                "url_antiga": it["url"], "alt": velha["alt"], "variacoes": vars_, "amostras": amostras,
                "quando": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
    json.dump(log, open(logpath, "w"), ensure_ascii=False, indent=1)
    print("  %-14s pos %2d  %s  variações %d  amostras %d" % (p["title"][:14], i + 1, novo[:70], len(vars_), len(amostras)), flush=True)


def conferir(log, pasta):
    import numpy as np
    from PIL import Image
    ruins = 0
    for mid, r in log.items():
        url = r["url_nova"]
        dados = urllib.request.urlopen(urllib.request.Request(url, headers={"Accept": "image/png"}), timeout=120).read()
        cdn = np.array(Image.open(io.BytesIO(dados)).convert("RGBA"))
        loc = np.array(Image.open(os.path.join(pasta, "branco", mid.rsplit("/", 1)[1] + ".png")).convert("RGBA"))
        ok = cdn.shape == loc.shape and (cdn == loc).all()
        r["cdn_identico"] = bool(ok)
        if not ok:
            ruins += 1
            print("DIFERE:", r["nome_novo"], cdn.shape, loc.shape)
    print("conferidas %d, diferentes %d" % (len(log), ruins))
    return ruins


def main():
    pasta = sys.argv[1]
    modo = sys.argv[2] if len(sys.argv) > 2 else ""
    itens = [x for x in json.load(open(os.path.join(pasta, "achatadas.json"))) if x["transp"] > 0]
    logpath = os.path.join(pasta, "achatar_fundo_site.log.json")
    log = json.load(open(logpath)) if os.path.exists(logpath) else {}
    store, token = auth.get_token()
    if modo == "--conferir":
        conferir(log, pasta)
        json.dump(log, open(logpath, "w"), ensure_ascii=False, indent=1)
        return
    if modo == "--apagar":
        refs = json.load(open(os.path.join(pasta, "refs-depois.json")))
        apagar = [m for m, r in log.items() if r.get("cdn_identico") and not refs.get(m)]
        print("apagar %d de %d (as outras têm referência fora da galeria)" % (len(apagar), len(log)))
        for k in range(0, len(apagar), 25):
            d = auth.gql(store, token, Q_DEL, {"ids": apagar[k:k + 25]})["fileDelete"]
            if d["userErrors"]:
                raise SystemExit("fileDelete: %s" % d["userErrors"])
            for m in d["deletedFileIds"]:
                log[m]["antiga_apagada"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
            json.dump(log, open(logpath, "w"), ensure_ascii=False, indent=1)
        return
    limite = int(os.environ.get("LIMITE", "0")) or None
    feitas = 0
    por_produto = {}
    for it in itens:
        por_produto.setdefault(it["pid"], []).append(it)
    for pid, its in por_produto.items():
        print(its[0]["produto"], len(its), flush=True)
        for it in sorted(its, key=lambda x: x["pos"]):
            if it["mid"] in log:
                continue
            arquivo = os.path.join(pasta, "branco", it["mid"].rsplit("/", 1)[1] + ".png")
            if not os.path.exists(arquivo):
                raise SystemExit("falta o arquivo branco: " + arquivo)
            if modo != "--trocar":
                print("  pos %2d  %s -> %s" % (it["pos"], nome_cdn(it["url"])[:60], nome_novo(it["url"])[:70]))
                continue
            trocar_uma(store, token, it, arquivo, log, logpath)
            feitas += 1
            if limite and feitas >= limite:
                print("parei no limite de %d" % limite); return
    print("ok" if modo == "--trocar" else "conferência ok (nada mudou)")


if __name__ == "__main__":
    main()
