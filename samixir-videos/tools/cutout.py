"""Cut a product off a white studio background: flood-fill near-white from the border,
keep everything enclosed, soften the edge, and strip the white fringe."""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

src, dst = sys.argv[1], sys.argv[2]
thr = int(sys.argv[3]) if len(sys.argv) > 3 else 236
crop_bottom = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0

im = np.asarray(Image.open(src).convert("RGB")).astype(np.float32)
h, w, _ = im.shape
mn = im.min(axis=2)
chroma = im.max(axis=2) - mn
bg_like = (mn >= thr) & (chroma < 18)

labels, _ = ndimage.label(bg_like)
border = np.unique(np.concatenate([labels[0], labels[-1], labels[:, 0], labels[:, -1]]))
border = border[border != 0]
bg = np.isin(labels, border)

fg = ~bg
# drop specks: keep the largest foreground blob plus anything big
lab, n = ndimage.label(fg)
if n > 1:
    sizes = ndimage.sum(fg, lab, range(1, n + 1))
    keep = np.zeros(n + 1, bool)
    keep[1:] = sizes >= max(sizes.max() * 0.02, 200)
    fg = keep[lab]
fg = ndimage.binary_fill_holes(fg) | (fg & ~ndimage.binary_fill_holes(fg))
fg = ndimage.binary_erosion(fg, iterations=1)

alpha = ndimage.gaussian_filter(fg.astype(np.float32), 0.9)
# inside the soft band, let near-white pixels fade further (anti-aliased edges on white)
band = (alpha > 0.01) & (alpha < 0.99)
white_a = np.clip((255.0 - mn) / (255.0 - thr + 1e-3), 0, 1)
alpha = np.where(band, np.minimum(alpha, np.maximum(white_a, alpha * 0.6)), alpha)

if crop_bottom > 0:
    cut = int(h * (1 - crop_bottom))
    ramp = np.linspace(1, 0, h - cut)[:, None]
    alpha[cut:] *= ramp

# un-premultiply against white to remove the halo
a = np.clip(alpha, 1e-3, 1)[..., None]
rgb = np.clip((im - (1 - a) * 255.0) / a, 0, 255)
rgba = np.dstack([rgb, alpha * 255]).astype(np.uint8)

# trim to content with a small margin
ys, xs = np.where(alpha > 0.02)
pad = 6
y0, y1 = max(ys.min() - pad, 0), min(ys.max() + pad + 1, h)
x0, x1 = max(xs.min() - pad, 0), min(xs.max() + pad + 1, w)
Image.fromarray(rgba[y0:y1, x0:x1], "RGBA").save(dst, optimize=True)
print(dst, rgba[y0:y1, x0:x1].shape)
