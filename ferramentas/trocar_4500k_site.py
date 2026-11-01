"""Troca no site a foto 4500K dos LUX e da Lumière pelo render 4500K (01/11/2026).

Pedido do Thiago (01/11/2026): "Aqui no site, na prática, o 4500K e o 6000K
parecem a mesma coisa". No cartão, ele escolheu "4500K fiel ao real". A lista
é `fotos-lux-centradas-2026-11-01.csv`, posição 1, com a coluna
`substitui_no_site`. Para a Lumière, a nova é a antiga 3000K com nome -5, na
pasta do projeto `2026-11-01-tons-anel/lumiere-4500k/`.

Para cada foto: sobe a nova com o mesmo alt da antiga, põe na mesma posição
da galeria, liga às variações que mostravam a antiga e tira a antiga do
produto. A antiga fica no Shopify Files (só perde a referência ao produto),
para dar para desfazer. O registro vai para `trocar_4500k_site.log.json`.

uso: python3 trocar_4500k_site.py            # só confere (não muda nada)
     python3 trocar_4500k_site.py --trocar   # troca"""
import csv, hashlib, json, os, sys, time, uuid, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("SHOPIFY_STORE", os.environ.get("SHOPIFY_FLAG_STORE", ""))
import shopify_auth as auth

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CSV = os.path.join(RAIZ, "ferramentas", "fotos-lux-centradas-2026-11-01.csv")
LUMIERE = "/mnt/project-files/fotografo/2026-11-01-tons-anel/lumiere-4500k/"
LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "trocar_4500k_site.log.json")
PRODUTOS = {"10202": "CLASSIQUE LUX", "10288": "ROYALE LUX", "10455": "MOBILE LUX", "10509": "VISAGE LUX",
            "10554": "FLEX LUX", "22005": "LUMIÈRE"}

Q_FIND = 'query($q:String!){products(first:5,query:$q){nodes{id title handle}}}'
Q_PROD = ('query($id:ID!){product(id:$id){id title status variants(first:30){nodes{id sku media(first:1){nodes{id}}}} '
          'media(first:80){nodes{id alt status ... on MediaImage{image{url width}}}}}}')
Q_STAGED = ('mutation($input:[StagedUploadInput!]!){stagedUploadsCreate(input:$input){'
            'stagedTargets{url resourceUrl parameters{name value}} userErrors{field message}}}')
Q_ADD = ('mutation($p:ProductUpdateInput!,$m:[CreateMediaInput!]){productUpdate(product:$p,media:$m){'
         'product{id} userErrors{field message}}}')
Q_REORDER = ('mutation($id:ID!,$moves:[MoveInput!]!){productReorderMedia(id:$id,moves:$moves){'
             'job{id} mediaUserErrors{field message}}}')
Q_VAR = ('mutation($p:ID!,$v:[ProductVariantsBulkInput!]!){productVariantsBulkUpdate(productId:$p,variants:$v){'
         'productVariants{id} userErrors{field message}}}')
Q_SOLTA = ('mutation($f:[FileUpdateInput!]!){fileUpdate(files:$f){files{id} userErrors{field message}}}')


def nome_cdn(m):
    return m["image"]["url"].split("/files/")[-1].split("?")[0] if m.get("image") else ""


def bate(m, antigo):
    """A mídia é a still recortada de nome `antigo` (a Shopify acrescenta _<uuid>; o site
    chama o black matte de matte-black). As ambientadas antigas de 800 px com o mesmo
    nome (Mobile Lux) não entram: as stills recortadas têm mais de 2000 px."""
    n = nome_cdn(m)
    if not n or (m["image"].get("width") or 0) < 2000:
        return False
    for a in (antigo, antigo.replace("black-matte", "matte-black")):
        stem = a[:-4]
        if n == a or (n.startswith(stem + "_") and n.endswith(".png")):
            return True
    return False


def trocas():
    out = []
    for r in csv.DictReader(open(CSV, encoding="utf-8")):
        if r["posicao"] == "1" and r["substitui_no_site"]:
            out.append({"codigo": r["codigo"], "novo": os.path.join(RAIZ, "aprovadas", r["codigo"], r["arquivo"]),
                        "nome": r["arquivo"], "antigo": r["substitui_no_site"], "md5": r["md5"]})
    for a in ("cromado", "brushed-nickel", "dourado", "red-gold", "black-matte"):
        cod = "22005" + {"cromado": "CR", "brushed-nickel": "NK.BU", "dourado": "GL", "red-gold": "GL.RD", "black-matte": "BL.MT"}[a]
        nome = "espelho-de-aumento-parede-led-lumiere-%s-gardie-5.png" % a
        out.append({"codigo": cod, "novo": LUMIERE + nome, "nome": nome,
                    "antigo": "espelho-de-aumento-parede-led-lumiere-%s-gardie-1.png" % a, "md5": ""})
    return out


def staged_upload(store, token, path, nome):
    v = {"input": [{"resource": "IMAGE", "filename": nome, "mimeType": "image/png", "httpMethod": "POST",
                    "fileSize": str(os.path.getsize(path))}]}
    d = auth.gql(store, token, Q_STAGED, v)["stagedUploadsCreate"]
    if d["userErrors"]:
        raise SystemExit("stagedUploads %s: %s" % (nome, d["userErrors"]))
    t = d["stagedTargets"][0]; b = uuid.uuid4().hex; body = b""
    for p in t["parameters"]:
        body += ("--%s\r\nContent-Disposition: form-data; name=\"%s\"\r\n\r\n%s\r\n" % (b, p["name"], p["value"])).encode()
    body += ("--%s\r\nContent-Disposition: form-data; name=\"file\"; filename=\"%s\"\r\n"
             "Content-Type: image/png\r\n\r\n" % (b, nome)).encode()
    body += open(path, "rb").read() + ("\r\n--%s--\r\n" % b).encode()
    req = urllib.request.Request(t["url"], data=body, method="POST")
    req.add_header("Content-Type", "multipart/form-data; boundary=%s" % b)
    urllib.request.urlopen(req, timeout=300)
    return t["resourceUrl"]


def main(trocar):
    store, token = auth.get_token()
    log = json.load(open(LOG)) if os.path.exists(LOG) else {}
    plano = {}
    for t in trocas():
        if t["md5"] and hashlib.md5(open(t["novo"], "rb").read()).hexdigest() != t["md5"]:
            raise SystemExit("MD5 diverge do CSV: " + t["nome"])
        plano.setdefault(t["codigo"][:5], []).append(t)
    for base, ts in plano.items():
        achados = auth.gql(store, token, Q_FIND, {"q": 'title:"%s"' % PRODUTOS[base]})["products"]["nodes"]
        achados = [p for p in achados if p["title"] == PRODUTOS[base]]
        if len(achados) != 1:
            raise SystemExit("produto %s: %d achados" % (PRODUTOS[base], len(achados)))
        pid = achados[0]["id"]
        p = auth.gql(store, token, Q_PROD, {"id": pid})["product"]
        midias = p["media"]["nodes"]
        for t in ts:
            idx = [i for i, m in enumerate(midias) if bate(m, t["antigo"])]
            ja = [m for m in midias if bate(m, t["nome"])]
            if ja:
                print("%-11s já trocada: %s" % (t["codigo"], t["nome"])); continue
            if len(idx) != 1:
                raise SystemExit("%s: %d mídias com %s" % (t["codigo"], len(idx), t["antigo"]))
            i = idx[0]; velha = midias[i]
            vars_ = [v["id"] for v in p["variants"]["nodes"] if v["media"]["nodes"] and v["media"]["nodes"][0]["id"] == velha["id"]]
            print("%-11s pos %2d  %s -> %s  variações ligadas: %d" % (t["codigo"], i + 1, nome_cdn(velha)[:60], t["nome"], len(vars_)))
            if not trocar:
                continue
            envio = t["nome"].replace("black-matte", "matte-black") if "matte-black" in nome_cdn(velha) else t["nome"]
            src = staged_upload(store, token, t["novo"], envio)
            d = auth.gql(store, token, Q_ADD, {"p": {"id": pid}, "m": [{"originalSource": src, "alt": velha["alt"],
                                                                         "mediaContentType": "IMAGE"}]})["productUpdate"]
            if d["userErrors"]:
                raise SystemExit("productUpdate %s: %s" % (t["nome"], d["userErrors"]))
            nova = None
            for _ in range(100):
                ms = auth.gql(store, token, Q_PROD, {"id": pid})["product"]["media"]["nodes"]
                cand = [m for m in ms if bate(m, envio)]
                if cand and cand[0]["status"] in ("READY", "FAILED"):
                    nova = cand[0]; break
                time.sleep(3)
            if not nova or nova["status"] != "READY":
                raise SystemExit("processamento falhou: " + t["nome"])
            d = auth.gql(store, token, Q_REORDER, {"id": pid, "moves": [{"id": nova["id"], "newPosition": str(i)}]})["productReorderMedia"]
            if d["mediaUserErrors"]:
                raise SystemExit("reorder %s: %s" % (t["nome"], d["mediaUserErrors"]))
            if vars_:
                d = auth.gql(store, token, Q_VAR, {"p": pid, "v": [{"id": v, "mediaId": nova["id"]} for v in vars_]})["productVariantsBulkUpdate"]
                if d["userErrors"]:
                    raise SystemExit("variações %s: %s" % (t["nome"], d["userErrors"]))
            d = auth.gql(store, token, Q_SOLTA, {"f": [{"id": velha["id"], "referencesToRemove": [pid]}]})["fileUpdate"]
            if d["userErrors"]:
                raise SystemExit("tirar a antiga %s: %s" % (t["antigo"], d["userErrors"]))
            log[t["nome"]] = {"codigo": t["codigo"], "produto": pid, "posicao_galeria": i + 1, "midia_nova": nova["id"],
                              "url_nova": nova["image"]["url"], "midia_antiga": velha["id"], "url_antiga": velha["image"]["url"],
                              "alt": velha["alt"], "variacoes": vars_, "quando": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
            json.dump(log, open(LOG, "w"), ensure_ascii=False, indent=1)
            midias = auth.gql(store, token, Q_PROD, {"id": pid})["product"]["media"]["nodes"]
            print("   trocada")
    print("ok" if trocar else "conferência ok (nada mudou)")


if __name__ == "__main__":
    main("--trocar" in sys.argv)
