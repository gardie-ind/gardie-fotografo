"""Refaz as fotos do Flex (10578) e do Mobile (10431) no catálogo e nos encartes com as versões sem o "gardie" no vidro.
Mesmo recorte, fundo, tamanho e qualidade do refazer.py de 2026-11-09-fotos-canonicas-pdf; só muda a foto de origem.
Guarda as de antes em antes-1011-sem-gardie/ e acerta a versão citada nas ambientadas dos encartes.
Uso: python3 -I refazer_pdf.py <pasta com <ID>.png limpas> <canon.json> <saida>"""
import json, os, re, sys, shutil, glob
import numpy as np
from PIL import Image
LIMPO, CANON, OUT = sys.argv[1:4]
ENC = '/mnt/project-files/fotografo/2026-11-07-encartes'; CAT = '/mnt/project-files/fotografo/2026-11-02-catalogo'
VER = {r[0]: r[3] + 1 for r in json.load(open(CANON))}   # versão que a foto limpa ganha ao ser canonizada
OC, OE = OUT + '/cat', OUT + '/enc'
for d in (OC, OE): os.makedirs(d, exist_ok=True)

def abrir(fid):
    im = Image.open('%s/%s.png' % (LIMPO, fid)); im.load(); return im

def no_branco(im):
    im = im.convert('RGBA'); a = np.asarray(im.getchannel('A'))
    m = a > 8 if a.min() < 250 else np.asarray(im.convert('L')) < 242
    f = Image.new('RGB', im.size, 'white'); f.paste(im, mask=im.getchannel('A'))
    return f, m

def caixa(m):
    ys, xs = np.nonzero(m)
    return int(xs.min()), int(ys.min()), int(xs.max() + 1), int(ys.max() + 1)

def jpg(f, path, q):
    f.save(path, quality=q, optimize=True, progressive=True); return f.size

def lista(fid, path, lado=420, margem=0.01, q=90):
    f, m = no_branco(abrir(fid)); x0, y0, x1, y1 = caixa(m)
    pad = int(round(max(y1 - y0, x1 - x0) * margem))
    x0, y0 = max(0, x0 - pad), max(0, y0 - pad); x1, y1 = min(f.width, x1 + pad), min(f.height, y1 + pad)
    c = f.crop((x0, y0, x1, y1)); s = lado / max(c.size)
    c = c.resize((max(1, round(c.width * s)), max(1, round(c.height * s))), Image.LANCZOS)
    return jpg(c, path, q)

def justa(fid, path, h, q):
    f, m = no_branco(abrir(fid)); c = f.crop(caixa(m))
    return jpg(c.resize((round(c.width * h / c.height), h), Image.LANCZOS), path, q)

def amb(fid, path, lado, q):
    im = abrir(fid).convert('RGB')
    if max(im.size) > lado: im.thumbnail((lado, lado), Image.LANCZOS)
    return jpg(im, path, q)

mapa = {'cat': {}, 'enc': {}}
def reg(doc, fn, fid, size): mapa[doc][fn] = {'id': fid, 'versao': VER[fid], 'w': size[0], 'h': size[1]}
ACABS = ['CR', 'GL', 'GL.RD', 'NK.BU', 'BL.MT']
AMB = {'10578-amb-1.jpg': '10578CR-AMB-01', '10578-amb-2.jpg': '10578GL-AMB-01', '10578-amb-3.jpg': '10578GL.RD-AMB-02',
       '10431-amb-1.jpg': '10431CR-AMB-01', '10431-amb-2.jpg': '10431GL-AMB-02', '10431-amb-3.jpg': '10431GL.RD-AMB-01'}
for ref in ('10578', '10431'):
    for c in ACABS:
        fid = '%s%s-STILL-01' % (ref, c)
        reg('cat', '%s-%s.jpg' % (ref, c), fid, lista(fid, '%s/%s-%s.jpg' % (OC, ref, c)))
        reg('enc', '%s-%s.jpg' % (ref, c), fid, justa(fid, '%s/%s-%s.jpg' % (OE, ref, c), 900, 88))
    fid = ref + 'CR-STILL-01'
    reg('cat', ref + '-grande.jpg', fid, justa(fid, '%s/%s-grande.jpg' % (OC, ref), 900, 90))
    reg('enc', ref + '-heroi.jpg', fid, justa(fid, '%s/%s-heroi.jpg' % (OE, ref), 1700, 88))
for fn, fid in AMB.items(): reg('enc', fn, fid, amb(fid, OE + '/' + fn, 1800, 86))
json.dump(mapa, open(OUT + '/mapa.json', 'w'), indent=1, ensure_ascii=False)

if '--aplicar' in sys.argv:
    BC, BE = CAT + '/antes-1011-sem-gardie', ENC + '/antes-1011-sem-gardie'
    for d in (BC + '/img', BE + '/img'): os.makedirs(d, exist_ok=True)
    for doc, src, bk, novo in (('cat', CAT + '/img', BC, OC), ('enc', ENC + '/site/img', BE, OE)):
        for fn, v in mapa[doc].items():
            antes = Image.open(src + '/' + fn).size
            assert antes == (v['w'], v['h']), (doc, fn, antes, v)   # mesmo tamanho: nada muda no layout
            if not os.path.exists(bk + '/img/' + fn): shutil.copyfile(src + '/' + fn, bk + '/img/' + fn)
            shutil.copyfile(novo + '/' + fn, src + '/' + fn)
    p = ENC + '/site/dados-encarte.js'
    if not os.path.exists(BE + '/dados-encarte.js'): shutil.copyfile(p, BE + '/dados-encarte.js')
    s = open(p, encoding='utf-8').read()
    for fn, fid in AMB.items():
        s, k = re.subn(r'("fonte": "%s \(Fotos canônicas, versão )\d+(\))' % re.escape(fid), lambda m: m.group(1) + str(VER[fid]) + m.group(2), s)
        assert k == 1, fid
    open(p, 'w', encoding='utf-8').write(s)
    print('aplicado')
print('cat', len(mapa['cat']), 'enc', len(mapa['enc']))
