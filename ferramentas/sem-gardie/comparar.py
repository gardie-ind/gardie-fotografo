"""comparar.py <orig> <limpo> <caixas.json> <saida-prefixo> : antes | depois ampliado, 6 por folha"""
import json, sys, glob, os
from PIL import Image, ImageDraw
o, l, cj, pre = sys.argv[1:5]
C = json.load(open(cj)); linhas = []
def abrir(p):
    im = Image.open(p).convert('RGBA'); b = Image.new('RGBA', im.size, (255,255,255,255)); b.alpha_composite(im); return b.convert('RGB')
for fid, cfg in C.items():
    x0,y0,x1,y1 = cfg['caixa'] if isinstance(cfg, dict) else cfg
    a = abrir(glob.glob(os.path.join(o, fid+'.*'))[0]); d = abrir(os.path.join(l, fid+'.png'))
    w, h = x1-x0, y1-y0; cx, cy = (x0+x1)/2, (y0+y1)/2; W = max(w*1.5, h*4); H = W*0.35
    bb = (int(cx-W/2), int(cy-H/2), int(cx+W/2), int(cy+H/2))
    ca, cd = a.crop(bb).resize((600,210), Image.LANCZOS), d.crop(bb).resize((600,210), Image.LANCZOS)
    t = Image.new('RGB', (1200, 230), 'white'); t.paste(ca,(0,20)); t.paste(cd,(600,20))
    dr = ImageDraw.Draw(t); dr.text((4,4), fid+'  antes', fill='black'); dr.text((604,4), 'depois', fill='black'); linhas.append(t)
for k in range(0, len(linhas), 6):
    g = linhas[k:k+6]; sh = Image.new('RGB', (1200, 230*len(g)), 'white')
    for j, t in enumerate(g): sh.paste(t, (0, 230*j))
    sh.save('%s-%d.jpg' % (pre, k//6), quality=90)
