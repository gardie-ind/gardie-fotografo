# -*- coding: utf-8 -*-
"""Upload de imagens para o Shopify Files (staged upload -> fileCreate -> poll)
e impressao das URLs CDN.

Uso:
  py upload_shopify.py imagem.png --remote nome-no-shopify.png --alt "texto alt"
  py upload_shopify.py --lote manifest.json

Manifest de lote: lista JSON de objetos
  [{"local": "arquivo.png", "remoto": "nome-remoto.png", "alt": "texto alt"}]

Caminhos relativos sao resolvidos a partir do diretorio atual; se nao
existirem la, tenta aprovadas/ (na raiz deste repositorio).
"""
import argparse
import json
import mimetypes
import os
import time
import uuid
import urllib.request
import shopify_auth as auth

HERE = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.abspath(os.path.join(HERE, "..", "aprovadas"))

Q_STAGED = ('mutation($input: [StagedUploadInput!]!){ stagedUploadsCreate(input: $input){ '
            'stagedTargets{ url resourceUrl parameters{ name value } } userErrors{ field message } } }')
Q_CREATE = ('mutation($files: [FileCreateInput!]!){ fileCreate(files: $files){ '
            'files{ id fileStatus } userErrors{ field message } } }')
Q_NODE = 'query($id: ID!){ node(id: $id){ ... on MediaImage { fileStatus image{ url } } } }'


def resolver(caminho):
    if os.path.exists(caminho):
        return os.path.abspath(caminho)
    alternativo = os.path.join(IMG_DIR, caminho)
    if os.path.exists(alternativo):
        return alternativo
    raise SystemExit("Arquivo nao encontrado: %s (nem em %s)" % (caminho, IMG_DIR))


def subir(store, token, local, remoto, alt):
    path = resolver(local)
    mime = mimetypes.guess_type(remoto)[0] or "image/png"

    v1 = {"input": [{"resource": "FILE", "filename": remoto, "mimeType": mime, "httpMethod": "POST"}]}
    d = auth.gql(store, token, Q_STAGED, v1)["stagedUploadsCreate"]
    if d["userErrors"]:
        raise SystemExit("stagedUploads %s: %s" % (local, d["userErrors"]))
    t = d["stagedTargets"][0]

    boundary = uuid.uuid4().hex
    body = b""
    for p in t["parameters"]:
        body += ("--%s\r\nContent-Disposition: form-data; name=\"%s\"\r\n\r\n%s\r\n"
                 % (boundary, p["name"], p["value"])).encode()
    body += ("--%s\r\nContent-Disposition: form-data; name=\"file\"; filename=\"%s\"\r\n"
             "Content-Type: %s\r\n\r\n" % (boundary, remoto, mime)).encode()
    body += open(path, "rb").read()
    body += ("\r\n--%s--\r\n" % boundary).encode()
    req = urllib.request.Request(t["url"], data=body, method="POST")
    req.add_header("Content-Type", "multipart/form-data; boundary=%s" % boundary)
    urllib.request.urlopen(req, timeout=120)

    v2 = {"files": [{"originalSource": t["resourceUrl"], "alt": alt, "contentType": "IMAGE"}]}
    d2 = auth.gql(store, token, Q_CREATE, v2)["fileCreate"]
    if d2["userErrors"]:
        raise SystemExit("fileCreate %s: %s" % (local, d2["userErrors"]))
    fid = d2["files"][0]["id"]

    for _ in range(30):
        n = auth.gql(store, token, Q_NODE, {"id": fid})["node"]
        if n["fileStatus"] == "READY" and n.get("image"):
            return n["image"]["url"]
        if n["fileStatus"] == "FAILED":
            raise SystemExit("processamento FAILED: %s (%s)" % (fid, local))
        time.sleep(2)
    raise SystemExit("timeout esperando READY: %s (%s)" % (fid, local))


def main():
    ap = argparse.ArgumentParser(description="Sobe imagens para o Shopify Files e imprime as URLs CDN.")
    ap.add_argument("imagem", nargs="?", help="arquivo local (modo arquivo unico)")
    ap.add_argument("--remote", help="nome do arquivo no Shopify (padrao: mesmo nome local)")
    ap.add_argument("--alt", default="", help="texto alt da imagem")
    ap.add_argument("--lote", help="manifest JSON com lista de {local, remoto, alt}")
    args = ap.parse_args()

    if args.lote:
        with open(args.lote, "r", encoding="utf-8-sig") as f:  # -sig: JSON salvo com BOM no Windows
            lote = json.load(f)
    elif args.imagem:
        remoto = args.remote or os.path.basename(args.imagem)
        lote = [{"local": args.imagem, "remoto": remoto, "alt": args.alt}]
    else:
        ap.error("informe uma imagem ou --lote manifest.json")

    store, token = auth.get_token()
    for item in lote:
        url = subir(store, token, item["local"], item["remoto"], item.get("alt", ""))
        print("%s -> %s" % (item["local"], url))


if __name__ == "__main__":
    main()
