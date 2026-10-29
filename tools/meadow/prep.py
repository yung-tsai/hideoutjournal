"""Prepares the valley test page's layers from master.png and clean.png:
   bg.npy (the clean background aligned and colour-matched under the foreground grass), fg.npy (the grass and ferns cut from the master),
   clouds (cut from the master), the pine (cut from the master, with a tree-free sky behind it).
   python prep.py   (in a working folder with master.png and clean.png; see build_page.py)"""
import numpy as np
from PIL import Image
from scipy import ndimage as nd

M = np.asarray(Image.open('master.png').convert('RGB')).astype(np.float32)
C = np.asarray(Image.open('clean.png').convert('RGB')).astype(np.float32)
H, W = M.shape[:2]; g = lambda a: a[..., 0] * .3 + a[..., 1] * .59 + a[..., 2] * .11
rows = np.arange(H)[:, None]; colsx = np.arange(W)[None, :]

# ---------- 1. the clean background, aligned tile by tile (it was slightly redrawn) and colour-matched ----------
Mg, Cg = g(M), g(C)
rough = nd.binary_dilation((Mg < 70) & (rows > 560), iterations=3)   # keep the foreground out of the matching
T = 48; R = 10; fx = np.zeros((H // T + 1, W // T + 1)); fy = np.zeros_like(fx); ok = np.zeros_like(fx, bool)
for ty in range(0, H, T):
    for tx in range(0, W, T):
        y0, y1, x0, x1 = ty, min(H, ty + T), tx, min(W, tx + T); keep = ~rough[y0:y1, x0:x1]
        if keep.sum() < T * T * .25 or ty < 380: continue
        a = Mg[y0:y1, x0:x1]; best = (1e9, 0, 0)
        for dy in range(-R, R + 1):
            for dx in range(-R, R + 1):
                ya, yb, xa, xb = y0 - dy, y1 - dy, x0 - dx, x1 - dx
                if ya < 0 or xa < 0 or yb > H or xb > W: continue
                e = np.abs(Cg[ya:yb, xa:xb] - a)[keep].mean()
                if e < best[0]: best = (e, dx, dy)
        fx[ty // T, tx // T], fy[ty // T, tx // T] = best[1], best[2]; ok[ty // T, tx // T] = True
for f in (fx, fy):
    idx = nd.distance_transform_edt(~ok, return_distances=False, return_indices=True); f[:] = f[tuple(idx)]
    f[:] = nd.median_filter(f, 3); f[:] = nd.gaussian_filter(f, 1.)
DX = nd.zoom(fx, (H / fx.shape[0], W / fx.shape[1]), order=1)[:H, :W]; DY = nd.zoom(fy, (H / fy.shape[0], W / fy.shape[1]), order=1)[:H, :W]
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
A = np.stack([nd.map_coordinates(C[..., c], [yy - DY, xx - DX], order=1, mode='nearest') for c in range(3)], -1)
BG = A.copy(); keep = ~rough
for c in range(3):
    w = keep.astype(np.float32); s = 40
    mm = nd.gaussian_filter(np.where(keep, M[..., c], 0), s) / np.maximum(nd.gaussian_filter(w, s), 1e-3)
    ma = nd.gaussian_filter(np.where(keep, A[..., c], 0), s) / np.maximum(nd.gaussian_filter(w, s), 1e-3)
    BG[..., c] = A[..., c] - ma + mm
BG = np.clip(BG, 0, 255); np.save('bg.npy', BG); print('background aligned, x', fx[ok].min(), fx[ok].max(), 'y', fy[ok].min(), fy[ok].max())

# ---------- 2. the foreground grass and ferns ----------
Bg = g(BG); BGs = np.stack([nd.gaussian_filter(BG[..., c], 1.5) for c in range(3)], -1)
d = np.sqrt(((M - BGs) ** 2).sum(-1))
strong = (d > 62) & (rows > 560) & ((Mg < Bg - 25) | (Mg < 60))
lab, n = nd.label(strong); touch = np.unique(lab[H - 4:, :]); core = np.isin(lab, touch[touch > 0])
for it in range(3):
    near = nd.binary_dilation(core, iterations=3); ids = np.unique(lab[near & strong]); core |= np.isin(lab, ids[ids > 0])
rim = nd.binary_dilation(core, iterations=2) & ~core & (d > 30) & (rows > 540)
fg = core | rim
holes = nd.binary_fill_holes(fg) & ~fg; hl, hn = nd.label(holes); hs = nd.sum(holes, hl, range(hn + 1))
fg |= np.isin(hl, [i for i in range(1, hn + 1) if hs[i] <= 60])
np.save('fg.npy', fg); print('grass', int(fg.sum()))

# ---------- 3. clouds, against the clean sky ----------
lum = M @ [.299, .587, .114]
Cs = np.roll(np.roll(C, 7, 0), -2, 1)
sky_zone = (rows > 6) & (rows < 335)
ref = np.percentile(M[:, 600:1660], 35, axis=1); ref = np.stack([nd.gaussian_filter1d(ref[:, c], 4) for c in range(3)], -1)
cloud = (np.sqrt(((M - ref[:, None, :]) ** 2).sum(-1)) > 38) & sky_zone & (colsx > 300) & (lum > (ref @ np.array([.299, .587, .114]))[:, None] - 5)
cloud = nd.binary_opening(cloud, iterations=1)
for it in range(3):
    keepS = sky_zone & ~nd.binary_dilation(cloud, iterations=14) & (colsx > 200) & (lum > 70) & ~nd.binary_dilation(lum < 70, iterations=4)
    S = np.empty_like(Cs)
    for c in range(3):
        w = keepS.astype(np.float32); s = 45
        mm = nd.gaussian_filter(np.where(keepS, M[..., c], 0), s) / np.maximum(nd.gaussian_filter(w, s), 1e-4)
        cc = nd.gaussian_filter(np.where(keepS, Cs[..., c], 0), s) / np.maximum(nd.gaussian_filter(w, s), 1e-4)
        S[..., c] = Cs[..., c] - cc + mm
    dS = np.sqrt(((M - S) ** 2).sum(-1))
    cloud = (dS > 20) & sky_zone & (colsx > 300)
    lab, n = nd.label(nd.binary_dilation(cloud, iterations=2)); sz = nd.sum(cloud, lab, range(n + 1)); keep_ids = []
    for i in range(1, n + 1):
        if sz[i] < 1500: continue
        ys, xs = np.where(lab == i)
        if ys.max() - ys.min() < 40: continue        # thin horizon streaks stay where they are
        if xs.min() <= 306: continue                 # sky between the pine's branches, not a cloud
        keep_ids.append(i)
    cloud = np.isin(lab, keep_ids) & cloud
    cloud = nd.binary_fill_holes(nd.binary_closing(cloud, iterations=2))
S = np.clip(S, 0, 255)
lab, n = nd.label(nd.binary_dilation(cloud, iterations=3)); sprites = []
for i in range(1, n + 1):
    m = (lab == i) & cloud; ys, xs = np.where(m)
    if len(xs) < 1500: continue
    cs = m.sum(0); x0, x1 = xs.min(), xs.max(); cuts = []
    if x1 - x0 > 700: cuts = [x0 + 250 + int(np.argmin(cs[x0 + 250:x1 - 250]))]   # the two big clouds touch: split them at the thinnest column
    edges = [x0] + cuts + [x1 + 1]
    for a_, b_ in zip(edges[:-1], edges[1:]):
        mm2 = m.copy(); mm2[:, :a_] = False; mm2[:, b_:] = False
        if mm2.sum() > 1500: sprites.append(mm2)
for sp in sprites:
    ys, xs = np.where(sp); print('cloud x', xs.min(), xs.max(), 'y', ys.min(), ys.max())

# ---------- 4. the whole pine, and a tree-free sky behind it ----------
zone = (colsx < 700) & (rows < 430)
surely = (lum > 95) & ~nd.binary_dilation(lum < 95, iterations=3) & ~nd.binary_dilation(cloud, iterations=6) & (rows < 430)
SM = np.empty_like(M)
for c in range(3):
    acc = np.zeros((H, W), np.float32); wsum = np.zeros((H, W), np.float32)
    for sg in (12, 30, 80):
        a1 = nd.gaussian_filter(np.where(surely, M[..., c], 0), sg); w1 = nd.gaussian_filter(surely.astype(np.float32), sg)
        take = (wsum < .5) & (w1 > 1e-3); acc = np.where(take, a1 / np.maximum(w1, 1e-6), acc); wsum = np.where(take, 1., wsum)
    SM[..., c] = acc
SKY = np.where((np.sqrt(((S - SM) ** 2).sum(-1)) < 18)[..., None], S, SM)
dd = np.sqrt(((M - SM) ** 2).sum(-1))
tree = zone & ~cloud & (dd > 9)
tree |= nd.binary_dilation(tree, iterations=1) & zone & (dd > 4)
tree = nd.binary_closing(tree, iterations=1) & zone
tree &= ~nd.binary_dilation(cloud, iterations=8)
lab, n = nd.label(tree); sz = nd.sum(tree, lab, range(n + 1)); low = set(np.unique(lab[310:430][tree[310:430]]).tolist())
tree = np.isin(lab, [i for i in range(1, n + 1) if sz[i] > 800 or i in low])
tree |= (colsx < 700) & (rows >= 430) & (rows < 760) & (lum < 200)
np.save('cloud.npy', cloud); np.save('sky.npy', S); np.save('treesky.npy', np.clip(SKY, 0, 255)); np.save('tree.npy', tree)
np.save('sprites.npy', np.array(sprites))
v = np.where(tree[..., None], M, [255, 0, 255]).astype(np.uint8)[:430, :700]; Image.fromarray(v).save('check_tree.png')
v = np.where(fg[..., None], M, [255, 0, 255]).astype(np.uint8)[560:]; Image.fromarray(v).resize((836, 190)).save('check_grass.png')
print('done')
