# -*- coding: utf-8 -*-
"""Gera imagens via Gemini (Nano Banana) — texto e/ou composição com fotos reais
de produto (image-to-image).

Credenciais (fora do repo): variável GEMINI_API_KEY ou ~/.config/gardie/gemini.json:
  { "api_key": "...", "image_model": "gemini-3-pro-image" }

Modelo: o de --model; senão o "image_model" do config; senão gemini-3-pro-image.
Qual modelo vai para produção sai do ensaio comparativo (ensaio.py), não daqui.
As referências vão ANTES do texto no pedido (recomendação do Google para prompt com imagem).

Uso:
  py gerar_imagem.py --prompt-file cena.txt --out saida.png --aspect 16:9
  py gerar_imagem.py --prompt "..." --ref capa.png,traseira.png --out cena.png --aspect 1:1 --model gemini-2.5-flash-image

Regras: guia/ deste repositório. Produto SEMPRE via --ref (foto real); nunca deixar
a IA inventar o espelho. Revisar fidelidade do produto.
"""
import os
import sys
import json
import base64
import argparse
import urllib.request
import urllib.error

CFG = os.path.expanduser("~/.config/gardie/gemini.json")
MIME = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}


def na_nuvem():
    """Sessão do Claude Code na nuvem. Lá a chave pode ser uma credencial de API
    do ambiente: o proxy a anexa à requisição e a sessão nunca a vê."""
    return os.environ.get("CLAUDE_CODE_REMOTE", "").strip().lower() == "true"


def load_cfg():
    """(chave, modelo padrão). GEMINI_API_KEY no ambiente vence o arquivo de config.
    Na nuvem, sem chave local, devolve chave vazia e conta com a credencial do ambiente."""
    c = {}
    if os.path.exists(CFG):
        with open(CFG, encoding="utf-8-sig") as f:
            c = json.load(f)
    key = os.environ.get("GEMINI_API_KEY", "").strip() or c.get("api_key", "")
    if not key and not na_nuvem():
        raise SystemExit("Credencial Gemini ausente: defina GEMINI_API_KEY ou crie %s "
                         "com {\"api_key\": \"...\"}" % CFG)
    return key, c.get("image_model", "gemini-3-pro-image")


def autenticar(req, key):
    """Chave no cabeçalho x-goog-api-key (nunca na URL). Sem chave, segue sem
    cabeçalho: na nuvem, o proxy anexa a credencial de API do ambiente."""
    if key:
        req.add_header("x-goog-api-key", key)


def erro_de_acesso(codigo, key):
    if codigo in (401, 403) and not key:
        return ("A API do Gemini recusou a chamada sem chave (HTTP %d). Na nuvem, cadastre no "
                "ambiente a credencial de API para generativelanguage.googleapis.com (cabeçalho "
                "x-goog-api-key, sem prefixo) ou a variável GEMINI_API_KEY." % codigo)
    return None


def ref_part(path):
    ext = os.path.splitext(path)[1].lower()
    data = base64.b64encode(open(path, "rb").read()).decode()
    return {"inline_data": {"mime_type": MIME.get(ext, "image/png"), "data": data}}


def gerar(prompt, out, refs=None, aspect="16:9", model=None):
    key, default_model = load_cfg()
    model = model or default_model
    parts = [ref_part(r) for r in (refs or [])] + [{"text": prompt}]
    body = {
        "contents": [{"parts": parts}],
        "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": aspect}},
    }
    url = "https://generativelanguage.googleapis.com/v1beta/models/%s:generateContent" % model
    req = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST")
    req.add_header("Content-Type", "application/json")
    autenticar(req, key)
    try:
        resp = urllib.request.urlopen(req, timeout=180)
    except urllib.error.HTTPError as e:
        msg = e.read().decode(errors="replace")
        acesso = erro_de_acesso(e.code, key)
        if acesso:
            raise SystemExit(acesso)
        if e.code == 429 and "free_tier" in msg:
            raise SystemExit("FATURAMENTO desabilitado: o free tier nao gera imagem. "
                             "Habilite billing no projeto Google Cloud e tente de novo.")
        raise SystemExit("Erro HTTP %s: %s" % (e.code, msg[:500]))
    data = json.loads(resp.read().decode())
    cands = data.get("candidates") or []
    if not cands:
        raise SystemExit("Resposta sem candidatos (bloqueio?): " + json.dumps(data.get("promptFeedback", data))[:400])
    for p in (cands[0].get("content") or {}).get("parts") or []:
        inl = p.get("inlineData") or p.get("inline_data")
        if inl and not p.get("thought"):  # rascunho do "thinking" (Gemini 3 Pro) não é a imagem final
            open(out, "wb").write(base64.b64decode(inl["data"]))
            print("OK: %s (%d KB)" % (out, os.path.getsize(out) // 1024))
            return out
    raise SystemExit("Resposta sem imagem (finishReason=%s): %s"
                     % (cands[0].get("finishReason"), json.dumps(data)[:400]))


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--prompt")
    g.add_argument("--prompt-file")
    ap.add_argument("--out", required=True)
    ap.add_argument("--ref", help="fotos de produto reais, separadas por virgula (a 1a e a principal)")
    ap.add_argument("--aspect", default="16:9")
    ap.add_argument("--model")
    a = ap.parse_args()
    prompt = a.prompt or open(a.prompt_file, encoding="utf-8-sig").read()  # -sig: BOM do Bloco de Notas
    refs = [x.strip() for x in a.ref.split(",")] if a.ref else []
    gerar(prompt, a.out, refs, a.aspect, a.model)


if __name__ == "__main__":
    main()
