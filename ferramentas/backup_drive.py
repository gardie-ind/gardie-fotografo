# -*- coding: utf-8 -*-
"""Backup de uma pasta do repositório no Google Drive, espelhando subpastas e
nomes. Padrão: aprovadas/ em imagens › Cloud › aprovadas, no drive
compartilhado do marketing (pedido do Thiago em 22/10/2026).

Uso:
  python3 backup_drive.py                       # aprovadas/ -> Cloud/aprovadas
  python3 backup_drive.py --simular             # só conta o que iria subir
  python3 backup_drive.py --origem ../referencias --nome referencias

Credencial: conta de serviço do Google, membro do drive compartilhado como
administrador de conteúdo. A chave JSON vem da variável de ambiente
GOOGLE_SERVICE_ACCOUNT_JSON (o conteúdo do arquivo) ou do arquivo
~/.config/gardie/google-sa.json. Nunca vai para o repositório.

Arquivo que já está no Drive com o mesmo nome e o mesmo MD5 é pulado; com o
mesmo nome e conteúdo diferente, ganha uma nova versão (o Drive guarda a
anterior). Nada é apagado no Drive.
"""
import argparse
import base64
import hashlib
import json
import mimetypes
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
CLOUD = '1WGHfDyHTc3irpUWkDleIwevSo1KA1OHj'   # imagens › Cloud
API = 'https://www.googleapis.com/drive/v3'
UPLOAD = 'https://www.googleapis.com/upload/drive/v3'
PASTA = 'application/vnd.google-apps.folder'
TODOS = {'supportsAllDrives': 'true', 'includeItemsFromAllDrives': 'true'}


def b64url(b):
    return base64.urlsafe_b64encode(b).rstrip(b'=').decode()


def chave():
    txt = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')
    if not txt:
        p = os.path.expanduser('~/.config/gardie/google-sa.json')
        if not os.path.exists(p):
            raise SystemExit('Sem credencial: defina GOOGLE_SERVICE_ACCOUNT_JSON ou crie %s' % p)
        txt = open(p, encoding='utf-8').read()
    return json.loads(txt)


class Drive:
    def __init__(self, sa):
        self.sa, self.token, self.validade = sa, None, 0

    def autenticar(self):
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import padding
        agora = int(time.time())
        cab = b64url(json.dumps({'alg': 'RS256', 'typ': 'JWT'}).encode())
        corpo = b64url(json.dumps({
            'iss': self.sa['client_email'], 'scope': 'https://www.googleapis.com/auth/drive',
            'aud': self.sa['token_uri'], 'iat': agora, 'exp': agora + 3600}).encode())
        pk = serialization.load_pem_private_key(self.sa['private_key'].encode(), password=None)
        assinatura = b64url(pk.sign(('%s.%s' % (cab, corpo)).encode(), padding.PKCS1v15(), hashes.SHA256()))
        dados = urllib.parse.urlencode({'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
                                        'assertion': '%s.%s.%s' % (cab, corpo, assinatura)}).encode()
        try:
            r = json.load(urllib.request.urlopen(urllib.request.Request(self.sa['token_uri'], dados), timeout=60))
        except urllib.error.HTTPError as e:
            raise SystemExit('Token recusado (%s): %s' % (e.code, e.read()[:300]))
        self.token, self.validade = r['access_token'], agora + int(r.get('expires_in', 3600)) - 300

    def pedir(self, metodo, url, params=None, corpo=None, tipo='application/json', cabecalhos=None, bruto=False):
        if params:
            url += '?' + urllib.parse.urlencode(params)
        for tentativa in range(5):
            if time.time() > self.validade:
                self.autenticar()
            h = {'Authorization': 'Bearer ' + self.token}
            if corpo is not None:
                h['Content-Type'] = tipo
            h.update(cabecalhos or {})
            dados = json.dumps(corpo).encode() if isinstance(corpo, dict) else corpo
            try:
                r = urllib.request.urlopen(urllib.request.Request(url, dados, h, method=metodo), timeout=300)
                return r if bruto else json.load(r)
            except urllib.error.HTTPError as e:
                if e.code in (429, 500, 502, 503, 504) and tentativa < 4:
                    time.sleep(2 ** (tentativa + 1))
                    continue
                raise SystemExit('%s %s: %s %s' % (metodo, url.split('?')[0], e.code, e.read()[:400]))

    def listar(self, pai):
        itens, pagina = {}, None
        while True:
            p = dict(TODOS, q="'%s' in parents and trashed = false" % pai, pageSize=1000,
                     fields='nextPageToken, files(id, name, mimeType, md5Checksum, size)')
            if pagina:
                p['pageToken'] = pagina
            r = self.pedir('GET', API + '/files', p)
            for f in r.get('files', []):
                itens[f['name']] = f
            pagina = r.get('nextPageToken')
            if not pagina:
                return itens

    def pasta(self, pai, nome, existentes):
        f = existentes.get(nome)
        if f and f['mimeType'] == PASTA:
            return f['id']
        return self.pedir('POST', API + '/files', dict(TODOS, fields='id'),
                          {'name': nome, 'mimeType': PASTA, 'parents': [pai]})['id']

    def enviar(self, caminho, pai, nome, id_existente=None):
        mime = mimetypes.guess_type(nome)[0] or 'application/octet-stream'
        tam = os.path.getsize(caminho)
        h = {'X-Upload-Content-Type': mime, 'X-Upload-Content-Length': str(tam)}
        if id_existente:
            r = self.pedir('PATCH', UPLOAD + '/files/' + id_existente, dict(TODOS, uploadType='resumable'), {}, cabecalhos=h, bruto=True)
        else:
            r = self.pedir('POST', UPLOAD + '/files', dict(TODOS, uploadType='resumable'),
                           {'name': nome, 'parents': [pai]}, cabecalhos=h, bruto=True)
        sessao = r.headers['Location']
        with open(caminho, 'rb') as f:
            return self.pedir('PUT', sessao, None, f.read(), tipo=mime)


def md5(caminho):
    h = hashlib.md5()
    with open(caminho, 'rb') as f:
        for bloco in iter(lambda: f.read(1 << 20), b''):
            h.update(bloco)
    return h.hexdigest()


def principal():
    ap = argparse.ArgumentParser(description='Espelha uma pasta do repositório no Google Drive.')
    ap.add_argument('--origem', default=os.path.join(HERE, '..', 'aprovadas'))
    ap.add_argument('--destino', default=CLOUD, help='id da pasta no Drive (padrão: imagens › Cloud)')
    ap.add_argument('--nome', help='nome da pasta criada no destino (padrão: o da origem)')
    ap.add_argument('--simular', action='store_true', help='só lista e conta, sem credencial')
    a = ap.parse_args()
    origem = os.path.abspath(a.origem)
    nome = a.nome or os.path.basename(origem)
    arquivos = []
    for raiz, pastas, nomes in os.walk(origem):
        pastas[:] = sorted(p for p in pastas if not p.startswith(('.', '_')))
        arquivos += [os.path.relpath(os.path.join(raiz, n), origem) for n in sorted(nomes) if not n.startswith('.')]
    total = sum(os.path.getsize(os.path.join(origem, r)) for r in arquivos)
    print('%s: %d arquivos, %.0f MB -> %s/%s' % (origem, len(arquivos), total / 1e6, a.destino, nome))
    if a.simular:
        return

    d = Drive(chave())
    ids = {'': d.pasta(a.destino, nome, d.listar(a.destino))}
    conteudo = {}

    def pasta(rel):          # id da subpasta no Drive, criada se faltar
        if rel not in ids:
            pai = os.path.dirname(rel)
            ids[rel] = d.pasta(pasta(pai), os.path.basename(rel), itens(pai))
        return ids[rel]

    def itens(rel):          # o que já existe na subpasta, por nome
        if rel not in conteudo:
            conteudo[rel] = d.listar(pasta(rel))
        return conteudo[rel]

    novos = iguais = versoes = enviados = 0
    for rel in arquivos:
        sub, arq = os.path.split(rel)
        local = os.path.join(origem, rel)
        remoto = itens(sub).get(arq)
        if remoto and remoto.get('md5Checksum') == md5(local):
            iguais += 1
            continue
        d.enviar(local, pasta(sub), arq, remoto['id'] if remoto else None)
        enviados += os.path.getsize(local)
        if remoto:
            versoes += 1
        else:
            novos += 1
        print('  %s %s' % ('versão' if remoto else 'novo  ', rel), flush=True)
    print('Fim: %d novos, %d com nova versão, %d iguais (pulados), %.0f MB enviados.'
          % (novos, versoes, iguais, enviados / 1e6))


if __name__ == '__main__':
    sys.exit(principal())
