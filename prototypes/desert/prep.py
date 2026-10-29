"""Step 1 of the desert test: prepare the layers from master.png and clean.png (run in this folder: python prep.py).
   The clean picture already lines up with the master pixel for pixel, so it only needs its colours matched.
   Writes layers/*.png (committed) and amp.npy (git-ignored):
     base.png      the still picture: the master, with the clean background (colour-matched to the master's shadow tones) behind
                   everything that moves, and an in-painted ground behind the midground clumps (the clean picture still has those)
     clouds/N.png  each cloud, cut from the master                  front.png  the saguaro, windmill and peaks, drawn over the clouds
     ocotillo.png  the ocotillo                                      fg.png     the foreground band: grass tufts, agaves and flowers
     mid.png       the midground flower clumps and bunchgrass        rocks: the master's dark rocks stay in base.png, still
   amp.npz holds each moving pixel's class (for how much it sways) and its anchor."""
import os, json, numpy as np
from PIL import Image
from scipy import ndimage as nd

M = np.asarray(Image.open('master.png').convert('RGB')).astype(np.float32)
C = np.asarray(Image.open('clean.png').convert('RGB')).astype(np.float32)
H, W = M.shape[:2]; rows = np.arange(H)[:, None]; cols = np.arange(W)[None, :]
lum = lambda a: a @ np.array([.299, .587, .114], np.float32)
Ml, Cl = lum(M), lum(C); r, g, b = M[..., 0], M[..., 1], M[..., 2]
Cs = np.stack([nd.gaussian_filter(C[..., c], 1.2) for c in range(3)], -1)
d = np.sqrt(((M - Cs) ** 2).sum(-1))                                   # how much the master differs from the clean picture
os.makedirs('layers/clouds', exist_ok=True); os.makedirs('shots', exist_ok=True)
def keep_big(m, n): l, k = nd.label(m); s = nd.sum(m, l, range(k + 1)); return np.isin(l, [i for i in range(1, k + 1) if s[i] >= n])

# ---------- a smooth model of the sky, from the clean picture (which has no clouds) ----------
skyL = np.median(Cl[:, 300:1500], 1)                                   # the sky's brightness, row by row
rc, gc, bc = C[..., 0], C[..., 1], C[..., 2]
looks_sky = (rows < 360) & (Cl > skyL[:, None] - 22) & ~((rows >= 280) & ~((rc > gc + 25) & (gc > bc - 8)))
SKY = np.empty_like(C)
for c in range(3):
    w = nd.gaussian_filter(looks_sky.astype(np.float32), 12); v = nd.gaussian_filter(np.where(looks_sky, C[..., c], 0), 12)
    w2 = nd.gaussian_filter(looks_sky.astype(np.float32), 40); v2 = nd.gaussian_filter(np.where(looks_sky, C[..., c], 0), 40)
    SKY[..., c] = np.where(w > .05, v / np.maximum(w, 1e-4), v2 / np.maximum(w2, 1e-4))

# ---------- in front of the clouds: everything in the clean picture that isn't sky (the saguaros with their lit edges, the windmill, the peaks) ----------
mtn_lit = (rows > 270) & (rows < 480) & (r > 200) & (g < r * .48) & (b > 60)            # the pink-lit faces (a touch pinker than the sky)
front = (rows < 360) & (np.sqrt(((C - SKY) ** 2).sum(-1)) > 20)
front = nd.binary_closing(front, iterations=1); front = keep_big(front, 60)
front = nd.binary_dilation(front, iterations=1) & (rows < 360)          # a pixel of margin, so no cloud colour shows at an edge

# ---------- clouds: bright shapes in the master's sky that the clean sky lacks, never on anything in front ----------
cloud = (d > 26) & (rows < 325) & (Ml > Cl + 6) & ~front
cloud = nd.binary_closing(cloud, iterations=2); cloud = nd.binary_fill_holes(cloud) & ~front
cloud |= nd.binary_dilation(cloud, iterations=2) & (d > 12) & (rows < 330) & ~front   # their soft edge pixels
cloud = keep_big(cloud, 120)
# ---------- the ocotillo: the master's thin stems the clean picture doesn't have ----------
oco = (d > 30) & (cols > 900) & (cols < 1160) & (rows > 390) & (rows < 665)
oco = nd.binary_closing(oco, iterations=1); oco |= nd.binary_dilation(oco, iterations=1) & (d > 16) & (cols > 900) & (cols < 1160) & (rows > 390) & (rows < 665)
oco = keep_big(oco, 400)
oy, ox = np.where(oco); OCO_BASE = (int(np.median(ox[oy > oy.max() - 12])), int(oy.max())); OCO_TOP = int(oy.min())

# ---------- the foreground band: grass tufts, agaves and flowers (the clean picture lacks them); its dark rocks stay still ----------
FY0 = 690
# the clean picture's lighter foreground band, brought to the master's tones locally (ignoring what differs), then compared again
Cm = C.copy(); ign = np.zeros((H, W), bool)
for it in range(3):
    ok_ = ~ign
    for c in range(3):
        w = ok_.astype(np.float32); s_ = 14
        mm = nd.gaussian_filter(np.where(ok_, M[..., c], 0), s_) / np.maximum(nd.gaussian_filter(w, s_), 1e-3)
        cc = nd.gaussian_filter(np.where(ok_, C[..., c], 0), s_) / np.maximum(nd.gaussian_filter(w, s_), 1e-3)
        Cm[..., c] = C[..., c] - cc + mm
    dm = np.sqrt(((M - np.stack([nd.gaussian_filter(Cm[..., c], 1.) for c in range(3)], -1)) ** 2).sum(-1))
    ign = nd.binary_dilation(dm > 30, iterations=2)
fgm = (dm > 30) & (rows > FY0)
fgm = nd.binary_closing(fgm, iterations=1)
lab, n = nd.label(fgm); sz = nd.sum(fgm, lab, range(n + 1)); touch = set(np.unique(lab[H - 3:, :]).tolist())
fgm = np.isin(lab, [i for i in range(1, n + 1) if i in touch or sz[i] > 120])
fgm |= nd.binary_dilation(fgm, iterations=1) & (dm > 16) & (rows > FY0)      # their soft lit edges
rockpx = (Cl < 70) & (rows > 740) & ~fgm                                      # the rocks are in both pictures: they stay in the still layer
flower = fgm & ((((r > 150) & (b > g + 10) & (g < r * .55))) | ((r > 200) & (b < 40)) | ((b > r) & (b > 130)) | ((r > 200) & (g > 165) & (b < 120)))
flower = nd.binary_dilation(flower, iterations=1) & fgm
agave = fgm & (g > r + 2) & ~flower                                  # teal rosettes: barely move                    # broad teal rosettes: barely move
klass = np.zeros((H, W), np.uint8)                                     # 1 grass tuft, 2 agave, 3 flower, 4 ocotillo, 5 midground
klass[fgm] = 1; klass[agave] = 2; klass[flower & fgm] = 3; klass[oco] = 4

# ---------- the midground: flower clumps and bunchgrass (in both pictures, so ground is painted in behind them) ----------
band = (rows > 540) & (rows < 748) & ~oco & (klass == 0)
straw = band & (r > 140) & (g > 80) & (b < 50) & (r > g + 40)                       # golden bunchgrass (the sand has more blue in it)
bloom = band & (((r > 150) & (b > g + 10) & (g < r * .55)) | ((r > 200) & (g > 165) & (b < 120)) | ((b > r) & (b > 140)))
mid = nd.binary_dilation(straw | bloom, iterations=1) & band & (Ml > 50) & ((M - M.mean(-1, keepdims=True)).std(-1) > 18)
cact = (g > r - 5) & (g > b) & (Ml < 110) & band                       # keep cactus pads (and the flowers sitting on them) still
mid &= ~nd.binary_dilation(keep_big(nd.binary_opening(cact, iterations=2), 300), iterations=2)
mid = keep_big(mid, 6)
klass[mid] = 5

# the foreground flower clumps whole: any flower-coloured pixel the master has there (and the clean picture lacks) sways with the clump
for x0, y0, x1, y1 in ((170, 690, 420, 830), (1130, 720, 1420, 840)):
    box = np.zeros((H, W), bool); box[y0:y1, x0:x1] = True
    fl = box & (d > 20) & ((((r > 140) & (b > g + 15) & (g < r * .5))) | ((r > 190) & (g > 50) & (g < 160) & (b < 70)) | ((b > r * .7) & (b > 100) & (g < b * .78)))
    fl = nd.binary_dilation(fl, iterations=1) & box & (d > 14)
    klass[fl & (klass != 4)] = 3
moving = klass > 0
# ---------- the still picture ----------
match = ~nd.binary_dilation(moving | cloud, iterations=3)
Cm = C.copy()
for c in range(3):                                                     # the clean picture in the master's own (darker) tones, locally
    w = match.astype(np.float32); s = 30
    mm = nd.gaussian_filter(np.where(match, M[..., c], 0), s) / np.maximum(nd.gaussian_filter(w, s), 1e-3)
    cc = nd.gaussian_filter(np.where(match, C[..., c], 0), s) / np.maximum(nd.gaussian_filter(w, s), 1e-3)
    Cm[..., c] = C[..., c] - cc + mm
base = M.copy()
behind = (moving & (klass != 5)) | cloud
base[behind] = np.clip(Cm[behind], 0, 255)
# the open sky comes entirely from the clean sky (in the master's colours), so no faint cloud edge is left behind when a cloud drifts on
okS = (rows < 340) & ~nd.binary_dilation(cloud, iterations=10) & ~front
S = C.copy()
for c in range(3):
    w = okS.astype(np.float32); s_ = 40
    mm = nd.gaussian_filter(np.where(okS, M[..., c], 0), s_) / np.maximum(nd.gaussian_filter(w, s_), 1e-3)
    cc = nd.gaussian_filter(np.where(okS, C[..., c], 0), s_) / np.maximum(nd.gaussian_filter(w, s_), 1e-3)
    S[..., c] = C[..., c] - cc + mm
skyzone = (rows < 335) & ~nd.binary_dilation(front, iterations=1) & ~((rows >= 280) & (Cl < skyL[:, None] - 12))
base[skyzone] = np.clip(S[skyzone], 0, 255)
# behind the midground clumps: the master's own ground, pulled in from just outside each clump and softened
hole = nd.binary_dilation(klass == 5, iterations=1)
_, (iy, ix) = nd.distance_transform_edt(hole, return_indices=True)
fill = M[iy, ix]; fill = np.stack([nd.gaussian_filter(fill[..., c], 1.) for c in range(3)], -1)
base[hole] = fill[hole]
# behind the foreground band, rocks carry on in their own colour where a tuft covered them
rk_hidden = nd.binary_fill_holes(nd.binary_closing(rockpx, iterations=4)) & behind & (rows > FY0)
if rk_hidden.any():
    _, (iy, ix) = nd.distance_transform_edt(~rockpx, return_indices=True); base[rk_hidden] = M[iy, ix][rk_hidden]

# ---------- the open sandy patch: pebbles, darker sand, a faint dry wash, and a few low dry tufts (pixel-snapped to 2 px) ----------
rng = np.random.default_rng(11)
PCX, PCY, PRX, PRY = 840, 732, 420, 74                                # the patch, as an ellipse
sandy = (base[..., 0] > 135) & (base[..., 1] > 65) & (base[..., 1] < 125) & (base[..., 2] > 45) & (base[..., 2] < 100) & ~moving
sandL = np.stack([nd.gaussian_filter(base[..., c], 6) for c in range(3)], -1)   # the local sand colour
def ell(x, y): return ((x - PCX) / PRX) ** 2 + ((y - PCY) / PRY) ** 2
def put(x, y, col, w=2, h=2):
    x, y = int(x) // 2 * 2, int(y) // 2 * 2
    if 0 <= x < W - w and 0 <= y < H - h and sandy[y:y + h, x:x + w].all(): base[y:y + h, x:x + w] = col
# a dry wash: a faint shallow channel curving across (darker floor, a lit lip on its far side)
for tt in np.linspace(0, 1, 900):
    x = 470 + tt * 760; y = 748 - 34 * np.sin(tt * 3.0 + .4) + 10 * np.sin(tt * 9.)
    wdt = 8 + 5 * np.sin(tt * 5.1)
    for k in range(-int(wdt), int(wdt) + 1, 2):
        if rng.random() < .55: put(x, y + k * .5, sandL[int(y), int(x)] * (.88 + .04 * rng.random()))
    if rng.random() < .35: put(x, y - wdt * .5 - 2, np.minimum(sandL[int(y), int(x)] * 1.1, 255))
# darker patches of sand (2 px blocks, loose noise blobs)
for _ in range(16):
    cx, cy = PCX + rng.uniform(-.9, .9) * PRX, PCY + rng.uniform(-.8, .8) * PRY; rx, ry = rng.uniform(18, 46), rng.uniform(5, 11)
    for y in range(int(cy - ry), int(cy + ry), 2):
        for x in range(int(cx - rx), int(cx + rx), 2):
            e = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
            if e < 1 and rng.random() > e * .9: put(x, y, sandL[y, x] * .92)
# pebbles: denser toward the edges of the patch, a dark body and a lit top
for _ in range(260):
    x, y = PCX + rng.uniform(-1, 1) * PRX, PCY + rng.uniform(-1, 1) * PRY; e = ell(x, y)
    if e > 1 or rng.random() > .25 + .75 * e: continue
    sc = sandL[int(y), int(x)]; dark = sc * np.array([.55, .55, .72]); lit = np.minimum(sc * 1.18, 255)
    if rng.random() < .7: put(x, y, dark)                                 # a single pixel
    else: put(x, y, dark, 4, 2); put(x, y - 2, lit)                        # a small stone
# low dry tufts near the edges of the patch: a separate layer, so they sway
tuft = np.zeros((H, W, 4), np.uint8); STRAW = np.array([[118, 64, 26], [166, 96, 32], [205, 138, 62], [232, 176, 96]], np.float32)
tufts = 0
while tufts < 11:
    a_ = rng.uniform(0, 2 * np.pi); e = rng.uniform(.72, .98); x0, y0 = PCX + np.cos(a_) * PRX * e, PCY + np.sin(a_) * PRY * e
    x0, y0 = int(x0) // 2 * 2, int(y0) // 2 * 2
    if not (0 < x0 < W and 0 < y0 < H) or not sandy[y0, x0]: continue
    nb = rng.integers(7, 12)
    for bl in range(nb):
        hgt = rng.uniform(12, 26); lean = (bl - nb / 2) / nb * 1.4 + rng.uniform(-.25, .25)   # fanning out from the foot
        for j in range(0, int(hgt), 2):
            x, y = int(x0 + lean * j) // 2 * 2 + int((bl - nb / 2) * .8) * 2, y0 - j
            if 0 <= x < W - 2 and 0 <= y < H: tuft[y:y + 2, x:x + 2] = np.append(STRAW[min(3, int(j / hgt * 3.99))], 255)
    base[y0:y0 + 2, x0 - 10:x0 + 12] = (sandL[y0, x0] * .78)                 # a little shadow at its foot
    tufts += 1
Image.fromarray(tuft).save('layers/tufts.png')

def rgba(m, box=None):
    a = np.dstack([M.astype(np.uint8), np.where(m, 255, 0).astype(np.uint8)])
    return Image.fromarray(a if box is None else a[box[1]:box[3], box[0]:box[2]])
Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).save('layers/base.png')
rgba(front).save('layers/front.png'); rgba(oco).save('layers/ocotillo.png'); rgba(moving & (klass < 4)).save('layers/fg.png'); rgba(klass == 5).save('layers/mid.png')
lab, n = nd.label(nd.binary_dilation(cloud, iterations=6)); meta = []
for i in range(1, n + 1):
    m = (lab == i) & cloud; ys, xs = np.where(m)
    if len(xs) < 150: continue
    box = (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1); rgba(m, box).save(f'layers/clouds/{len(meta)}.png')
    meta.append({'x': box[0], 'y': box[1], 'w': box[2] - box[0], 'h': box[3] - box[1], 'px': int(len(xs))})
# mountains' lit band (for the alpenglow) and its shadow colour
mz = (rows > 285) & (rows < 480)
lit = mtn_lit & (rows > 290) & ~cloud & (Cl < skyL[:, None] + 40) & ((rows > 345) | front) & ~((rows < 305) & ~front)   # the pink-lit mountain faces (not the low wisp of cloud)
shade = mz & (b > r + 10) & (b > g + 20)
json.dump({'clouds': meta, 'oco_base': OCO_BASE, 'oco_top': OCO_TOP, 'shadow': np.median(M[shade], 0).round(1).tolist()}, open('layers/meta.json', 'w'))
np.savez('amp.npz', klass=klass, lit=lit)
for k, nm in enumerate(['', 'grass', 'agave', 'flower', 'ocotillo', 'mid']):
    if k: print(nm, int((klass == k).sum()))
print('clouds', len(meta), [c['w'] for c in meta], 'front', int(front.sum()), 'lit mountain', int(lit.sum()), 'ocotillo base', OCO_BASE, 'top', OCO_TOP)
# check pictures
v = (M * .3).astype(np.uint8); col = {1: [255, 200, 0], 2: [0, 220, 160], 3: [255, 60, 200], 4: [255, 90, 40], 5: [120, 160, 255]}
for k, c in col.items(): v[klass == k] = c
v[cloud] = [255, 255, 255]; v[front] = (v[front] * .5 + [80, 0, 120]).astype(np.uint8); v[lit] = (v[lit] * .5 + [120, 60, 0]).astype(np.uint8); v[rockpx] = [90, 30, 30]
Image.fromarray(v).resize((1254, 706)).save('shots/check_layers.png')
Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).resize((1254, 706)).save('shots/check_base.png')
