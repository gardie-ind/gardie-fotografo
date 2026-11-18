"""Prancha antes/depois: por foto, a foto inteira antes e depois e o zoom no logo antes e depois.
uso: python3 -I prancha.py <orig> <limpo> <caixas.json> <titulo> <saida.jpg> [prefixo de fid]"""
import json, sys, glob, os
from PIL import Image, ImageDraw, ImageFont
o, l, cj, titulo, saida = sys.argv[1:6]; pre = sys.argv[6] if len(sys.argv) > 6 else ''
C = {k: v for k, v in json.load(open(cj)).items() if k.startswith(pre)}
try:
    F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 22); f2 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 30)
except Exception:
    F = f2 = ImageFont.load_default()
def plano(p):
    im = Image.open(p).convert('RGBA'); b = Image.new('RGBA', im.size, (255, 255, 255, 255)); b.alpha_composite(im); return b.convert('RGB')
T, ZW, ZH, CAB = 380, 520, 380, 34
linhas = []
for fid, cfg in C.items():
    x0, y0, x1, y1 = cfg['caixa'] if isinstance(cfg, dict) else cfg
    a = plano(glob.glob(os.path.join(o, fid + '.*'))[0]); d = plano(os.path.join(l, fid + '.png'))
    fa, fd = a.copy(), d.copy(); fa.thumbnail((T, T), Image.LANCZOS); fd.thumbnail((T, T), Image.LANCZOS)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2; W = max((x1 - x0) * 2.0, (y1 - y0) * 6); H = W * ZH / ZW
    bb = (int(cx - W / 2), int(cy - H / 2), int(cx + W / 2), int(cy + H / 2))
    za, zd = a.crop(bb).resize((ZW, ZH), Image.LANCZOS), d.crop(bb).resize((ZW, ZH), Image.LANCZOS)
    row = Image.new('RGB', (2 * T + 2 * ZW + 50, T + CAB), 'white'); dr = ImageDraw.Draw(row)
    dr.text((6, 4), fid, fill=(20, 20, 20), font=F)
    xs = [0, T + 10, 2 * T + 30, 2 * T + ZW + 50]
    for x, im, lab in zip(xs, (fa, fd, za, zd), ('antes', 'depois', 'zoom antes', 'zoom depois')):
        row.paste(im, (x + (T - im.width) // 2 if im.width < T else x, CAB + (T - im.height) // 2 if im.height < T else CAB))
        dr.text((x + 6, CAB + 4), lab, fill=(200, 30, 30), font=F)
    dr.rectangle((xs[0] + (T - fa.width) // 2 + int((bb[0]) * fa.width / a.width), CAB + (T - fa.height) // 2 + int(bb[1] * fa.height / a.height),
                  xs[0] + (T - fa.width) // 2 + int(bb[2] * fa.width / a.width), CAB + (T - fa.height) // 2 + int(bb[3] * fa.height / a.height)), outline=(200, 30, 30), width=2)
    linhas.append(row)
Wt = linhas[0].width; sh = Image.new('RGB', (Wt, 60 + sum(r.height + 12 for r in linhas)), (238, 238, 238))
ImageDraw.Draw(sh).text((10, 12), titulo, fill=(10, 10, 10), font=f2); y = 60
for r in linhas: sh.paste(r, (0, y)); y += r.height + 12
sh.save(saida, quality=88); print(saida, sh.size)
