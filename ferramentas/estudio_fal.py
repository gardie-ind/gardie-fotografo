# -*- coding: utf-8 -*-
"""Estúdio fal.ai — re-render por referência e retoque por máscara (Fotógrafo Gardie).

Dois usos:
  - CRIAR CENA: re-render do produto a partir da referência (Kontext / Seedream), chamado
    pelo ensaio.py; a fidelidade é conferida no RESULTADO.
  - RETOCAR: máscara + FLUX Fill só para defeito LOCAL (texto fantasma, objeto pequeno);
    aí os pixels fora da máscara ficam intocados por construção. Nunca para criar cena.

Credenciais (fora do repo): variável FAL_KEY ou ~/.config/gardie/fal.json:
  { "api_key": "..." }

Subcomandos:
  py estudio_fal.py recortar foto.png pasta_saida/
      -> BiRefNet v2: salva <base>-recorte.png (produto com fundo transparente).
         A máscara vem do canal alfa do recorte (gerada localmente).
  py estudio_fal.py mascara-fundo recorte.png mask-fundo.png [--folga 4]
      -> LOCAL (sem API): alfa do recorte -> máscara binária do FUNDO
         (branco = área que a IA pode repintar), com o produto dilatado
         --folga px para a área repintável não encostar na borda dele.
  py estudio_fal.py fundo original.png mask-fundo.png saida.png --prompt "..."
      -> FLUX Fill: repinta SÓ a área branca da máscara (o cenário);
         os pixels do produto ficam intocados POR CONSTRUÇÃO.
  py estudio_fal.py relight foto.png saida.png --prompt "..."
      -> IC-Light v2 (EXPERIMENTAL): re-ilumina a imagem para casar com o
         cenário. Este passo TOCA pixels do produto — sempre conferir com o
         checklist de guia/criterios.md antes de aprovar.
  py estudio_fal.py rerender-kontext ref.jpg saida.png --prompt "..." [--aspecto 1:1]
      -> re-render por referência (FLUX Kontext Max; usa 1 imagem).
  py estudio_fal.py rerender-seedream ref.jpg saida.png --prompt "..." [--ref-extra b.png c.png]
      -> re-render por referência (Seedream 4 edit, 1280x1280; aceita várias refs).

Regras: guia/ deste repositório. Rodar com PYTHONUTF8=1 py.
"""
import os
import re
import sys
import json
import time
import base64
import shutil
import argparse
import http.client
import urllib.request
import urllib.error

CFG = os.path.expanduser("~/.config/gardie/fal.json")
FILA = "https://queue.fal.run"
MIME = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}

MODELO_RECORTE = "fal-ai/birefnet/v2"
MODELO_FUNDO = "fal-ai/flux-pro/v1/fill"
MODELO_RELIGHT = "fal-ai/iclight-v2"
MODELO_KONTEXT = "fal-ai/flux-pro/kontext/max"
MODELO_SEEDREAM = "fal-ai/bytedance/seedream/v4/edit"


def na_nuvem():
    """Sessão do Claude Code na nuvem: a chave pode ser uma credencial de API do
    ambiente, que o proxy anexa à requisição sem a sessão ver."""
    return os.environ.get("CLAUDE_CODE_REMOTE", "").strip().lower() == "true"


def chave():
    """FAL_KEY no ambiente vence o arquivo de config. Na nuvem, sem chave local,
    devolve "" e conta com a credencial de API do ambiente."""
    k = os.environ.get("FAL_KEY", "").strip()
    if k:
        return k
    if not os.path.exists(CFG):
        if na_nuvem():
            return ""
        raise SystemExit("Credencial fal ausente: defina FAL_KEY ou crie %s com "
                         "{\"api_key\": \"...\"} (chave em fal.ai/dashboard/keys)" % CFG)
    with open(CFG, encoding="utf-8-sig") as f:
        k = (json.load(f).get("api_key") or "").strip()
    if not k and not na_nuvem():
        raise SystemExit("Credencial fal ausente: %s sem \"api_key\"" % CFG)
    return k


def _autenticar(req, key):
    """Sem chave, segue sem cabeçalho: na nuvem o proxy anexa Authorization: Key ..."""
    if key:
        req.add_header("Authorization", "Key %s" % key)


def data_uri(path):
    ext = os.path.splitext(path)[1].lower()
    b64 = base64.b64encode(open(path, "rb").read()).decode()
    return "data:%s;base64,%s" % (MIME.get(ext, "image/png"), b64)


def _req(url, body=None, key=None):
    req = urllib.request.Request(url, data=json.dumps(body).encode() if body else None,
                                 method="POST" if body else "GET")
    _autenticar(req, key)
    if body:
        req.add_header("Content-Type", "application/json")
    try:
        return json.loads(urllib.request.urlopen(req, timeout=120).read().decode())
    except urllib.error.HTTPError as e:
        if e.code in (401, 403) and not key:
            raise SystemExit("O fal recusou a chamada sem chave (HTTP %d). Na nuvem, cadastre no "
                             "ambiente a credencial de API para fal.run e *.fal.run (cabeçalho "
                             "Authorization, prefixo Key) ou a variável FAL_KEY." % e.code)
        raise SystemExit("Erro HTTP %s em %s: %s" % (e.code, url, e.read().decode(errors="replace")[:600]))


def _transitorio(e):
    """Rede caiu ou o fal respondeu 429/5xx: vale consultar de novo (o job segue na fila)."""
    if isinstance(e, SystemExit):
        return bool(re.search(r"Erro HTTP (429|5\d\d)\b", str(e)))
    return isinstance(e, (OSError, http.client.HTTPException))


def _cancelar(sub, key):
    """Tira o job da fila (melhor esforço), para um timeout não virar cobrança em dobro."""
    if not sub.get("cancel_url"):
        return
    req = urllib.request.Request(sub["cancel_url"], method="PUT")
    _autenticar(req, key)
    try:
        urllib.request.urlopen(req, timeout=30).read()
    except Exception:
        pass


def rodar(modelo, entrada, timeout=300):
    """Submete na fila do fal, faz poll até concluir e devolve o resultado.
    Falha transitória no poll ou na leitura do resultado não perde o job já pago: consulta
    de novo até o timeout. No timeout, cancela o job antes de desistir."""
    key = chave()
    sub = _req("%s/%s" % (FILA, modelo), entrada, key)
    status_url, resp_url = sub["status_url"], sub["response_url"]
    t0, erros = time.time(), 0
    while True:
        st = {}
        try:
            st = _req(status_url, key=key)
            if st.get("status") == "COMPLETED":
                return _req(resp_url, key=key)
            erros = 0
        except (OSError, http.client.HTTPException, SystemExit) as e:
            erros += 1
            if not _transitorio(e) or erros > 5:
                raise
        if st.get("status") in ("FAILED", "CANCELLED"):
            raise SystemExit("Job %s: %s" % (st.get("status"), json.dumps(st)[:600]))
        if time.time() - t0 > timeout:
            _cancelar(sub, key)
            raise SystemExit("Timeout (%ds) esperando %s (job cancelado)" % (timeout, modelo))
        time.sleep(2)


def baixar(url, out, tentativas=3):
    """Baixa o resultado com timeout (urlretrieve não tem: podia travar a thread para sempre)."""
    for k in range(1, tentativas + 1):
        try:
            with urllib.request.urlopen(url, timeout=120) as r, open(out, "wb") as f:
                shutil.copyfileobj(r, f)
            break
        except (OSError, http.client.HTTPException):
            if k == tentativas:
                raise
            time.sleep(3)
    print("OK: %s (%d KB)" % (out, os.path.getsize(out) // 1024))


def recortar(foto, pasta):
    os.makedirs(pasta, exist_ok=True)
    base = os.path.splitext(os.path.basename(foto))[0]
    r = rodar(MODELO_RECORTE, {
        "image_url": data_uri(foto),
        "output_format": "png",
        "refine_foreground": True,
    })
    out = os.path.join(pasta, base + "-recorte.png")
    baixar(r["image"]["url"], out)
    return out


def mascara_fundo(recorte, out, folga=4):
    """Local, sem API: alfa do recorte -> máscara do fundo (branco = repintar)."""
    from PIL import Image, ImageFilter
    im = Image.open(recorte)
    if "A" not in im.getbands():
        raise SystemExit("O recorte não tem canal alfa: %s" % recorte)
    alfa = im.getchannel("A")
    produto = alfa.point(lambda p: 255 if p > 8 else 0)  # binária, alfa fraco conta como produto
    if folga > 0:
        produto = produto.filter(ImageFilter.MaxFilter(2 * folga + 1))  # dilata o produto
    fundo = produto.point(lambda p: 0 if p else 255)
    fundo.save(out)
    print("OK: %s (folga=%dpx; branco = área repintável)" % (out, folga))
    return out


def fundo(original, mascara, out, prompt):
    r = rodar(MODELO_FUNDO, {
        "image_url": data_uri(original),
        "mask_url": data_uri(mascara),
        "prompt": prompt,
        "output_format": "png",
        "safety_tolerance": "2",
    })
    baixar(r["images"][0]["url"], out)
    return out


def relight(foto, out, prompt):
    r = rodar(MODELO_RELIGHT, {
        "image_url": data_uri(foto),
        "prompt": prompt,
        "output_format": "png",
    })
    baixar(r["images"][0]["url"], out)
    return out


def rerender_kontext(ref, out, prompt, aspect_ratio="1:1", seed=None):
    """Re-render por referência via FLUX Kontext Max (1 imagem de referência)."""
    entrada = {
        "prompt": prompt,
        "image_url": data_uri(ref),
        "aspect_ratio": aspect_ratio,
        "output_format": "png",
        "safety_tolerance": "2",
    }
    if seed is not None:
        entrada["seed"] = int(seed)
    r = rodar(MODELO_KONTEXT, entrada)
    baixar(r["images"][0]["url"], out)
    return out


def rerender_seedream(ref, out, prompt, refs_extra=None, image_size=None, seed=None):
    """Re-render por referência via Seedream 4 edit. Aceita várias refs: `ref` pode ser
    um caminho ou uma lista (a 1ª é a principal), mais `refs_extra`."""
    refs = list(ref) if isinstance(ref, (list, tuple)) else [ref]
    urls = [data_uri(x) for x in refs + list(refs_extra or [])]
    entrada = {
        "prompt": prompt,
        "image_urls": urls,
        "image_size": image_size or {"width": 1280, "height": 1280},
    }
    if seed is not None:
        entrada["seed"] = int(seed)
    r = rodar(MODELO_SEEDREAM, entrada)
    baixar(r["images"][0]["url"], out)
    # O Seedream pode devolver JPEG mesmo pedindo .png; garante a promessa da extensão.
    from PIL import Image
    Image.open(out).convert("RGB").save(out, "PNG")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("recortar")
    p.add_argument("foto")
    p.add_argument("pasta")

    p = sub.add_parser("mascara-fundo")
    p.add_argument("recorte")
    p.add_argument("saida")
    p.add_argument("--folga", type=int, default=4)

    p = sub.add_parser("fundo")
    p.add_argument("original")
    p.add_argument("mascara")
    p.add_argument("saida")
    p.add_argument("--prompt", required=True)

    p = sub.add_parser("relight")
    p.add_argument("foto")
    p.add_argument("saida")
    p.add_argument("--prompt", required=True)

    p = sub.add_parser("rerender-kontext")
    p.add_argument("ref")
    p.add_argument("saida")
    p.add_argument("--prompt", required=True)
    p.add_argument("--aspecto", default="1:1")

    p = sub.add_parser("rerender-seedream")
    p.add_argument("ref")
    p.add_argument("saida")
    p.add_argument("--prompt", required=True)
    p.add_argument("--ref-extra", nargs="*", default=[])

    a = ap.parse_args()
    if a.cmd == "recortar":
        recortar(a.foto, a.pasta)
    elif a.cmd == "mascara-fundo":
        mascara_fundo(a.recorte, a.saida, a.folga)
    elif a.cmd == "fundo":
        fundo(a.original, a.mascara, a.saida, a.prompt)
    elif a.cmd == "relight":
        relight(a.foto, a.saida, a.prompt)
    elif a.cmd == "rerender-kontext":
        rerender_kontext(a.ref, a.saida, a.prompt, a.aspecto)
    elif a.cmd == "rerender-seedream":
        rerender_seedream(a.ref, a.saida, a.prompt, a.ref_extra)


if __name__ == "__main__":
    main()
