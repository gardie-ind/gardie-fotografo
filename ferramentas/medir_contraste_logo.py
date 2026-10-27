"""Contraste do logo gravado no cromado: traço × vidro em volta, em sRGB (luminância)."""
import sys, glob, json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
P='../padrao2'; A='/home/user/gardie-fotografo/aprovadas'
Y=lambda a:(a[...,:3]@np.array([.2126,.7152,.0722]))
for m,c in (('flex-lux','10554'),('mobile-lux','10455'),('visage-lux','10509'),('royale-lux','10288'),('classique-lux','10202')):
    med=json.load(open(f'{P}/{m}/logo-medidas.json'))['cromado']; cx,cy=map(int,med['logo_novo_centro']); r=int(med['logo_novo_largura_px']*0.7)
    bx=(slice(cy-r//3,cy+r//3),slice(cx-r,cx+r))
    fs=sorted(glob.glob(f'{A}/{c}CR/*.jpg')); orig=np.asarray(Image.open(fs[-1]).convert('RGB')).astype(float)[bx]
    nova=np.asarray(Image.open(f'{P}/{m}/{m}-cromado-desligado.jpg').convert('RGB')).astype(float)[bx]
    tr=np.abs(Y(nova)-Y(orig))>20
    viz=ndi.binary_dilation(tr,iterations=int(med['logo_novo_largura_px']*0.06)+6)&~ndi.binary_dilation(tr,iterations=int(med['logo_novo_largura_px']*0.03)+3)
    out=[f'{m:14s} traços={tr.sum():5d}']
    for k in ('desligado','ligado-3000k','ligado-4500k','ligado-6000k'):
        im=np.asarray(Image.open(f'{P}/{m}/{m}-cromado-{k}.jpg').convert('RGB')).astype(float)[bx]
        y=Y(im); out.append(f'{k}: traço {np.median(y[tr]):.0f} vidro {np.median(y[viz]):.0f}')
    print(' | '.join(out))
