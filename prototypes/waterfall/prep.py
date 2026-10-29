"""Prepares the waterfall test's layers from master.png and clean.png (run in this folder: python prep.py).
   fg.npy    the foreground: the ferns and the dark rocks along the bottom, cut pixel-exact from the master (sway.npy marks the fern part)
   bg.npy    what shows behind them: the clean picture's water and bank, aligned and colour-matched to the master;
             wherever the clean picture has rocks of its own that the master doesn't, it's filled with water instead
   masks.npz the parts that move by colour cycling (both falls, the foam, the pool) and the pool's geometry"""
import numpy as np
from PIL import Image
from scipy import ndimage as nd

M = np.asarray(Image.open('master.png').convert('RGB')).astype(np.float32)
C = np.asarray(Image.open('clean.png').convert('RGB')).astype(np.float32)
H, W = M.shape[:2]; g = lambda a: a @ np.array([.299, .587, .114], np.float32)
Mg, Cg = g(M), g(C); rows = np.arange(H)[:, None]; cols = np.arange(W)[None, :]
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)

# ---------- 1. align: a uniform scale and shift first (fitted above the water), then tile by tile ----------
def warp(img, s, tx, ty): return nd.map_coordinates(img, [yy * s + ty, xx * s + tx], order=1, mode='nearest')
reg = (slice(60, 600), slice(80, 1600)); small = lambda a: a[reg][::3, ::3]
best = None; Yr, Xr, Mr = yy[reg][::3, ::3], xx[reg][::3, ::3], small(Mg)
for s in np.arange(.985, 1.036, .005):
    for tx in range(-48, 49, 4):
        for ty in range(-28, 29, 4):
            e = np.abs(nd.map_coordinates(Cg, [Yr * s + ty, Xr * s + tx], order=1, mode='nearest') - Mr).mean()
            if best is None or e < best[0]: best = (e, s, tx, ty)
e, s0, tx0, ty0 = best
for step in (2, 1, .5, .25):
    for s in (s0 - .0012 * step, s0, s0 + .0012 * step):
        for tx in (tx0 - step, tx0, tx0 + step):
            for ty in (ty0 - step, ty0, ty0 + step):
                e = np.abs(nd.map_coordinates(Cg, [Yr * s + ty, Xr * s + tx], order=1, mode='nearest') - Mr).mean()
                if e < best[0]: best = (e, s, tx, ty)
    e, s0, tx0, ty0 = best
print('global fit: scale %.4f shift %.1f, %.1f  (error %.1f)' % (s0, tx0, ty0, e))
A = np.stack([warp(C[..., c], s0, tx0, ty0) for c in range(3)], -1); Ag = g(A)

rough = nd.binary_dilation((Mg < 60) & (rows > 600), iterations=3)          # keep the master's ferns and rocks out of the matching
T, R = 48, 6; fx = np.zeros((H // T + 1, W // T + 1)); fy = np.zeros_like(fx); ok = np.zeros_like(fx, bool)
for ty in range(0, H, T):
    for tx in range(0, W, T):
        y0, y1, x0, x1 = ty, min(H, ty + T), tx, min(W, tx + T); keep = ~rough[y0:y1, x0:x1]
        if keep.sum() < T * T * .3: continue
        a = Mg[y0:y1, x0:x1]; b0 = (1e9, 0, 0)
        for dy in range(-R, R + 1):
            for dx in range(-R, R + 1):
                ya, yb, xa, xb = y0 - dy, y1 - dy, x0 - dx, x1 - dx
                if ya < 0 or xa < 0 or yb > H or xb > W: continue
                e = np.abs(Ag[ya:yb, xa:xb] - a)[keep].mean()
                if e < b0[0]: b0 = (e, dx, dy)
        fx[ty // T, tx // T], fy[ty // T, tx // T] = b0[1], b0[2]; ok[ty // T, tx // T] = True
for f in (fx, fy):
    idx = nd.distance_transform_edt(~ok, return_distances=False, return_indices=True); f[:] = f[tuple(idx)]
    f[:] = nd.median_filter(f, 3); f[:] = nd.gaussian_filter(f, 1.)
DX = nd.zoom(fx, (H / fx.shape[0], W / fx.shape[1]), order=1)[:H, :W]; DY = nd.zoom(fy, (H / fy.shape[0], W / fy.shape[1]), order=1)[:H, :W]
A = np.stack([nd.map_coordinates(A[..., c], [yy - DY, xx - DX], order=1, mode='nearest') for c in range(3)], -1); Ag = g(A)
print('tile refinement: x %.1f..%.1f, y %.1f..%.1f' % (fx[ok].min(), fx[ok].max(), fy[ok].min(), fy[ok].max()))

# ---------- 2. the foreground: ferns and the dark rocks along the bottom, from the master ----------
diff0 = np.sqrt(((M - A) ** 2).sum(-1))
dark = (Mg < 62) & (rows > 600) & ((diff0 > 35) | (rows > 730))   # near the waterline, reflections are in both pictures: only what the clean one lacks is foreground
lab, n = nd.label(dark); touch = np.unique(lab[H - 4:, :])        # rooted at the bottom edge (the bank's reflections touch the sides, not the bottom)
core = np.isin(lab, touch[touch > 0]) & (rows > 640)
for it in range(3):                                                    # leaflets separated by a lit edge join if close
    near = nd.binary_dilation(core, iterations=3); ids = np.unique(lab[near & dark]); core |= np.isin(lab, ids[ids > 0]) & (rows > 640)
diff = np.sqrt(((M - A) ** 2).sum(-1))
rim = nd.binary_dilation(core, iterations=2) & ~core & (diff > 28) & (rows > 630)   # the lit edges of fronds and rocks
fg = core | rim
holes = nd.binary_fill_holes(fg) & ~fg; hl, hn = nd.label(holes); hs = nd.sum(holes, hl, range(hn + 1))
fg |= np.isin(hl, [i for i in range(1, hn + 1) if hs[i] <= 80])
# which of it sways: the ferns (fine, ragged), not the rocks (big, smooth, rounded)
mu = nd.uniform_filter(Mg, 9); sd = np.sqrt(np.maximum(nd.uniform_filter(Mg * Mg, 9) - mu * mu, 0))   # fronds are busy, rocks are smooth
smooth = nd.binary_opening(fg & (sd < 7), iterations=2)
rl, rn = nd.label(smooth); rs = nd.sum(smooth, rl, range(rn + 1))
rocks = nd.binary_fill_holes(np.isin(rl, [i for i in range(1, rn + 1) if rs[i] > 1500]))
rocks = nd.binary_dilation(rocks, iterations=2) & fg & ~nd.binary_dilation(fg & (sd > 12) & ~rocks, iterations=1)
sway = fg & ~rocks
np.save('fg.npy', fg); np.save('sway.npy', sway); np.save('rocks.npy', rocks)

# ---------- 3. the background behind them: the clean water and bank, its own rocks replaced with water ----------
crock = nd.binary_dilation(((Ag < 60) | (A[..., 0] > A[..., 2] + 4)) & (rows > 690), iterations=5)      # the clean picture's own rocks, lit tops and ripple rings
cl, cn = nd.label(crock); cs = nd.sum(crock, cl, range(cn + 1)); crock = np.isin(cl, [i for i in range(1, cn + 1) if cs[i] > 300])
BG = A.copy()
for y in np.where(crock.any(1))[0]:                                    # water runs in horizontal streaks: fill each row from the open water beside it
    r = crock[y]; xs = np.where(~r)[0]
    if not len(xs): continue
    for x in np.where(r)[0]:
        j = np.searchsorted(xs, x); src = xs[min(j, len(xs) - 1)] if j < len(xs) else xs[-1]
        span = abs(src - x); src2 = src + span if src > x else src - span       # mirror the water from beyond the rock
        BG[y, x] = A[y, int(np.clip(src2, 0, W - 1))] if not r[int(np.clip(src2, 0, W - 1))] else A[y, src]
keep = ~rough & ~crock
for c in range(3):                                                      # match the master's colours, locally
    w = keep.astype(np.float32); s = 40
    mm = nd.gaussian_filter(np.where(keep, M[..., c], 0), s) / np.maximum(nd.gaussian_filter(w, s), 1e-3)
    ma = nd.gaussian_filter(np.where(keep, BG[..., c], 0), s) / np.maximum(nd.gaussian_filter(w, s), 1e-3)
    BG[..., c] = BG[..., c] - ma + mm
BG = np.clip(BG, 0, 255)
hull = nd.binary_fill_holes(nd.binary_closing(rocks, iterations=6))
_, (iy, ix) = nd.distance_transform_edt(~rocks, return_indices=True)
BG = np.where((hull & ~rocks)[..., None], M[iy, ix], BG)
np.save('bg.npy', BG)

# ---------- 4. what moves by colour cycling ----------
base = np.where(sway[..., None], BG, M); B = base; r, gg, b = B[..., 0], B[..., 1], B[..., 2]; lum = g(B)
blueish = (b > r + 25) & (lum > 105)
fall1 = blueish & (cols > 1085) & (cols < 1260) & (rows > 80) & (rows < 600)
fall2 = blueish & (cols > 1480) & (cols < 1535) & (rows > 45) & (rows < 545)
foam = (lum > 150) & (np.abs(r - b) < 70) & (cols > 1000) & (cols < 1340) & (rows >= 560) & (rows < 655) & ~fall1
pool = (rows >= 645) & (b > r + 8) & ~fg & ~foam & (lum > 40)
streak = pool & (cols > 1080) & (cols < 1280) & (lum > 120)
np.savez('masks.npz', fall1=fall1, fall2=fall2, foam=foam, pool=pool, streak=streak)
for k, m in dict(fall1=fall1, fall2=fall2, foam=foam, pool=pool, streak=streak, fg=fg, sway=sway).items(): print(k, int(m.sum()))
v = np.where(fg[..., None], np.where(sway[..., None], M, M * .5 + [80, 0, 0]), [255, 0, 255]).astype(np.uint8)[560:]
Image.fromarray(v).resize((836, 190)).save('shots/check_fg.png')
v = (M * .35).astype(np.uint8); v[fall1 | fall2] = [0, 200, 255]; v[foam] = [255, 255, 255]; v[pool] = (v[pool] * .4 + [0, 120, 60]).astype(np.uint8); v[streak] = [255, 220, 0]
Image.fromarray(v).resize((836, 470)).save('shots/check_masks.png')
Image.fromarray(np.where(sway[..., None], BG, M).astype(np.uint8)[560:]).resize((836, 190)).save('shots/check_behind.png')
print('done')
