# -*- coding: utf-8 -*-
"""Backup de aprovadas/ no Google Drive, em imagens › Cloud › aprovadas, no
drive compartilhado do marketing (pedido do Thiago em 22/10/2026).

O envio passa pelo n8n da Gardie (fluxo "Fotógrafo: backup das fotos no
Drive", id rJrYUOUjCrR1xmTi), que grava com o login do Google Drive de lá.
Cada foto vai num POST para o webhook, com a pasta de destino e o nome na
query. As pastas do Drive estão em drive-cloud-pastas.json, uma por
subpasta de aprovadas/; subpasta nova precisa ser criada no Drive e
acrescentada ao mapa antes do envio.

Uso:
  N8N_BACKUP_TOKEN=... python3 backup_drive.py              # envia o que falta
  python3 backup_drive.py --simular                         # só lista

O token é o do filtro do webhook no n8n (opção onlyRunIf) e não vai para o
repositório. O que já subiu fica em drive-cloud-enviados.json (caminho ->
MD5 e id no Drive): arquivo com o mesmo MD5 é pulado; arquivo alterado sobe
de novo, como um arquivo novo ao lado do antigo. Nada é apagado no Drive.
A rede da sessão precisa liberar n8n.gardie.com.br, e o fluxo fica desligado
entre um backup e outro: publique-o antes e despublique depois.
"""
import argparse
import concurrent.futures
import hashlib
import json
import mimetypes
import os
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
WEBHOOK = 'https://n8n.gardie.com.br/webhook/fotografo-backup-62671b1798c277a7'
PASTAS = os.path.join(HERE, 'drive-cloud-pastas.json')
ENVIADOS = os.path.join(HERE, 'drive-cloud-enviados.json')


def md5(caminho):
    h = hashlib.md5()
    with open(caminho, 'rb') as f:
        for bloco in iter(lambda: f.read(1 << 20), b''):
            h.update(bloco)
    return h.hexdigest()


def enviar(caminho, pasta, nome, token):
    url = WEBHOOK + '?' + urllib.parse.urlencode({'folder': pasta, 'name': nome})
    dados = open(caminho, 'rb').read()
    cab = {'Content-Type': mimetypes.guess_type(nome)[0] or 'application/octet-stream',
           'x-fotografo-token': token}
    for tentativa in range(4):
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, dados, cab, method='POST'), timeout=600)
            corpo = r.read()
            try:
                return json.loads(corpo)
            except ValueError:
                raise SystemExit('Resposta inesperada do n8n para %s (token ou fluxo desligado?): %r' % (nome, corpo[:200]))
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and tentativa < 3:
                time.sleep(2 ** (tentativa + 2))
                continue
            raise SystemExit('%s: HTTP %s %s' % (nome, e.code, e.read()[:300]))


def principal():
    ap = argparse.ArgumentParser(description='Backup de aprovadas/ no Google Drive pelo n8n.')
    ap.add_argument('--origem', default=os.path.join(HERE, '..', 'aprovadas'))
    ap.add_argument('--simular', action='store_true', help='só lista o que iria subir')
    ap.add_argument('--paralelo', type=int, default=4, help='envios simultâneos (padrão 4)')
    a = ap.parse_args()
    origem = os.path.abspath(a.origem)
    pastas = json.load(open(PASTAS, encoding='utf-8'))
    enviados = json.load(open(ENVIADOS, encoding='utf-8')) if os.path.exists(ENVIADOS) else {}

    fila, iguais = [], 0
    for sub in sorted(os.listdir(origem)):
        d = os.path.join(origem, sub)
        if not os.path.isdir(d) or sub.startswith(('.', '_')):
            continue
        if sub not in pastas:
            raise SystemExit('Subpasta sem pasta no Drive: %s (crie no Drive e acrescente em %s)' % (sub, PASTAS))
        for nome in sorted(os.listdir(d)):
            if nome.startswith('.'):
                continue
            rel = '%s/%s' % (sub, nome)
            soma = md5(os.path.join(d, nome))
            if enviados.get(rel, {}).get('md5') == soma:
                iguais += 1
            else:
                fila.append((rel, sub, nome, soma))
    total = sum(os.path.getsize(os.path.join(origem, r)) for r, *_ in fila)
    print('%d a enviar (%.0f MB), %d já no Drive' % (len(fila), total / 1e6, iguais))
    if a.simular or not fila:
        return

    token = os.environ.get('N8N_BACKUP_TOKEN')
    if not token:
        raise SystemExit('Defina N8N_BACKUP_TOKEN (o token do filtro do webhook no n8n).')
    trava, feitos = threading.Lock(), [0]

    def um(item):
        rel, sub, nome, soma = item
        r = enviar(os.path.join(origem, rel), pastas[sub], nome, token)
        if r.get('md5') != soma:
            raise SystemExit('%s: MD5 no Drive (%s) diferente do local (%s)' % (rel, r.get('md5'), soma))
        with trava:
            enviados[rel] = {'md5': soma, 'id': r.get('id')}
            json.dump(enviados, open(ENVIADOS, 'w', encoding='utf-8'), indent=1, sort_keys=True)
            feitos[0] += 1
            print('  %d/%d %s' % (feitos[0], len(fila), rel), flush=True)

    with concurrent.futures.ThreadPoolExecutor(a.paralelo) as ex:
        for f in [ex.submit(um, item) for item in fila]:
            f.result()
    print('Fim: %d enviados e conferidos pelo MD5, %.0f MB.' % (len(fila), total / 1e6))


if __name__ == '__main__':
    sys.exit(principal())
