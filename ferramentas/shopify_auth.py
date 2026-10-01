"""Autenticacao compartilhada para os scripts Shopify da Gardie.

Le credenciais de um arquivo FORA do repositorio (nunca versionado):
  Windows: %USERPROFILE%\\.config\\gardie\\shopify.json
  Outros:  ~/.config/gardie/shopify.json

Formato do arquivo:
  { "store": "...myshopify.com", "client_id": "...", "client_secret": "shpss_..." }

Fallback: variaveis de ambiente SHOPIFY_STORE / SHOPIFY_CLIENT_ID /
SHOPIFY_CLIENT_SECRET, ou SHOPIFY_ADMIN_TOKEN (token shpat_ direto).

O token Admin (shpat_) e emitido sob demanda via grant client_credentials
e expira em ~24h, por isso nao e guardado: re-emitimos a cada execucao.
"""
import os
import json
import urllib.request

API_VERSION = "2025-01"


def _config_path():
    return os.path.join(os.path.expanduser("~"), ".config", "gardie", "shopify.json")


def load_config():
    cfg = {}
    path = _config_path()
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8-sig") as f:  # -sig: JSON salvo com BOM no Windows
            cfg = json.load(f)
    store = (cfg.get("store") or os.environ.get("SHOPIFY_STORE", "")).strip()
    client_id = (cfg.get("client_id") or os.environ.get("SHOPIFY_CLIENT_ID", "")).strip()
    client_secret = (cfg.get("client_secret") or os.environ.get("SHOPIFY_CLIENT_SECRET", "")).strip()
    direct_token = os.environ.get("SHOPIFY_ADMIN_TOKEN", "").strip()
    if not store:
        raise SystemExit(
            "Loja Shopify nao configurada. Crie %s ou defina SHOPIFY_STORE." % _config_path()
        )
    return store, client_id, client_secret, direct_token


def get_token():
    """Retorna um token Admin (shpat_). Usa SHOPIFY_ADMIN_TOKEN se definido;
    senao emite via client_credentials com client_id + client_secret."""
    store, client_id, client_secret, direct_token = load_config()
    if direct_token:
        return store, direct_token
    if not client_id or not client_secret:
        raise SystemExit(
            "Sem client_id/client_secret em %s nem SHOPIFY_ADMIN_TOKEN no ambiente." % _config_path()
        )
    url = "https://%s/admin/oauth/access_token" % store
    body = json.dumps({
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials",
    }).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.loads(r.read().decode("utf-8"))
    return store, data["access_token"]


def admin_endpoint(store):
    return "https://%s/admin/api/%s/graphql.json" % (store, API_VERSION)


def gql(store, token, query, variables=None):
    body = json.dumps({"query": query, "variables": variables or {}}).encode("utf-8")
    req = urllib.request.Request(admin_endpoint(store), data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("X-Shopify-Access-Token", token)
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.loads(r.read().decode("utf-8"))
    if "errors" in data:
        raise SystemExit("Erro GraphQL: " + json.dumps(data["errors"], ensure_ascii=False))
    return data["data"]
