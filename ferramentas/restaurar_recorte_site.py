"""Desfaz o `achatar_fundo_site.py`: volta para o site os recortes transparentes (03/11/2026).

Pedido do Thiago (03/11/2026, 14h47 UTC): "Precisamos das fotos recortadas de
volta". A foto achatada no branco virou um quadrado branco no painel cinza do
bloco de luz (TRI-LED / DUAL-LED, `snippets/gardie-luz-fotos.liquid`), que
precisa da transparência.

Entrada: a mesma PASTA da troca, com `achatar_fundo_site.log.json` (antes →
depois, por foto) e `orig/<id da mídia>.png` (o original baixado do CDN, byte a
byte).

Para cada foto do registro:
1. se a antiga ainda está no Shopify Files (não foi apagada), liga a mesma de
   volta ao produto (`fileUpdate referencesToAdd`): mesmo arquivo, mesmo nome;
   se foi apagada, sobe o original com nome novo (`<nome antigo>-recorte.png`),
   porque nome de arquivo não se reaproveita;
2. põe a transparente na posição da branca, com o mesmo alt;
3. liga a transparente às variações e às amostras de cor (`gardie.foto_amostra`)
   que estavam na branca;
4. tira a branca do produto. A branca fica no Shopify Files, para uma eventual
   versão só do Google (feed suplementar do Merchant).

O registro vai para `restaurar_recorte_site.log.json`, na PASTA.

uso: python3 restaurar_recorte_site.py PASTA              # só confere
     python3 restaurar_recorte_site.py PASTA --restaurar  # restaura
     python3 restaurar_recorte_site.py PASTA --conferir   # compara pixels do CDN com o original
     LIMITE=N e SO=<id da mídia antiga>[,...] limitam a rodada"""
import io, json, os, re, sys, time, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("SHOPIFY_STORE", os.environ.get("SHOPIFY_FLAG_STORE", ""))
import shopify_auth as auth
from trocar_4500k_site import staged_upload, Q_ADD, Q_REORDER, Q_VAR, Q_SOLTA
from achatar_fundo_site import Q_PROD, Q_MF, nome_cdn, produto

Q_NO = 'query($id:ID!){node(id:$id){id ... on MediaImage{fileStatus image{url}}}}'
UUID = r"_[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"


def nome_recorte(url):
    stem = re.sub(UUID, "", nome_cdn(url).rsplit(".", 1)[0])
    return stem + "-recorte.png"


def esperar(store, token, pid, achar, rotulo):
    for _ in range(120):
        ms = produto(store, token, pid)["media"]["nodes"]
        m = achar(ms)
        if m and m["status"] in ("READY", "FAILED"):
            if m["status"] != "READY":
                raise SystemExit("processamento falhou: " + rotulo)
            return m
        time.sleep(3)
    raise SystemExit("não apareceu no produto: " + rotulo)


def restaurar_uma(store, token, mid, r, pasta, log, logpath):
    pid, branca = r["pid"], r["midia_nova"]
    p = produto(store, token, pid)
    midias = p["media"]["nodes"]
    idx = [i for i, m in enumerate(midias) if m["id"] == branca]
    if len(idx) != 1:
        raise SystemExit("%s: a branca %s não está no produto" % (r["produto"], r["nome_novo"]))
    i = idx[0]
    ja = [m["id"] for m in midias]
    if r.get("antiga_apagada"):
        arquivo = os.path.join(pasta, "orig", mid.rsplit("/", 1)[1] + ".png")
        nome = nome_recorte(r["url_antiga"])
        src = staged_upload(store, token, arquivo, nome)
        d = auth.gql(store, token, Q_ADD, {"p": {"id": pid}, "m": [{"originalSource": src, "alt": r["alt"],
                                                                     "mediaContentType": "IMAGE"}]})["productUpdate"]
        if d["userErrors"]:
            raise SystemExit("productUpdate %s: %s" % (nome, d["userErrors"]))
        stem = nome[:-4]
        volta = esperar(store, token, pid, lambda ms: next((m for m in reversed(ms) if m["id"] not in ja and m.get("image")
                                                            and nome_cdn(m["image"]["url"]).startswith(stem)), None), nome)
        modo = "subida de novo"
    else:
        d = auth.gql(store, token, Q_SOLTA, {"f": [{"id": mid, "referencesToAdd": [pid]}]})["fileUpdate"]
        if d["userErrors"]:
            raise SystemExit("religar %s: %s" % (nome_cdn(r["url_antiga"]), d["userErrors"]))
        volta = esperar(store, token, pid, lambda ms: next((m for m in ms if m["id"] == mid), None), mid)
        nome = nome_cdn(volta["image"]["url"])
        modo = "religada"
        if (volta.get("alt") or "") != r["alt"]:
            raise SystemExit("alt mudou ao religar %s" % nome)
    d = auth.gql(store, token, Q_REORDER, {"id": pid, "moves": [{"id": volta["id"], "newPosition": str(i)}]})["productReorderMedia"]
    if d["mediaUserErrors"]:
        raise SystemExit("reorder %s: %s" % (nome, d["mediaUserErrors"]))
    for _ in range(60):
        ms = produto(store, token, pid)["media"]["nodes"]
        if ms[i]["id"] == volta["id"]:
            break
        time.sleep(2)
    else:
        raise SystemExit("reorder não aplicou: " + nome)
    if r["variacoes"]:
        d = auth.gql(store, token, Q_VAR, {"p": pid, "v": [{"id": v, "mediaId": volta["id"]} for v in r["variacoes"]]})["productVariantsBulkUpdate"]
        if d["userErrors"]:
            raise SystemExit("variações %s: %s" % (nome, d["userErrors"]))
    if r["amostras"]:
        d = auth.gql(store, token, Q_MF, {"m": [{"ownerId": v, "namespace": "gardie", "key": "foto_amostra",
                                                  "type": "file_reference", "value": volta["id"]} for v in r["amostras"]]})["metafieldsSet"]
        if d["userErrors"]:
            raise SystemExit("amostra %s: %s" % (nome, d["userErrors"]))
    d = auth.gql(store, token, Q_SOLTA, {"f": [{"id": branca, "referencesToRemove": [pid]}]})["fileUpdate"]
    if d["userErrors"]:
        raise SystemExit("tirar a branca %s: %s" % (r["nome_novo"], d["userErrors"]))
    log[mid] = {"produto": r["produto"], "pid": pid, "posicao_galeria": i + 1, "modo": modo, "nome": nome,
                "midia": volta["id"], "url": volta["image"]["url"], "midia_branca_tirada": branca,
                "alt": r["alt"], "variacoes": r["variacoes"], "amostras": r["amostras"],
                "quando": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
    json.dump(log, open(logpath, "w"), ensure_ascii=False, indent=1)
    print("  %-14s pos %2d  %-14s %s  var %d  amostras %d" % (r["produto"][:14], i + 1, modo, nome[:66],
                                                             len(r["variacoes"]), len(r["amostras"])), flush=True)


def conferir(log, pasta):
    import numpy as np
    from PIL import Image
    ruins = 0
    for mid, r in log.items():
        dados = urllib.request.urlopen(urllib.request.Request(r["url"], headers={"Accept": "image/png"}), timeout=120).read()
        cdn = np.array(Image.open(io.BytesIO(dados)).convert("RGBA"))
        loc = np.array(Image.open(os.path.join(pasta, "orig", mid.rsplit("/", 1)[1] + ".png")).convert("RGBA"))
        ok = cdn.shape == loc.shape and (cdn == loc).all()
        r["cdn_identico"] = bool(ok)
        if not ok:
            ruins += 1
            print("DIFERE:", r["nome"], cdn.shape, loc.shape)
    print("conferidas %d, diferentes %d" % (len(log), ruins))
    return ruins


def main():
    pasta = sys.argv[1]
    modo = sys.argv[2] if len(sys.argv) > 2 else ""
    troca = json.load(open(os.path.join(pasta, "achatar_fundo_site.log.json")))
    logpath = os.path.join(pasta, "restaurar_recorte_site.log.json")
    log = json.load(open(logpath)) if os.path.exists(logpath) else {}
    if modo == "--conferir":
        conferir(log, pasta)
        json.dump(log, open(logpath, "w"), ensure_ascii=False, indent=1)
        return
    store, token = auth.get_token()
    so = [x for x in os.environ.get("SO", "").split(",") if x]
    limite = int(os.environ.get("LIMITE", "0")) or None
    feitas = 0
    for mid, r in sorted(troca.items(), key=lambda kv: (kv[1]["pid"], kv[1]["posicao_galeria"])):
        if mid in log or (so and mid not in so):
            continue
        if modo != "--restaurar":
            print("  %-14s pos %2d  %s" % (r["produto"][:14], r["posicao_galeria"],
                                           "subir " + nome_recorte(r["url_antiga"]) if r.get("antiga_apagada") else "religar " + nome_cdn(r["url_antiga"])))
            continue
        restaurar_uma(store, token, mid, r, pasta, log, logpath)
        feitas += 1
        if limite and feitas >= limite:
            print("parei no limite de %d" % limite); return
    print("ok" if modo == "--restaurar" else "conferência ok (nada mudou)")


if __name__ == "__main__":
    main()
