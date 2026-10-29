"""Step 2 of the desert test: animates prep.py's layers. python build.py -> index.html (the test page) and desert.js (the scene engine).
   Anchored sway (bases fixed, tips move most, pixel-snapped, 7 fps; each pixel reads from beside itself, so whole rows never slide):
   the ocotillo (the hero: each stem a little out of step), the foreground grass tufts, agaves (barely), flowers and midground clumps (small).
   Clouds drift right and loop behind the saguaro; a farm windmill fan turns on the empty hub; gusts sweep left to right (stronger sway,
   a faster windmill, a little dust along the ground); the mountains' pink alpenglow slowly fades toward shadow and resets; now and then a bird.
   The camp's Amiga look goes over the whole frame."""
import json, base64, io, numpy as np
from PIL import Image
from scipy import ndimage as nd

L = 'layers/'
M = np.asarray(Image.open('master.png').convert('RGB')).astype(np.uint8)
base = np.asarray(Image.open(L + 'base.png').convert('RGB')).astype(np.uint8)
meta = json.load(open(L + 'meta.json')); A = np.load('amp.npz'); klass = A['klass']; lit = A['lit']
H, W = base.shape[:2]; AW, AH = 952, 536
def png(a): b = io.BytesIO(); Image.fromarray(a).save(b, 'PNG', optimize=True); return base64.b64encode(b.getvalue()).decode()
def smooth_fill(val, m, s):                                            # spread a per-pixel value smoothly over the box, so neighbours move together
    w = nd.gaussian_filter(m.astype(np.float32), s); v = nd.gaussian_filter(np.where(m, val, 0).astype(np.float32), s)
    out = v / np.maximum(w, 1e-4); _, (iy, ix) = nd.distance_transform_edt(w < 1e-3, return_indices=True); return np.where(w < 1e-3, out[iy, ix], out)

layers = []
def add_layer(name, m, weight, amp, phase):
    ys, xs = np.where(m); y0, y1, x0, x1 = max(0, ys.min() - 4), min(H, ys.max() + 2), max(0, xs.min() - 12), min(W, xs.max() + 13)
    box = (slice(y0, y1), slice(x0, x1))
    rgba = np.dstack([M[box], np.where(m[box], 255, 0).astype(np.uint8)])
    maps = np.dstack([np.clip(weight[box] * 255, 0, 255), np.clip(amp[box] * 20, 0, 255), np.clip((phase[box] % (2 * np.pi)) / (2 * np.pi) * 255, 0, 255),
                      np.full(rgba.shape[:2], 255)]).astype(np.uint8)
    layers.append({'name': name, 'x': int(x0), 'y': int(y0), 'w': int(x1 - x0), 'h': int(y1 - y0), 'img': png(rgba), 'maps': png(maps)})

rows = np.arange(H)[:, None].astype(np.float32); cols = np.arange(W)[None, :].astype(np.float32)
# ---------- the ocotillo: anchored at its base, every stem a little out of step ----------
oco = klass == 4; bx, by = meta['oco_base']; top = meta['oco_top']
w_oco = np.clip((by - rows) / (by - top), 0, 1) ** 1.3 * np.ones((H, W))
ang = np.arctan2(cols - bx, np.maximum(by - rows, 1)); ph_oco = ang * 7. + np.zeros((H, W))
add_layer('ocotillo', oco, w_oco, np.full((H, W), 9.), ph_oco)
# ---------- the foreground band: tufts sway, agaves barely, flowers a little; all rooted at the bottom of the picture ----------
fg = (klass >= 1) & (klass <= 3)
cm = fg.any(0); topc = np.where(cm, fg.argmax(0), H - 1).astype(np.float32); topc = nd.gaussian_filter1d(nd.minimum_filter1d(topc, 21), 5)
span = np.maximum(40, H - topc)[None, :]; k = np.clip((H - rows) / span, 0, 1); w_fg = k * k * (3 - 2 * k) * k
amp_fg = smooth_fill(np.select([klass == 1, klass == 2, klass == 3], [6., 1., 3.], 0.), fg, 3)
ph_fg = (np.sin(cols * .011) * 1.7 + np.sin(cols * .027 + 1.3) * 1.1 + np.sin(cols * .053 + 4.) * .6) + np.zeros((H, W))
add_layer('fg', fg, w_fg, amp_fg, ph_fg)
# ---------- the midground clumps: small sway, each rooted at its own bottom ----------
mid = klass == 5
root = np.full((H, W), -1, np.int32); run_top = np.zeros((H, W), np.int32)
for y in range(H - 1, -1, -1):
    m = mid[y]; below = root[y + 1] if y + 1 < H else np.full(W, -1)
    root[y] = np.where(m, np.where(below >= 0, below, y), -1)
for y in range(H):
    m = mid[y]; above = run_top[y - 1] if y > 0 else np.zeros(W, np.int32)
    run_top[y] = np.where(m, np.where((y > 0) & mid[y - 1], above, y), 0)
for y in range(H - 2, -1, -1):                                         # the top of each run, carried down it
    run_top[y] = np.where(mid[y] & mid[y + 1], np.minimum(run_top[y], run_top[y + 1]), run_top[y])
w_mid = np.where(mid, (root - rows) / np.maximum(root - run_top + 1, 3), 0); w_mid = smooth_fill(w_mid, mid, 1.2)
add_layer('mid', mid, np.clip(w_mid, 0, 1), np.full((H, W), 2.2), ph_fg * 1.3)

# ---------- the low dry tufts in the open patch: drawn by prep.py, each blade bends from its foot ----------
T = np.asarray(Image.open(L + 'tufts.png').convert('RGBA')); tm = T[..., 3] > 0
if tm.any():
    lab, n = nd.label(nd.binary_dilation(tm, iterations=2)); w_t = np.zeros((H, W), np.float32)
    for i in range(1, n + 1):
        ys, xs = np.where((lab == i) & tm); w_t[ys, xs] = (ys.max() + 1 - ys) / max(6, ys.max() + 1 - ys.min())
    M2 = M.copy(); M2[tm] = T[tm][:, :3]
    Msave = M; M = M2; add_layer('tufts', tm, np.clip(w_t, 0, 1) ** 1.4, np.full((H, W), 3.), ph_fg * .9 + 1.); M = Msave

# ---------- the Pixel Tuner look (camp settings): a fixed 80-colour palette ----------
TUNE = dict(bright=6, contrast=-4, sat=7, temp=-3, shadows=-16, colors=80, dstr=42)
def tune(a):
    t = TUNE; a = a + t['bright'] / 200; a = (a - .5) * (1 + t['contrast'] / 100) + .5
    l = (a * [.299, .587, .114]).sum(-1, keepdims=True); a = l + (a - l) * (1 + t['sat'] / 100)
    a = a + np.array([1, 0, -1]) * t['temp'] / 100 * .12
    l = np.clip((a * [.299, .587, .114]).sum(-1, keepdims=True), 0, 1); a = a * (1 + t['shadows'] / 100 * (1 - l) ** 2)
    return np.clip(a, 0, 1)
small = np.asarray(Image.fromarray(M).resize((AW, AH), Image.BILINEAR)).astype(np.float32) / 255
shadow = np.array(meta['shadow'], np.float32)
dim = base.astype(np.float32).copy(); dim[lit] = dim[lit] * .2 + shadow * .8                       # include the alpenglow's shadow end in the palette
sm2 = np.asarray(Image.fromarray(dim.astype(np.uint8)).resize((AW, AH), Image.BILINEAR)).astype(np.float32) / 255
pal = Image.fromarray((np.concatenate([tune(small), tune(sm2)], 0) * 255 + .5).astype(np.uint8)).quantize(TUNE['colors'], method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
PAL = np.array(pal.getpalette()[:TUNE['colors'] * 3]).reshape(-1, 3).tolist()

clouds = [{**c, 'img': png(np.asarray(Image.open(f'{L}clouds/{i}.png').convert('RGBA')))} for i, c in enumerate(meta['clouds'])]
front = np.asarray(Image.open(L + 'front.png').convert('RGBA')); fy = np.where(front[..., 3].any(1))[0].max() + 1
LIT = np.flatnonzero(lit.ravel()).tolist()
# the sky, for its saturation controls: above the horizon, not the saguaros, windmill or peaks (front.png), not the dark ground below
SY = 430; bb = base[:SY].astype(np.float32); ry = np.arange(SY)[:, None]
skym = (front[:SY, :, 3] == 0) & ((ry < 345) | ((bb[..., 0] > 205) & (bb[..., 1] > 105) & (bb[..., 0] > bb[..., 2] + 60)))   # and the glow showing between the low ranges
skym &= ~nd.binary_dilation(front[:SY, :, 3] > 0, iterations=1)
blue = np.clip((bb[..., 2] - bb[..., 0] + 30) / 90, 0, 1)                  # how blue (upper sky) vs orange (lower sky) each pixel is
blue = nd.gaussian_filter(blue, 6)                                     # blended smoothly where they meet
skypng = np.dstack([np.where(skym, 255, 0), (blue * 255).round(), np.zeros((SY, W)), np.full((SY, W), 255)]).astype(np.uint8)

engine = r"""/* The desert: a pixel-art sunset desert. Made by prototypes/desert/build.py from master.png and clean.png.
   DesertScene.start(canvas, active) draws into a 952x536 canvas at 7 fps while active() is true. */
window.DesertScene={start(v,active=()=>true){const API={ready:false};
const W=@W@,H=@H@,AW=@AW@,AH=@AH@,PAL=@PAL@,TUNE=@TUNE@,LAYERS=@LAYERS@,CLOUDS=@CLOUDS@,LIT=@LIT@,SHADOW=@SHADOW@,FRONT_H=@FRONTH@;
const vg=v.getContext('2d');
const work=document.createElement('canvas');work.width=W;work.height=H;const g=work.getContext('2d');g.imageSmoothingEnabled=false;
const small=document.createElement('canvas');small.width=AW;small.height=AH;const sg=small.getContext('2d',{willReadFrequently:true});sg.imageSmoothingEnabled=true;sg.imageSmoothingQuality='high';
const glow=document.createElement('canvas');glow.width=AW;glow.height=AH;const gg=glow.getContext('2d');
const load=s=>new Promise(r=>{const i=new Image();i.onload=()=>r(i);i.src='data:image/png;base64,'+s});
const hash=n=>{const s=Math.sin(n*127.1)*43758.5453;return s-Math.floor(s)};
const px=(c,x,y,col)=>{c.fillStyle=col;c.fillRect(Math.round(x/2)*2,Math.round(y/2)*2,2,2)};   // one art pixel, on the grid
const rd=(im,w,h)=>{const c=document.createElement('canvas');c.width=w;c.height=h;const x=c.getContext('2d',{willReadFrequently:true});x.drawImage(im,0,0);return x.getImageData(0,0,w,h)};

/* ---------- the camp's look: tune, 80 fixed colours, a Bayer 4x4 dither locked to the screen, glow and vignette ---------- */
function tune(r,g,b){const t=TUNE;r+=t.bright/200;g+=t.bright/200;b+=t.bright/200;const k=1+t.contrast/100;r=(r-.5)*k+.5;g=(g-.5)*k+.5;b=(b-.5)*k+.5;
  let l=r*.299+g*.587+b*.114;const s=1+t.sat/100;r=l+(r-l)*s;g=l+(g-l)*s;b=l+(b-l)*s;r+=t.temp/100*.12;b-=t.temp/100*.12;
  l=Math.min(1,Math.max(0,r*.299+g*.587+b*.114));const sh=1+t.shadows/100*(1-l)*(1-l);return [r*sh,g*sh,b*sh]}
const LUT=new Uint8Array(64*64*64*3);
for(let i=0;i<64;i++)for(let j=0;j<64;j++)for(let k=0;k<64;k++){const [r,g2,b]=tune((i+.5)/64,(j+.5)/64,(k+.5)/64);let best=0,bd=1e9;
  for(let p=0;p<PAL.length;p++){const dr=r*255-PAL[p][0],dg=g2*255-PAL[p][1],db=b*255-PAL[p][2],d=dr*dr*.3+dg*dg*.59+db*db*.11;if(d<bd){bd=d;best=p}}
  const o=((i*64+j)*64+k)*3;LUT[o]=PAL[best][0];LUT[o+1]=PAL[best][1];LUT[o+2]=PAL[best][2]}
const BAYER=[0,8,2,10,12,4,14,6,3,11,1,9,15,7,13,5],DSTR=TUNE.dstr/100*36;let lookOn=true;
function finish(){sg.drawImage(work,0,0,AW,AH);const im=sg.getImageData(0,0,AW,AH),d=im.data;
  if(lookOn){for(let y=0;y<AH;y++)for(let x=0;x<AW;x++){const o=(y*AW+x)*4,dt=(BAYER[(y&3)*4+(x&3)]/16-.47)*DSTR;
      const r=Math.min(63,Math.max(0,(d[o]+dt)>>2)),g2=Math.min(63,Math.max(0,(d[o+1]+dt)>>2)),b=Math.min(63,Math.max(0,(d[o+2]+dt)>>2)),q=((r*64+g2)*64+b)*3;
      d[o]=LUT[q];d[o+1]=LUT[q+1];d[o+2]=LUT[q+2]}}
  vg.putImageData(im,0,0);
  if(lookOn){gg.clearRect(0,0,AW,AH);gg.filter='blur(1.6px)';gg.drawImage(v,0,0);gg.filter='none';
    vg.save();vg.globalCompositeOperation='screen';vg.globalAlpha=.4;vg.drawImage(glow,0,0);vg.restore();
    const R=Math.hypot(AW*.6,AH*.55),vgr=vg.createRadialGradient(AW*.5,AH*.48,R*.4,AW*.5,AH*.48,R);vgr.addColorStop(0,'rgba(0,0,0,0)');vgr.addColorStop(1,'rgba(0,0,0,.8)');
    vg.fillStyle=vgr;vg.fillRect(0,0,AW,AH)}}

/* no gusts (tried, removed): the wind is the gentle sway alone */

/* ---------- anchored sway: each pixel reads from beside itself, by its own weight (0 at the root) and amount ---------- */
const SNAP=2,FPS=7;
async function prepLayer(Lr){const im=rd(await load(Lr.img),Lr.w,Lr.h),mp=rd(await load(Lr.maps),Lr.w,Lr.h),n=Lr.w*Lr.h,wt=new Float32Array(n),am=new Float32Array(n),ph=new Float32Array(n);
  for(let i=0;i<n;i++){wt[i]=mp.data[i*4]/255;am[i]=mp.data[i*4+1]/20;ph[i]=mp.data[i*4+2]/255*6.2832}
  const cv=document.createElement('canvas');cv.width=Lr.w;cv.height=Lr.h;return {...Lr,src:im.data,wt,am,ph,out:new ImageData(Lr.w,Lr.h),cv,cx:cv.getContext('2d')}}
function sway(Lr,t){const O=Lr.out.data,S=Lr.src,w=Lr.w,h=Lr.h;O.fill(0);
  const hero=Lr.name==='ocotillo',sp=hero?1.05:1.25;
  for(let y=0;y<h;y++){const r=y*w;for(let x=0;x<w;x++){const i=r+x,wt=Lr.wt[i];if(wt<=0)continue;
      const wave=Math.sin(t*sp+Lr.ph[i])*.8+Math.sin(t*sp*1.7+Lr.ph[i]*1.6)*.2;
      const d=Math.round(Lr.am[i]*wt*wave/SNAP)*SNAP,sx=x-d;
      if(sx<0||sx>=w)continue;const si=(r+sx)*4;if(S[si+3]===0)continue;const o=i*4;O[o]=S[si];O[o+1]=S[si+1];O[o+2]=S[si+2];O[o+3]=255}}
  Lr.cx.putImageData(Lr.out,0,0);g.drawImage(Lr.cv,Lr.x,Lr.y)}

/* ---------- the windmill: a classic farm fan of 14 narrow blades on the empty hub, turning in pixel-snapped steps ---------- */
const HUB=[1593,338],RF=21,RI=5;let fanA=0,lastF=null;
function fan(t){if(lastF===null)lastF=t;const dt=Math.min(.5,Math.max(0,t-lastF));lastF=t;fanA+=dt*.5;
  const step=2*Math.PI/14/3,a0=Math.round(fanA/step)*step;   // snapped: a third of a blade per step
  for(let b=0;b<14;b++){const a=a0+b*2*Math.PI/14,ca=Math.cos(a),sa=Math.sin(a);
    for(let r=RI;r<=RF;r+=1.5)px(g,HUB[0]+ca*r*.48,HUB[1]+sa*r,'#1f1c3c')}   // the fan seen a little from the side
  for(let k=0;k<28;k++){const a=k/28*2*Math.PI;px(g,HUB[0]+Math.cos(a)*RF*.48,HUB[1]+Math.sin(a)*RF,'#2a2550')}
  px(g,HUB[0],HUB[1],'#141228')}

/* ---------- a tumbleweed: now and then one rolls across the open patch (the TEST button sends one at once) ---------- */
const TW=[];{let tt=150;for(let i=0;i<60;i++){TW.push(tt);tt+=180+hash(i*4.4)*150}}   // about every 3-5 minutes
let twForced=null;API.tumbleweed=()=>{twForced=curT};let curT=0;
const TWP=(()=>{const P=[],seen=new Set(),add=(x,y)=>{const k=Math.round(x)+','+Math.round(y);if(!seen.has(k)){seen.add(k);P.push([x,y])}};   // a loose tangle of twigs in a ball
  for(let k=0;k<20;k++){const a0=hash(k*3.3)*6.28,a1=a0+1.4+hash(k*7.1)*2.6,rr=3+hash(k*2.2)*8;for(let a=a0;a<a1;a+=.12)add(Math.cos(a)*rr*(1+.3*Math.sin(a*3+k)),Math.sin(a)*rr*.9)}
  for(let a=0;a<6.28;a+=.14)add(Math.cos(a)*11,Math.sin(a)*10);return P})();
function tumbleweed(t){let s0=null;for(const s of TW){if(s>t)break;s0=s}
  const start=twForced!==null?twForced:s0;if(start===null)return;const a=t-start;if(a<0||a>9){if(twForced!==null&&a>9)twForced=null;return}
  const x=380+a*(980/9),hop=Math.abs(Math.sin(a*3.4))*(10-a*.6),y=742+(x-380)*.012-Math.max(0,hop),rot=a*3.1;   // rolling left to right, bouncing lower as it goes
  const c=Math.cos(rot),s=Math.sin(rot);g.globalAlpha=.32;for(let k=-12;k<=12;k+=2)px(g,x+k*1.8,744+(x-380)*.012+2,'#5a2f22');g.globalAlpha=1;   // its shadow on the sand
  for(let k=0;k<TWP.length;k++){const [p,q]=TWP[k];px(g,x+(p*c-q*s)*2,y-20+(p*s+q*c)*2,k%6===0?'#c99460':k%2?'#4e2a1a':'#6e3f24')}}

/* ---------- now and then a bird ---------- */
const BIRDS=[];{let tt=20;for(let i=0;i<200;i++){BIRDS.push(tt);tt+=40+hash(i*5.1)*40}}
const BIRD={up:[[-2,-1],[2,-1],[-1,0],[1,0],[0,0]],mid:[[-2,0],[-1,0],[0,0],[1,0],[2,0]],down:[[-2,1],[2,1],[-1,0],[1,0],[0,0]]},FLAP=['up','mid','down','mid'];
function bird(t){for(let i=0;i<BIRDS.length;i++){const s=BIRDS[i];if(s>t)break;const a=t-s;if(a>20)continue;const f=Math.floor(t*7),dir=hash(i)>.5?1:-1;
  const x=dir>0?-30+a*(W+60)/20:W+30-a*(W+60)/20,y=140+hash(i*3)*120+Math.sin(a*.8)*8,glide=Math.sin(a*1.3)>.3;
  for(const [p,q] of BIRD[glide?'mid':FLAP[f%4]])px(g,x+p*2,y+q*2,'#2a1f2c')}}

Promise.all([load('@BASE@'),load('@FRONT@'),load('@SKY@'),...CLOUDS.map(c=>load(c.img))]).then(async([bi,fi,ski,...ci])=>{
  const BASE=rd(bi,W,H),ORIG=BASE.data.slice(),LY=[];
  /* sky saturation: blue (upper sky, also a touch darker for dusk), orange (lower sky and the glow), and the clouds */
  const SY=@SY@,SK=rd(ski,W,SY).data,SKI=[],SKB=[];for(let i=0;i<W*SY;i++)if(SK[i*4]>127){SKI.push(i);SKB.push(SK[i*4+1]/255)}
  const desat=(r,g,b,s,dk)=>{const l=r*.299+g*.587+b*.114;return [(l+(r-l)*(1-s))*(1-dk),(l+(g-l)*(1-s))*(1-dk),(l+(b-l)*(1-s))*(1-dk)]};
  const CLD=ci.map((im,i)=>{const d=rd(im,CLOUDS[i].w,CLOUDS[i].h),c=document.createElement('canvas');c.width=d.width;c.height=d.height;return {src:d.data.slice(),d,c,x:c.getContext('2d')}});
  API.sky=({blue=30,orange=25,cloud=25}={})=>{const sb=blue/100,so=orange/100,dk=blue/100*.2;   // 30% blue also darkens it about 6%
    for(let q=0;q<SKI.length;q++){const i=SKI[q],w=SKB[q],p=i*4,[r,g,b]=desat(ORIG[p],ORIG[p+1],ORIG[p+2],sb*w+so*(1-w),dk*w);BASE.data[p]=r;BASE.data[p+1]=g;BASE.data[p+2]=b}
    // a cloud's sky-blue edge pixels get the sky's treatment, its warm body the cloud slider's
    for(const c of CLD){const S=c.src,D=c.d.data;for(let p=0;p<S.length;p+=4){const w=Math.min(1,Math.max(0,(S[p+2]-S[p]+30)/90)),[r,g,b]=desat(S[p],S[p+1],S[p+2],sb*w+cloud/100*(1-w),dk*w);D[p]=r;D[p+1]=g;D[p+2]=b;D[p+3]=S[p+3]}c.x.putImageData(c.d,0,0)}
    for(let q=0;q<SKI.length;q++){const p=SKI[q]*4;ORIG2[p]=BASE.data[p];ORIG2[p+1]=BASE.data[p+1];ORIG2[p+2]=BASE.data[p+2]}last=-1};
  const ORIG2=ORIG;for(const Lr of LAYERS)LY.push(await prepLayer(Lr));
  const cs=CLOUDS.map((c,i)=>({...c,im:CLD[i].c,fx:c.x,v:5+7*(c.w/900)}));   // a cloud takes about 3-5 minutes to cross
  let playing=true,t0=performance.now(),last=-1;
  function glowAt(t){const P=210,a=t%P;return a<185?.82*(k=>k*k*(3-2*k))(a/185):.82*(1-(a-185)/25)}   // the pink fades toward shadow, then comes back
  function frame(now){requestAnimationFrame(frame);const f=Math.floor((now-t0)/1000*FPS);if(f===last||!playing||!active())return;last=f;const t=f/FPS;
    const D=BASE.data,k=glowAt(t);for(let q=0;q<LIT.length;q++){const p=LIT[q]*4;D[p]=ORIG[p]+(SHADOW[0]-ORIG[p])*k;D[p+1]=ORIG[p+1]+(SHADOW[1]-ORIG[p+1])*k;D[p+2]=ORIG[p+2]+(SHADOW[2]-ORIG[p+2])*k}
    g.putImageData(BASE,0,0);
    for(const c of cs){const x=((c.fx+t*c.v+c.w)%(W+c.w))-c.w;g.drawImage(c.im,Math.round(x/2)*2,c.y)}   // drifting right, looping round
    bird(t);g.drawImage(fi,0,0);fan(t);
    for(const Lr of LY)sway(Lr,t);
    tumbleweed(t);curT=t;finish()}
  API.sky();requestAnimationFrame(frame);
  API.t=t=>{t0=performance.now()-t*1000;last=-1;lastF=null;twForced=null};API.pause=on=>{playing=!on;last=-1};API.look=on=>{lookOn=on;last=-1};API.ready=true;
});
return API}};
"""
vals = {'@W@': W, '@H@': H, '@AW@': AW, '@AH@': AH, '@PAL@': json.dumps(PAL), '@TUNE@': json.dumps(TUNE),
        '@LAYERS@': json.dumps(layers), '@CLOUDS@': json.dumps(clouds), '@LIT@': json.dumps(LIT), '@SHADOW@': json.dumps(meta['shadow']), '@FRONTH@': int(fy),
        '@BASE@': png(base), '@SKY@': png(skypng), '@SY@': SY, '@FRONT@': png(front)}
for k_, val in vals.items(): engine = engine.replace(k_, str(val))
shell = r"""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Desert test</title>
<style>
:root{--page:#1b1d22;--ink:#e8e4da}
html,body{margin:0;height:100%;background:var(--page);color:var(--ink);font:13px/1.4 system-ui,sans-serif}
.wrap{display:grid;place-items:center;min-height:100%;padding:16px;box-sizing:border-box}
canvas{display:block;image-rendering:pixelated;image-rendering:crisp-edges}
.bar{margin-top:10px;display:flex;gap:8px;align-items:center;flex-wrap:wrap;justify-content:center}
label{display:inline-flex;align-items:center;gap:8px}label b{font-weight:600;min-width:3.2em;font-variant-numeric:tabular-nums}input[type=range]{width:150px;accent-color:#e8a060}
button{font:inherit;color:var(--ink);background:#2c2f36;border:1px solid #444a55;border-radius:8px;padding:6px 10px;cursor:pointer}
</style></head><body><div class="wrap"><div>
<canvas id="v" width="952" height="536" aria-label="Pixel-art desert at sunset: saguaros, an ocotillo, a windmill, mountains"></canvas>
<div class="bar"><button id="play" type="button">Pause</button><button id="look" type="button">Amiga look: on</button><button id="tw" type="button">TEST: tumbleweed</button><span id="info">7 fps</span></div>
<div class="bar sl"><label>Blue sky <input type="range" id="sb" min="0" max="80" value="30"><b id="sbv">30%</b></label>
<label>Orange sky <input type="range" id="so" min="0" max="80" value="25"><b id="sov">25%</b></label>
<label>Clouds <input type="range" id="sc" min="0" max="80" value="25"><b id="scv">25%</b></label></div>
</div></div>
<script>
@ENGINE@
const v=document.getElementById('v'),S=DesertScene.start(v);
function fit(){const AW=952,AH=536,dpr=devicePixelRatio||1,avail=Math.min(innerWidth-32,(innerHeight-70)*AW/AH)*dpr,n=Math.max(1,Math.floor(avail/AW));
  const css=AW*n/dpr<=innerWidth-16?AW*n/dpr:(innerWidth-32);v.style.width=css+'px';v.style.height=(css*AH/AW)+'px'}
addEventListener('resize',fit);fit();
let paused=false,look=true;
document.getElementById('play').onclick=e=>{paused=!paused;S.pause(paused);e.target.textContent=paused?'Play':'Pause'};
document.getElementById('look').onclick=e=>{look=!look;S.look(look);e.target.textContent='Amiga look: '+(look?'on':'off')};
const sky=()=>{const g=id=>+document.getElementById(id).value;for(const id of ['sb','so','sc'])document.getElementById(id+'v').textContent=g(id)+'% less';
  S.sky&&S.sky({blue:g('sb'),orange:g('so'),cloud:g('sc')})};for(const id of ['sb','so','sc'])document.getElementById(id).oninput=sky;setTimeout(sky,0);
document.getElementById('tw').onclick=()=>S.tumbleweed();window.__t=t=>S.t(t);window.__tw=()=>S.tumbleweed();
</script></body></html>"""
open('desert.js', 'w').write(engine); open('index.html', 'w').write(shell.replace('@ENGINE@', engine)); print('index.html', len(engine))
