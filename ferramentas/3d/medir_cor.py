# -*- coding: utf-8 -*-
"""Matiz e croma (CIELAB) medianos numa região de um render (pixels não saturados).
Uso: python medir_cor.py img.png x0,y0,x1,y1 [x0,y0,x1,y1 ...]"""
import sys
import numpy as np
from PIL import Image
def lin(c):
    c = c / 255.0; return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
def lab(rgb):
    M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    t = (rgb @ M.T) / np.array([0.95047, 1, 1.08883])
    f = np.where(t > 0.008856, np.cbrt(t), 7.787 * t + 16 / 116)
    L = 116 * f[:, 1] - 16; a = 500 * (f[:, 0] - f[:, 1]); b = 200 * (f[:, 1] - f[:, 2])
    return L, np.hypot(a, b), (np.degrees(np.arctan2(b, a)) + 360) % 360
a = np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(float)
for box in sys.argv[2:]:
    x0, y0, x1, y1 = map(int, box.split(','))
    px = a[y0:y1, x0:x1].reshape(-1, 3); mx = px.max(1)
    px = px[(mx > 30) & (mx < 250)]
    L, C, h = lab(lin(px))
    print('%s: n=%d L %.0f C %.1f h %.0f' % (box, len(px), np.median(L), np.median(C), np.median(h)))
