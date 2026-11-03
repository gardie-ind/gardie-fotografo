"""Troca no site a still da posição 1 (acesa 4500K) do Royale Lux 10288 nos 5 acabamentos (03/11/2026).

A nova (-7) tem o pescoço foguetinho, a alça de barra chata com o degrau e o assento, o niple aberto do
Classique Lux e o cabo saindo dele, sem IA. Thiago, 03/11/2026 01:07: "Royale Lux aprovado, pode subir para
o site". A lista é `fotos-lux-centradas-2026-11-01.csv` (posição 1 do 10288, coluna `substitui_no_site`).

Para cada acabamento: sobe a nova com o mesmo alt da antiga (com o #hashtag da variação), põe na mesma
posição da galeria, liga às variações que mostravam a antiga e tira a antiga do produto. A antiga fica no
Shopify Files, para dar para desfazer. O registro vai para `trocar_royale_site.log.json`.

Depois (Thiago, 03/11/2026 01:11: "Precisam das outras cores de temperatura de luz do Royale Lux"): as
mesmas peças na apagada (-8 no lugar da -2) e na 6000K (-10 no lugar da -4). A 3000K (-9) não vai ao site
(publicar = nao até a versão de 3 cores estar à venda).

uso: python3 trocar_royale_site.py [--posicoes 2,4]            # só confere (não muda nada)
     python3 trocar_royale_site.py [--posicoes 2,4] --trocar   # troca (padrão: posição 1)"""
import csv, hashlib, json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("SHOPIFY_STORE", os.environ.get("SHOPIFY_FLAG_STORE", ""))
import shopify_auth as auth
from trocar_4500k_site import Q_FIND, Q_PROD, Q_ADD, Q_REORDER, Q_VAR, Q_SOLTA, staged_upload, nome_cdn, bate

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CSV = os.path.join(RAIZ, "ferramentas", "fotos-lux-centradas-2026-11-01.csv")
LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "trocar_royale_site.log.json")
Q_FILES = 'query($q:String!){files(first:20,query:$q){nodes{id ... on MediaImage{image{url}}}}}'


def trocas(posicoes=("1",)):
    out = []
    for r in csv.DictReader(open(CSV, encoding="utf-8")):
        if r["codigo"].startswith("10288") and r["posicao"] in posicoes and r["substitui_no_site"] \
                and r["publicar"] == "sim":
            out.append({"codigo": r["codigo"], "novo": os.path.join(RAIZ, "aprovadas", r["codigo"], r["arquivo"]),
                        "nome": r["arquivo"], "antigo": r["substitui_no_site"], "md5": r["md5"]})
    return out


def main(trocar, posicoes=("1",)):
    store, token = auth.get_token()
    log = json.load(open(LOG)) if os.path.exists(LOG) else {}
    ach = [p for p in auth.gql(store, token, Q_FIND, {"q": 'title:"ROYALE LUX"'})["products"]["nodes"]
           if p["title"] == "ROYALE LUX"]
    if len(ach) != 1:
        raise SystemExit("ROYALE LUX: %d produtos" % len(ach))
    pid = ach[0]["id"]
    p = auth.gql(store, token, Q_PROD, {"id": pid})["product"]
    midias = p["media"]["nodes"]
    for t in trocas(posicoes):
        if hashlib.md5(open(t["novo"], "rb").read()).hexdigest() != t["md5"]:
            raise SystemExit("MD5 diverge do CSV: " + t["nome"])
        envio = t["nome"]
        idx = [i for i, m in enumerate(midias) if bate(m, t["antigo"])]
        if idx and "matte-black" in nome_cdn(midias[idx[0]]):
            envio = t["nome"].replace("black-matte", "matte-black")
        if [m for m in midias if bate(m, envio)]:
            print("%-11s já trocada: %s" % (t["codigo"], envio)); continue
        if len(idx) != 1:
            raise SystemExit("%s: %d mídias com %s" % (t["codigo"], len(idx), t["antigo"]))
        i = idx[0]; velha = midias[i]
        vars_ = [v["id"] for v in p["variants"]["nodes"] if v["media"]["nodes"] and v["media"]["nodes"][0]["id"] == velha["id"]]
        stem = envio[:-4]
        homonimos = [f for f in auth.gql(store, token, Q_FILES, {"q": "filename:%s" % stem})["files"]["nodes"]
                     if f.get("image") and f["image"]["url"].split("/files/")[-1].split("?")[0].split(".")[0].split("_")[0] == stem]
        print("%-11s pos %2d  %s -> %s  variações: %d  homônimos no Files: %d" % (
            t["codigo"], i + 1, nome_cdn(velha)[:60], envio, len(vars_), len(homonimos)))
        if homonimos:
            raise SystemExit("já existe arquivo com o nome %s no Shopify Files" % envio)
        if not trocar:
            continue
        src = staged_upload(store, token, t["novo"], envio)
        d = auth.gql(store, token, Q_ADD, {"p": {"id": pid}, "m": [{"originalSource": src, "alt": velha["alt"],
                                                                     "mediaContentType": "IMAGE"}]})["productUpdate"]
        if d["userErrors"]:
            raise SystemExit("productUpdate %s: %s" % (envio, d["userErrors"]))
        nova = None
        for _ in range(100):
            ms = auth.gql(store, token, Q_PROD, {"id": pid})["product"]["media"]["nodes"]
            cand = [m for m in ms if bate(m, envio)]
            if cand and cand[0]["status"] in ("READY", "FAILED"):
                nova = cand[0]; break
            time.sleep(3)
        if not nova or nova["status"] != "READY":
            raise SystemExit("processamento falhou: " + envio)
        d = auth.gql(store, token, Q_REORDER, {"id": pid, "moves": [{"id": nova["id"], "newPosition": str(i)}]})["productReorderMedia"]
        if d["mediaUserErrors"]:
            raise SystemExit("reorder %s: %s" % (envio, d["mediaUserErrors"]))
        if vars_:
            d = auth.gql(store, token, Q_VAR, {"p": pid, "v": [{"id": v, "mediaId": nova["id"]} for v in vars_]})["productVariantsBulkUpdate"]
            if d["userErrors"]:
                raise SystemExit("variações %s: %s" % (envio, d["userErrors"]))
        d = auth.gql(store, token, Q_SOLTA, {"f": [{"id": velha["id"], "referencesToRemove": [pid]}]})["fileUpdate"]
        if d["userErrors"]:
            raise SystemExit("tirar a antiga %s: %s" % (t["antigo"], d["userErrors"]))
        log[envio] = {"codigo": t["codigo"], "produto": pid, "posicao_galeria": i + 1, "midia_nova": nova["id"],
                      "url_nova": nova["image"]["url"], "midia_antiga": velha["id"], "url_antiga": velha["image"]["url"],
                      "alt": velha["alt"], "variacoes": vars_, "quando": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
        json.dump(log, open(LOG, "w"), ensure_ascii=False, indent=1)
        p = auth.gql(store, token, Q_PROD, {"id": pid})["product"]
        midias = p["media"]["nodes"]
        print("   trocada")
    print("ok" if trocar else "conferência ok (nada mudou)")


if __name__ == "__main__":
    pos = ("1",)
    if "--posicoes" in sys.argv:
        pos = tuple(sys.argv[sys.argv.index("--posicoes") + 1].split(","))
    main("--trocar" in sys.argv, pos)
