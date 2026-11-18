"""Troca no site as 3 stills recortadas do Svelte 10479 (cromo, gold, red gold) pelas novas -2, com a
canopla lisa e a borda azulada do cristal (Thiago 02/11/2026 22:44: "Após corrigir estas imagens, subir
para o Shopify apagando as antigas").

Para cada uma: sobe a nova com o mesmo alt da antiga (com o #hashtag da variação), põe na mesma posição da
galeria, liga à variação, tira a antiga do produto e apaga o arquivo antigo do Shopify Files. As antigas
foram baixadas antes para /mnt/project-files/fotografo/2026-11-02-svelte-canopla/shopify-antes/ (midias.json +
PNG), para dar para desfazer. Rodado em 02/11/2026; o registro está em trocar_svelte_site.log.json.

Depois (Thiago, 03/11/2026 01:12, sobre a -2: "Está com um rechupe do plástico e uma deformidade do reflexo.
Essa peça é lisa e o reflexo é liso"): a -3, com o reflexo liso (`svelte_reflexo_liso.py`), entra no lugar
da -2 do mesmo jeito, achando a mídia da -2 pelo registro.

uso: python3 trocar_svelte_site.py [--versao 3]            # só confere
     python3 trocar_svelte_site.py [--versao 3] --trocar   # troca e apaga as antigas (padrão: versão 2)"""
import json, os, sys, time
sys.path.insert(0, '/home/user/gardie-fotografo/ferramentas')
os.environ.setdefault("SHOPIFY_STORE", os.environ.get("SHOPIFY_FLAG_STORE", ""))
import shopify_auth as auth
from trocar_4500k_site import staged_upload, Q_PROD, Q_ADD, Q_REORDER, Q_VAR, Q_SOLTA

KIT = os.path.dirname(os.path.abspath(__file__))
PID = 'gid://shopify/Product/7355777876071'
LOG = os.path.join(KIT, 'trocar_svelte_site.log.json')
TROCAS = [  # (variação, mídia antiga, arquivo novo)
    ('10479CR', 'gid://shopify/MediaImage/29271309156455', 'espelho-de-aumento-parede-svelte-cromado-gardie-2.png'),
    ('10479GL', 'gid://shopify/MediaImage/29271309189223', 'espelho-de-aumento-parede-svelte-dourado-gardie-2.png'),
    ('10479GL.RD', 'gid://shopify/MediaImage/29271309221991', 'espelho-de-aumento-parede-svelte-red-gold-gardie-2.png'),
]
Q_DEL = 'mutation($ids:[ID!]!){fileDelete(fileIds:$ids){deletedFileIds userErrors{field message}}}'
Q_FILES = 'query($q:String!){files(first:20,query:$q){nodes{id ... on MediaImage{image{url}}}}}'


def trocas(versao, log):
    if versao == 2:
        return TROCAS
    out = []
    for sku, _, nome in TROCAS:
        ant = nome.replace('-gardie-2.png', '-gardie-%d.png' % (versao - 1))
        out.append((sku, log[ant]["midia_nova"], nome.replace('-gardie-2.png', '-gardie-%d.png' % versao)))
    return out


def main(trocar, versao=2):
    store, token = auth.get_token()
    log = json.load(open(LOG)) if os.path.exists(LOG) else {}
    for sku, velha_id, nome in trocas(versao, log):
        p = auth.gql(store, token, Q_PROD, {"id": PID})["product"]
        midias = p["media"]["nodes"]
        ja = [m for m in midias if m.get("image") and m["image"]["url"].split("/files/")[-1].startswith(nome[:-4])]
        if ja:
            print(sku, "já trocada:", nome); continue
        idx = [i for i, m in enumerate(midias) if m["id"] == velha_id]
        if len(idx) != 1:
            raise SystemExit("%s: mídia antiga %s não está no produto" % (sku, velha_id))
        i = idx[0]; velha = midias[i]
        var = [v["id"] for v in p["variants"]["nodes"] if v["sku"] == sku]
        homonimos = auth.gql(store, token, Q_FILES, {"q": "filename:%s" % nome[:-4]})["files"]["nodes"]
        print("%-10s pos %2d  alt %r -> %s  variação %s  homônimos no Files: %d" % (sku, i + 1, velha["alt"], nome, var, len(homonimos)))
        if not trocar:
            continue
        caminho = os.path.join(KIT, '..', 'aprovadas', sku, nome)
        src = staged_upload(store, token, caminho, nome)
        d = auth.gql(store, token, Q_ADD, {"p": {"id": PID}, "m": [{"originalSource": src, "alt": velha["alt"], "mediaContentType": "IMAGE"}]})["productUpdate"]
        if d["userErrors"]:
            raise SystemExit("productUpdate %s: %s" % (nome, d["userErrors"]))
        nova = None
        for _ in range(100):
            ms = auth.gql(store, token, Q_PROD, {"id": PID})["product"]["media"]["nodes"]
            cand = [m for m in ms if m.get("image") and m["image"]["url"].split("/files/")[-1].startswith(nome[:-4])] or \
                   [m for m in ms if m["id"] not in {x["id"] for x in midias} and m["status"] != "READY"]
            if cand and cand[0]["status"] in ("READY", "FAILED") and cand[0].get("image"):
                nova = cand[0]; break
            time.sleep(3)
        if not nova or nova["status"] != "READY":
            raise SystemExit("processamento falhou: " + nome)
        d = auth.gql(store, token, Q_REORDER, {"id": PID, "moves": [{"id": nova["id"], "newPosition": str(i)}]})["productReorderMedia"]
        if d["mediaUserErrors"]:
            raise SystemExit("reorder %s: %s" % (nome, d["mediaUserErrors"]))
        d = auth.gql(store, token, Q_VAR, {"p": PID, "v": [{"id": v, "mediaId": nova["id"]} for v in var]})["productVariantsBulkUpdate"]
        if d["userErrors"]:
            raise SystemExit("variação %s: %s" % (nome, d["userErrors"]))
        d = auth.gql(store, token, Q_SOLTA, {"f": [{"id": velha_id, "referencesToRemove": [PID]}]})["fileUpdate"]
        if d["userErrors"]:
            raise SystemExit("tirar a antiga %s: %s" % (velha_id, d["userErrors"]))
        d = auth.gql(store, token, Q_DEL, {"ids": [velha_id]})["fileDelete"]
        if d["userErrors"]:
            raise SystemExit("apagar a antiga %s: %s" % (velha_id, d["userErrors"]))
        log[nome] = {"variacao": sku, "posicao_galeria": i + 1, "midia_nova": nova["id"], "url_nova": nova["image"]["url"],
                     "midia_antiga_apagada": velha_id, "url_antiga": velha["image"]["url"], "alt": velha["alt"],
                     "quando": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
        json.dump(log, open(LOG, "w"), ensure_ascii=False, indent=1)
        print("   trocada e antiga apagada")
    print("ok" if trocar else "conferência ok (nada mudou)")


if __name__ == "__main__":
    v = int(sys.argv[sys.argv.index("--versao") + 1]) if "--versao" in sys.argv else 2
    main("--trocar" in sys.argv, v)
