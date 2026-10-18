"""Make a dark-background variant of a product cut-out.

The white-background cut-outs keep the grey floor shadow under the product and the white
highlights inside clear lids; on the blue studio backdrop both read as white blobs. This turns
light, low-chroma pixels below the product's base line into a soft black shadow, and (for clear
lids) fades bright white highlights toward transparent. Output keeps the input's size.

usage: studio_cutout.py IN.png OUT.png FLOOR_Y [LID_Y [FROST [SHADOW]]]
  FLOOR_Y  fraction of height below which light pixels are floor shadow
  LID_Y    optional fraction of height above which bright whites are clear plastic (0 = none)
  FROST    opacity of the brightest clear plastic, 0..1 (default 0.8)
  SHADOW   strength of the kept floor shadow, 0..1 (default 0.85; 0 drops it for a floating product)
"""
import sys
import numpy as np
from PIL import Image

src, dst, floor_y = sys.argv[1], sys.argv[2], float(sys.argv[3])
lid_y = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0
frost_lvl = float(sys.argv[5]) if len(sys.argv) > 5 else 0.8
shadow_k = float(sys.argv[6]) if len(sys.argv) > 6 else 0.85

im = np.asarray(Image.open(src).convert("RGBA")).astype(np.float32)
rgb, a = im[..., :3], im[..., 3] / 255.0
h, w = a.shape
lum = rgb @ np.array([0.299, 0.587, 0.114])
mn = rgb.min(axis=2)
chroma = rgb.max(axis=2) - mn
rows = (np.arange(h) / h)[:, None]

# ---- floor shadow ----
band = np.clip((rows - floor_y) / 0.015, 0, 1)  # soft seam across the base line
dark = np.clip((250 - lum) / 110, 0, 1)  # white floor -> 0, mid grey shadow -> ~0.6
shadow_a = a * dark * shadow_k
keep = np.clip((140 - lum) / 50, 0, 1)  # dark product parts (feet, trays) stay as they are
grey = np.clip((40 - chroma) / 20, 0, 1)  # only neutral pixels count as floor
t = band * grey * (1 - keep)
new_a = a * (1 - t) + shadow_a * t
new_rgb = rgb * (1 - t[..., None])  # shadow pixels go to black

# ---- clear lids: close the ragged silhouette, then read bright whites as frosted plastic ----
if lid_y > 0:
    from scipy import ndimage

    top = int(h * lid_y)
    pad = 40  # close over a taller slice so the erosion border never bites into the kept rows
    solid_ext = a[: top + pad] > 0.5
    yy, xx = np.mgrid[-12:13, -12:13]
    closed = ndimage.binary_closing(solid_ext, structure=(xx**2 + yy**2) <= 144, iterations=1)
    closed = (ndimage.binary_fill_holes(closed) | solid_ext)[:top]
    solid = solid_ext[:top]
    holes = closed & ~solid
    region = np.zeros_like(a, dtype=bool)
    region[:top] = closed
    filled = np.zeros_like(a, dtype=bool)
    filled[:top] = holes
    new_rgb[filled] = (238, 243, 250)
    new_a[filled] = 1.0
    ramp = np.clip((lid_y - rows) / 0.03, 0, 1) * region
    frost = np.clip((22 - chroma) / 10, 0, 1)
    frost = np.where(filled, 1.0, frost)
    lvl = frost_lvl + (1 - frost_lvl) * np.clip((235 - mn) / 60, 0, 1)
    lvl = np.where(filled, frost_lvl, lvl)
    lid = ramp * frost
    new_a = new_a * (1 - lid) + new_a * lvl * lid
    # smooth the frosted area a little and trim anything outside the closed silhouette
    smooth = ndimage.gaussian_filter(new_a, 1.2)
    new_a = np.where(lid > 0.5, smooth, new_a)
    soft = ndimage.gaussian_filter(region.astype(np.float32), 1.0)
    soft[top - 2 :] = 1.0
    new_a = np.minimum(new_a, soft)

out = np.dstack([np.clip(new_rgb, 0, 255), np.clip(new_a, 0, 1) * 255]).astype(np.uint8)
Image.fromarray(out, "RGBA").save(dst, optimize=True)
print(dst, out.shape)
