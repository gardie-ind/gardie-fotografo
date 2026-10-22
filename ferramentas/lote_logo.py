"""Um LUX nos 5 acabamentos: logo a laser (logo_laser.py) e padrão de luz
(luz_padrao.py) nos 3 tons. Sai, por acabamento, a apagada nova e as 3 ligadas,
mais os recortes da cabeça para a prancha.

uso: HALO=0.6 [ACABS=red-gold] [ACAB_DIR=pasta] [CROMO_DIR=pasta] python3 lote_logo.py <modelo> <código> <Ø vidro mm> <saida>

Fontes, todas sem o logo a laser: o cromado é o par ligado e apagado de
CROMO_DIR/<código>CR/ (os dois últimos .jpg); os outros acabamentos, a
recoloração de ACAB_DIR/<modelo>/<modelo>-<acabamento>-{ligado,desligado}.png,
que fica na pasta do projeto, fora do git. Não rode com as aprovadas atuais
como fonte: desde 22/10/2026 elas já têm o logo a laser e a luz. Para refazer,
tire o par cromado do commit c1a59b9 (git show) para uma pasta e passe-a em
CROMO_DIR."""
import sys, os, glob, json
import numpy as np
from PIL import Image
import logo_laser
from luz_padrao import ler, acender, RENDER
from luz_anel import srgb, YW

APROVADAS = os.environ.get('CROMO_DIR', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'aprovadas'))
ACAB = os.environ.get('ACAB_DIR', '/mnt/project-files/fotografo/2026-10-21-acabamentos')
ACABAMENTOS = os.environ.get('ACABS', 'cromado,brushed-nickel,gold,red-gold,black-matte').split(',')

modelo, codigo, vidro, saida = sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4]
os.makedirs(f'{saida}/cabeca', exist_ok=True); os.makedirs(f'{saida}/_tmp', exist_ok=True)
info = {}
for acab in ACABAMENTOS:
    if acab == 'cromado':
        fs = sorted(glob.glob(f'{APROVADAS}/{codigo}CR/*.jpg')); lig, apa = fs[-2], fs[-1]; ext = '.jpg'
    else:
        lig, apa = f'{ACAB}/{modelo}/{modelo}-{acab}-ligado.png', f'{ACAB}/{modelo}/{modelo}-{acab}-desligado.png'; ext = '.png'
    tmp = f'{saida}/_tmp/{acab}-ligado-logo.png'
    out_apa = f'{saida}/{modelo}-{acab}-desligado{ext}'
    info[acab] = logo_laser.principal(lig, apa, vidro, tmp, out_apa)
    L1, A1 = ler(tmp); L2, A2 = ler(out_apa)
    if ext == '.jpg':
        A1 = np.full(A1.shape, 255, np.uint8)
    same = (np.abs(A1.astype(int) - A2.astype(int)) <= 2)[..., None]
    YE = np.clip(L1 - L2 - 0.004, 0, None) @ YW.astype(np.float32)
    ys, xs = np.where(YE > 0.2); m = int(0.08 * max(np.ptp(ys), np.ptp(xs)))
    caixa = (max(xs.min() - m, 0), max(ys.min() - m, 0), min(xs.max() + m, A1.shape[1]), min(ys.max() + m, A1.shape[0]))
    orig = Image.open(lig)
    def cabeca(im, nome):
        bg = Image.new('RGB', im.size, (255, 255, 255)); bg.paste(im, (0, 0), im if im.mode == 'RGBA' else None)
        t = bg.crop(caixa); t.thumbnail((700, 700), Image.LANCZOS); t.save(f'{saida}/cabeca/{nome}.jpg', quality=92)
    cabeca(Image.open(out_apa), f'{acab}-desligado')
    for tom, T in RENDER.items():
        out = np.where(same, acender(L1, L2, T), L1)
        rgb = (srgb(out) * 255 + 0.5).astype(np.uint8)
        nome = f'{saida}/{modelo}-{acab}-ligado-{tom}k'
        if ext == '.jpg':
            im = Image.fromarray(rgb)
            im.save(nome + ext, quality=95, qtables=orig.quantization, subsampling=0, exif=orig.info.get('exif', b''))
        else:
            im = Image.fromarray(np.dstack([rgb, A1])); im.save(nome + ext, optimize=True)
        cabeca(im, f'{acab}-{tom}k')
    os.remove(tmp)
    print(modelo, acab, json.dumps(info[acab])[:160], flush=True)
json.dump(info, open(f'{saida}/logo-medidas.json', 'w'), indent=1)
