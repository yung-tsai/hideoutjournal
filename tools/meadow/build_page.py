"""Builds the valley test page (index.html) from prep.py's layers.
   Foreground grass sway, the camp's Amiga look, drifting clouds behind the pine, meadow colour-cycling waves, water,
   gusts (stronger lean, a bright wave, golden seed specks), and rare wildlife (a flock or butterflies), one at a time.
   Run in a working folder outside the repo, after prep.py (needs numpy, scipy, pillow):
     cp assets/meadow/*.png tools/meadow/*.py <folder>; cd <folder>; python prep.py; python build_page.py
   It writes meadow.js (copy it to src/meadow.js, then python3 build.py) and meadow-test.html (the scene on its own page)."""
import json, base64, io, numpy as np
from PIL import Image
from scipy import ndimage as nd


M = np.asarray(Image.open('master.png').convert('RGB')).astype(np.uint8)
BG = np.load('bg.npy').astype(np.uint8); FG = np.load('fg.npy')
cloud = np.load('cloud.npy'); S = np.load('sky.npy'); SKY = np.load('treesky.npy'); tree = np.load('tree.npy'); sprites = np.load('sprites.npy')
H, W = FG.shape; Y0 = 520; AW, AH = 952, 536
def png(a): b = io.BytesIO(); Image.fromarray(a).save(b, 'PNG', optimize=True); return base64.b64encode(b.getvalue()).decode()

# ---------- the still layers ----------
base0 = np.where(FG[..., None], BG, M)                                   # with the clouds, for the palette
base = np.where(nd.binary_dilation(cloud, iterations=2)[..., None], S.astype(np.uint8), base0)
base = np.where((tree & (np.arange(H)[:, None] < 430))[..., None], SKY.astype(np.uint8), base)   # sky behind the pine
clouds = []
for sp in sprites:
    ys, xs = np.where(sp); x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    clouds.append({'x': int(x0), 'y': int(y0), 'w': int(x1 - x0), 'px': int(sp.sum()),
                   'img': np.dstack([M[y0:y1, x0:x1], np.where(sp[y0:y1, x0:x1], 255, 0).astype(np.uint8)])})
ty, tx = np.where(tree); tree_img = np.dstack([M[:ty.max() + 1, :tx.max() + 1], np.where(tree[:ty.max() + 1, :tx.max() + 1], 255, 0).astype(np.uint8)])
fgr = np.dstack([M, np.where(FG, 255, 0).astype(np.uint8)])[Y0:]
cols = FG[Y0:].any(0); top = np.where(cols, FG[Y0:].argmax(0), H - Y0 - 1).astype(np.float32)
top = nd.gaussian_filter1d(nd.minimum_filter1d(top, 25), 6)

# ---------- colour-cycling ramps: meadow, stream, waterfall ----------
B = base.astype(np.float32); r, g, b = B[..., 0], B[..., 1], B[..., 2]; lum = B @ [.299, .587, .114]
rows = np.arange(H)[:, None]; colsx = np.arange(W)[None, :]
masks = {'meadow': (rows >= 590) & (r > g * .92) & (g > b * 1.15) & (r - b > 45) & (lum > 55),
         'stream': (colsx > 330) & (colsx < 540) & (rows > 590) & (rows < 670) & (b > g * 1.02) & (lum > 95),
         'fall': (colsx > 1410) & (colsx < 1480) & (rows > 430) & (rows < 540) & (lum > 110) & (np.abs(r - b) < 45)}
CY = 420; cmap = np.zeros((H - CY, W, 3), np.uint8); ramps = {}
for ch, (k, m) in enumerate(masks.items()):
    K = {'meadow': 20, 'stream': 10, 'fall': 10}[k]
    L = lum[m]; qs = np.quantile(L, np.linspace(0, 1, K + 1)); idx = np.clip(np.searchsorted(qs, L, 'right') - 1, 0, K - 1)
    ramps[k] = [B[m][idx == i].mean(0).round(1).tolist() for i in range(K)]
    cmap[..., ch][m[CY:]] = (idx + 1).astype(np.uint8)

# ---------- the Pixel Tuner look (camp settings): a fixed 80-colour palette ----------
TUNE = dict(bright=6, contrast=-4, sat=7, temp=-3, shadows=-16, colors=80, dstr=42)
def tune(a):
    t = TUNE; a = a + t['bright'] / 200; a = (a - .5) * (1 + t['contrast'] / 100) + .5
    l = (a * [.299, .587, .114]).sum(-1, keepdims=True); a = l + (a - l) * (1 + t['sat'] / 100)
    a = a + np.array([1, 0, -1]) * t['temp'] / 100 * .12
    l = np.clip((a * [.299, .587, .114]).sum(-1, keepdims=True), 0, 1); a = a * (1 + t['shadows'] / 100 * (1 - l) ** 2)
    return np.clip(a, 0, 1)
small = np.asarray(Image.fromarray(base0).resize((AW, AH), Image.BILINEAR)).astype(np.float32) / 255
pal = Image.fromarray((tune(small) * 255 + .5).astype(np.uint8)).quantize(TUNE['colors'], method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
PAL = np.array(pal.getpalette()[:TUNE['colors'] * 3]).reshape(-1, 3).tolist()

big = max(c['px'] for c in clouds)
CL = [{'x': c['x'], 'y': c['y'], 'w': c['w'], 'T': round((180 + 90 * (1 - c['px'] / big)) * 1.1, 1)} for c in clouds]   # 10% slower than before
hidden = max(range(len(clouds)), key=lambda i: clouds[i]['x'] + clouds[i]['w'])

engine = r"""/* The meadow: Hideout's pixel-art golden-hour scene. Made by tools/meadow/build_page.py from assets/meadow/master.png and clean.png.
   MeadowScene.start(canvas, active) draws into a 952x536 canvas at 7 fps while active() is true. */
window.MeadowScene={start(v,active=()=>true){const API={ready:false};
const W=@W@,H=@H@,Y0=@Y0@,AW=@AW@,AH=@AH@,CY=@CY@,TOP=@TOP@,PAL=@PAL@,TUNE=@TUNE@,RAMPS=@RAMPS@,CL=@CL@,HIDDEN=@HIDDEN@;
const vg=v.getContext('2d');
const work=document.createElement('canvas');work.width=W;work.height=H;const g=work.getContext('2d');g.imageSmoothingEnabled=false;
const small=document.createElement('canvas');small.width=AW;small.height=AH;const sg=small.getContext('2d',{willReadFrequently:true});sg.imageSmoothingEnabled=true;sg.imageSmoothingQuality='high';
const glow=document.createElement('canvas');glow.width=AW;glow.height=AH;const gg=glow.getContext('2d');
const load=s=>new Promise(r=>{const i=new Image();i.onload=()=>r(i);i.src='data:image/png;base64,'+s});
const hash=n=>{const s=Math.sin(n*127.1)*43758.5453;return s-Math.floor(s)};
const vn=(x,y)=>{const ix=Math.floor(x),iy=Math.floor(y),fx=x-ix,fy=y-iy,u=fx*fx*(3-2*fx),w=fy*fy*(3-2*fy),h=(a,b)=>hash(a*57.3+b*131.7);
  return (h(ix,iy)*(1-u)+h(ix+1,iy)*u)*(1-w)+(h(ix,iy+1)*(1-u)+h(ix+1,iy+1)*u)*w};

/* ---------- the camp's look: tune, 80 fixed colours, a Bayer 4x4 dither locked to the screen, glow and vignette ---------- */
function tune(r,g,b){const t=TUNE;r+=t.bright/200;g+=t.bright/200;b+=t.bright/200;const k=1+t.contrast/100;r=(r-.5)*k+.5;g=(g-.5)*k+.5;b=(b-.5)*k+.5;
  let l=r*.299+g*.587+b*.114;const s=1+t.sat/100;r=l+(r-l)*s;g=l+(g-l)*s;b=l+(b-l)*s;r+=t.temp/100*.12;b-=t.temp/100*.12;
  l=Math.min(1,Math.max(0,r*.299+g*.587+b*.114));const sh=1+t.shadows/100*(1-l)*(1-l);return [r*sh,g*sh,b*sh]}
const LUT=new Uint8Array(64*64*64*3);
for(let i=0;i<64;i++)for(let j=0;j<64;j++)for(let k=0;k<64;k++){const [r,g2,b]=tune((i+.5)/64,(j+.5)/64,(k+.5)/64);let best=0,bd=1e9;
  for(let p=0;p<PAL.length;p++){const dr=r*255-PAL[p][0],dg=g2*255-PAL[p][1],db=b*255-PAL[p][2],d=dr*dr*.3+dg*dg*.59+db*db*.11;if(d<bd){bd=d;best=p}}
  const o=((i*64+j)*64+k)*3;LUT[o]=PAL[best][0];LUT[o+1]=PAL[best][1];LUT[o+2]=PAL[best][2]}
const BAYER=[0,8,2,10,12,4,14,6,3,11,1,9,15,7,13,5],DSTR=TUNE.dstr/100*36;
let lookOn=true;
function finish(){sg.drawImage(work,0,0,AW,AH);const im=sg.getImageData(0,0,AW,AH),d=im.data;
  if(lookOn){for(let y=0;y<AH;y++)for(let x=0;x<AW;x++){const o=(y*AW+x)*4,dt=(BAYER[(y&3)*4+(x&3)]/16-.47)*DSTR;
      const r=Math.min(63,Math.max(0,(d[o]+dt)>>2)),g2=Math.min(63,Math.max(0,(d[o+1]+dt)>>2)),b=Math.min(63,Math.max(0,(d[o+2]+dt)>>2)),q=((r*64+g2)*64+b)*3;
      d[o]=LUT[q];d[o+1]=LUT[q+1];d[o+2]=LUT[q+2]}}
  vg.putImageData(im,0,0);
  if(lookOn){gg.clearRect(0,0,AW,AH);gg.filter='blur(1.6px)';gg.drawImage(v,0,0);gg.filter='none';
    vg.save();vg.globalCompositeOperation='screen';vg.globalAlpha=.4;vg.drawImage(glow,0,0);vg.restore();
    const R=Math.hypot(AW*.6,AH*.55),vgr=vg.createRadialGradient(AW*.5,AH*.48,R*.4,AW*.5,AH*.48,R);vgr.addColorStop(0,'rgba(0,0,0,0)');vgr.addColorStop(1,'rgba(0,0,0,.8)');
    vg.fillStyle=vgr;vg.fillRect(0,0,AW,AH)}}

/* ---------- gusts: one every 8-15 s, a 2 s rise, a short hold, a 4.5 s settle ---------- */
const GU=[];{let tt=5;for(let i=0;i<2000;i++){GU.push(tt);tt+=8+hash(i*3.7)*7}}
const gustStart=t=>{let s=-1;for(const x of GU){if(x>t)break;s=x}return s};
const gust=t=>{const s=gustStart(t);if(s<0)return 0;const a=t-s;if(a<2){const k=a/2;return k*k*(3-2*k)}if(a<3.5)return 1;if(a<8){const k=1-(a-3.5)/4.5;return k*k*(3-2*k)}return 0};
window.__gust=gust;
const px=(g,x,y,c)=>{g.fillStyle=c;g.fillRect(Math.round(x/2)*2,Math.round(y/2)*2,2,2)};   // one art pixel, on the grid

/* ---------- wildlife: one at a time, 30-60 s of quiet between: flock, butterflies, flock, and round again ---------- */
const LIFE=[];{let tt=8;const order=['flock','flies','flock'];
  for(let i=0;i<300;i++){const type=order[i%3],dur=type==='flock'?24:11;LIFE.push({s:tt,type,dur,i});tt+=dur+30+hash(i*2.9)*30}}
const lifeNow=t=>{for(const e of LIFE){if(e.s>t)return null;if(t<e.s+e.dur)return e}return null};
window.__life=t=>{const e=lifeNow(t);return e?e.type:null};window.__lifeList=LIFE.slice(0,6);
const BIRD={up:[[-2,-1],[2,-1],[-1,0],[1,0],[0,0]],mid:[[-2,0],[-1,0],[0,0],[1,0],[2,0]],down:[[-2,1],[2,1],[-1,0],[1,0],[0,0]]},FLAP=['up','mid','down','mid'];
const shape=(g,S,x,y,c)=>{for(const [a,b] of S)px(g,x+a*2,y+b*2,c)};
function skyLife(g,t){const e=lifeNow(t);if(!e)return;const a=t-e.s,f=Math.floor(t*7);
  if(e.type==='flock'){const n=5+Math.floor(hash(e.i)*3),y0=110+hash(e.i*7)*130;
    for(let b=0;b<n;b++){const side=b%2?1:-1,rank=Math.ceil(b/2),jx=hash(e.i+b*3.1)*10,jy=hash(e.i*2+b)*8;
      const x=-120+a*(W+300)/e.dur-rank*26-jx,y=y0+side*rank*13+jy+Math.sin(a*1.1+b)*3,flap=Math.sin(a*.9+b*1.7)>.1;
      shape(g,BIRD[flap?FLAP[(f+b)%4]:'mid'],x,y,'#1d1a22')}}}
function grassLife(g,t){const e=lifeNow(t);if(!e||e.type!=='flies')return;const a=t-e.s,f=Math.floor(t*7),n=1+(hash(e.i*4)>.5?1:0);
  for(let b=0;b<n;b++){const h=hash(e.i*9+b),x0=300+h*1000+b*60,up=Math.min(1,a/1.5,(e.dur-a)/1.5);
    const x=x0+Math.sin(a*.7+b)*90+a*14,y=860-up*(70+h*40)+Math.sin(a*3.1+b*2)*14+Math.sin(a*7.3+b)*4,open=(f+b)%2===0;
    const c1=b?'#f6efd8':'#f2d27a',c2='#c98a3a';
    if(open){px(g,x-4,y-2,c1);px(g,x+4,y-2,c1);px(g,x-2,y,c1);px(g,x+2,y,c1);px(g,x-4,y,c2);px(g,x+4,y,c2);px(g,x,y,'#3a2c22')}
    else{px(g,x,y-2,c1);px(g,x,y,'#3a2c22');px(g,x-2,y-2,c2)}}}
/* ---------- seeds: in a gust, a few tiny golden specks of fluff drift across with the wind ---------- */
const SEED=['#f3d58a','#e8c070','#fbe6b0'];
function seeds(g,t){const s=gustStart(t);if(s<0)return;const a=t-s;if(a>8)return;
  for(let j=0;j<9;j++){const h=hash(s*13.1+j*7.7),d=h*2.2,age=a-d;if(age<0||age>5.5)continue;
    const x=-30+hash(s+j*1.9)*700+age*(150+h*70),y=420+hash(s*3+j*5)*330+Math.sin(age*1.7+j)*10-age*6;
    if(age<.6&&hash(j+f7(t))>age/.6)continue;if(age>4.6&&hash(j*3+f7(t))<(age-4.6)/.9)continue;   // fade in and out a frame at a time
    px(g,x,y,SEED[j%3]);if(j%4===0)px(g,x+2,y-2,SEED[(j+1)%3])}}
const f7=t=>Math.floor(t*7);

Promise.all([load('@BASE@'),load('@FGR@'),load('@TREE@'),load('@CMAP@'),...[@CLOUDS@].map(load)]).then(([bi,fi,treeI,cmapI,...cloudI])=>{
  const fw=W,fh=H-Y0,tc=document.createElement('canvas');tc.width=fw;tc.height=fh;const tx=tc.getContext('2d');tx.drawImage(fi,0,0);
  const src=tx.getImageData(0,0,fw,fh).data,out=new ImageData(fw,fh),O=out.data;
  const wt=new Float32Array(fw*fh);for(let x=0;x<fw;x++){const t=TOP[x],span=Math.max(40,fh-t);for(let y=0;y<fh;y++){const k=Math.min(1,Math.max(0,(fh-y)/span));wt[y*fw+x]=k*k*(3-2*k)*k}}
  const ph=new Float32Array(fw);for(let x=0;x<fw;x++)ph[x]=Math.sin(x*.011)*1.7+Math.sin(x*.027+1.3)*1.1+Math.sin(x*.053+4.)*.6;
  const AMP=7,SNAP=2,FPS=7,SPEED=1.05;let playing=true,t0=performance.now(),last=-1;   // the sway runs 5% faster than before
  const bc=document.createElement('canvas');bc.width=W;bc.height=H;const bx=bc.getContext('2d',{willReadFrequently:true});bx.drawImage(bi,0,0);const BASE=bx.getImageData(0,0,W,H);
  /* colour cycling: each pixel keeps its place and only steps along the ramp of colours it belongs to */
  const mc=document.createElement('canvas');mc.width=W;mc.height=H-CY;const mx=mc.getContext('2d',{willReadFrequently:true});mx.drawImage(cmapI,0,0);const md=mx.getImageData(0,0,W,H-CY).data;
  const ORIG=BASE.data.slice(),LIST={meadow:[],stream:[],fall:[]},KEYS=['meadow','stream','fall'];
  for(let i=0,n=W*(H-CY);i<n;i++)for(let c=0;c<3;c++){const q=md[i*4+c];if(q)LIST[KEYS[c]].push(i+CY*W,q-1)}
  const DEL={};for(const k of KEYS){const R=RAMPS[k];DEL[k]=R.map((_,i)=>{const row=[];for(let s=-3;s<=3;s++){const j=Math.min(R.length-1,Math.max(0,i+s));row.push([R[j][0]-R[i][0],R[j][1]-R[i][1],R[j][2]-R[i][2]])}return row})}
  const MP=LIST.meadow,mN=MP.length/2,mPh=new Float32Array(mN),mEn=new Float32Array(mN),mSc=new Float32Array(mN);
  for(let k=0;k<mN;k++){const o=MP[k*2],x=o%W,y=(o/W)|0,dz=Math.max(30,y-520);mPh[k]=(x-836)/dz*2.4+260/dz*3.;mEn[k]=.55+.45*vn(x/(dz*1.6),y/40);mSc[k]=Math.max(.35,dz/420)}
  let mPhase=0,lastC=null;
  function cycle(d,t,G){if(lastC===null)lastC=t;const dt=Math.min(1,Math.max(0,t-lastC));lastC=t;mPhase+=dt*.55*(1+.6*G);
    const str=1.6*(1+.9*G),gs=gustStart(t),ga=t-gs,front=gs>=0&&ga<7?-400+(W+800)*ga/6.5:null,fe=front===null?0:Math.sin(Math.PI*Math.min(1,ga/6.5));
    for(let k=0;k<mN;k++){const o=MP[k*2],i=MP[k*2+1],w=Math.sin(mPh[k]-mPhase);let b=w>.25?(w-.25)/.75:0;b=b*b*(3-2*b)*mEn[k];
      let gw=0;if(front!==null){const q=((o%W)-front)/(260*mSc[k]);gw=q*q<9?Math.exp(-q*q)*fe:0}   // the gust's bright sunray band sweeping across
      const s=Math.min(3,Math.round(b*str)+Math.round(3*gw*mEn[k])),D=DEL.meadow[i][s+3],p=o*4;d[p]=ORIG[p]+D[0];d[p+1]=ORIG[p+1]+D[1];d[p+2]=ORIG[p+2]+D[2]}
    const SP=LIST.stream;for(let k=0;k<SP.length;k+=2){const o=SP[k],i=SP[k+1],x=o%W,y=(o/W)|0,h=hash(x*.37+y*1.91);
      const tw=i>=7?Math.round(2.4*Math.max(0,Math.sin(t*(1.3+h*2.2)+h*40)**8)-(Math.sin(t*(.9+h)+h*20)>.6?1:0)):Math.round(.9*Math.sin(x*.21-t*1.6+y*.5));   // glints twinkle
      const D=DEL.stream[i][Math.max(-3,Math.min(3,tw))+3],p=o*4;d[p]=ORIG[p]+D[0];d[p+1]=ORIG[p+1]+D[1];d[p+2]=ORIG[p+2]+D[2]}
    const FP=LIST.fall,PAT=[0,1,2,1,0,-1,-1,0];for(let k=0;k<FP.length;k+=2){const o=FP[k],i=FP[k+1],x=o%W,y=(o/W)|0;
      const s=PAT[(((Math.floor((y+hash(x)*7)/3-t*7))%8)+8)%8];   // stripes running down the fall
      const D=DEL.fall[i][s+3],p=o*4;d[p]=ORIG[p]+D[0];d[p+1]=ORIG[p+1]+D[1];d[p+2]=ORIG[p+2]+D[2]}}
  /* clouds: drift right, come back from behind the pine, 2-3 up, never bunched */
  const ENTRY=160,GAP=140,MAXV=3,cs=CL.map((c,i)=>({...c,img:cloudI[i],fx:c.x,v:(W+c.w)/c.T,on:i!==HIDDEN,wait:0}));let lastT=null;
  function stepSky(dt){const on=cs.filter(c=>c.on).sort((a,b)=>a.fx-b.fx);
    for(let i=0;i<on.length;i++){const c=on[i],ahead=on[i+1];let vv=c.v;
      if(ahead){const gap=ahead.fx-(c.fx+c.w);if(gap<GAP*1.6)vv=Math.min(vv,ahead.v*(gap<GAP?.9:1))}
      c.fx+=vv*dt;if(c.fx>W){c.on=false;c.wait=20+Math.random()*40}}
    const n=cs.filter(c=>c.on).length,lead=Math.min(...cs.filter(c=>c.on).map(c=>c.fx),W);
    for(const c of cs){if(c.on)continue;c.wait-=dt;if(n<MAXV&&lead>ENTRY+GAP*2.2&&(n<2||c.wait<=0)){c.on=true;c.fx=ENTRY-c.w;break}}}
  window.__clouds=()=>cs.map(c=>({x:Math.round(c.fx),on:c.on,w:c.w}));
  function frame(now){requestAnimationFrame(frame);const f=Math.floor((now-t0)/1000*FPS);if(f===last||!playing||!active())return;last=f;const t=f/FPS;
    const G=gust(t),ts=t*SPEED;O.fill(0);
    const sw=(.65+.35*Math.sin(ts*.35))*(1+.5*G);
    const off=new Float32Array(fw);for(let x=0;x<fw;x++)off[x]=AMP*sw*(Math.sin(ts*1.25+ph[x])*.8+Math.sin(ts*2.1+ph[x]*1.7)*.2)+AMP*1.5*G*(.85+.15*Math.sin(ts*1.7+ph[x]));   // in a gust the grass leans with the wind
    for(let y=0;y<fh;y++){const r=y*fw;for(let x=0;x<fw;x++){const d=Math.round(off[x]*wt[r+x]/SNAP)*SNAP,sx=x-d;
      if(sx<0||sx>=fw)continue;const si=(r+sx)*4;if(src[si+3]===0)continue;const o=(r+x)*4;O[o]=src[si];O[o+1]=src[si+1];O[o+2]=src[si+2];O[o+3]=255}}
    cycle(BASE.data,t,G);g.putImageData(BASE,0,0);
    if(lastT===null)lastT=t;let dt=Math.max(0,t-lastT);lastT=t;while(dt>0){const s=Math.min(1,dt);stepSky(s);dt-=s}
    for(const c of cs)if(c.on)g.drawImage(c.img,Math.round(c.fx/2)*2,c.y);
    skyLife(g,t);                 // birds, behind the pine
    g.drawImage(treeI,0,0);       // the pine, above the clouds and the birds
    seeds(g,t);
    tx.putImageData(out,0,0);g.drawImage(tc,0,Y0);
    grassLife(g,t);finish()}
  requestAnimationFrame(frame);
API.t=t=>{t0=performance.now()-t*1000;last=-1;lastT=null;lastC=null};API.pause=on=>{playing=!on;last=-1};API.look=on=>{lookOn=on;last=-1};API.ready=true;
});

return API}};
"""
test = r"""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Meadow test</title>
<style>
:root{--page:#1b1d22;--ink:#e8e4da}
html,body{margin:0;height:100%;background:var(--page);color:var(--ink);font:13px/1.4 system-ui,sans-serif}
.wrap{display:grid;place-items:center;min-height:100%;padding:16px;box-sizing:border-box}
canvas{display:block;image-rendering:pixelated;image-rendering:crisp-edges}
.bar{margin-top:10px;display:flex;gap:8px;align-items:center;flex-wrap:wrap;justify-content:center}
button{font:inherit;color:var(--ink);background:#2c2f36;border:1px solid #444a55;border-radius:8px;padding:6px 10px;cursor:pointer}
</style></head><body><div class="wrap"><div>
<canvas id="v" width="@AW@" height="@AH@" aria-label="Pixel-art meadow at sunset, gently moving"></canvas>
<div class="bar"><button id="play" type="button">Pause</button><button id="look" type="button">Amiga look: on</button><span id="info"></span></div>
</div></div>
<script>
@ENGINE@
const v=document.getElementById('v'),M=MeadowScene.start(v);
function fit(){const AW=952,AH=536,dpr=devicePixelRatio||1,avail=Math.min(innerWidth-32,(innerHeight-70)*AW/AH)*dpr,n=Math.max(1,Math.floor(avail/AW));
  const css=AW*n/dpr<=innerWidth-16?AW*n/dpr:(innerWidth-32);v.style.width=css+'px';v.style.height=(css*AH/AW)+'px'}
addEventListener('resize',fit);fit();
let paused=false,look=true;
document.getElementById('play').onclick=e=>{paused=!paused;M.pause(paused);e.target.textContent=paused?'Play':'Pause'};
document.getElementById('look').onclick=e=>{look=!look;M.look(look);e.target.textContent='Amiga look: '+(look?'on':'off')};
document.getElementById('info').textContent='7 fps';
window.__t=t=>M.t(t);
</script></body></html>"""
for k, val in {'@AW@': AW, '@AH@': AH, '@W@': W, '@H@': H, '@Y0@': Y0, '@CY@': CY, '@TOP@': json.dumps([round(float(t), 1) for t in top]),
               '@PAL@': json.dumps(PAL), '@TUNE@': json.dumps(TUNE), '@RAMPS@': json.dumps(ramps), '@CL@': json.dumps(CL), '@HIDDEN@': hidden,
               '@BASE@': png(base), '@FGR@': png(fgr), '@TREE@': png(tree_img), '@CMAP@': png(cmap),
               '@CLOUDS@': ','.join("'" + png(c['img']) + "'" for c in clouds)}.items():
    engine = engine.replace(k, str(val)); test = test.replace(k, str(val))
import sys
open('meadow.js', 'w').write(engine); open('meadow-test.html', 'w').write(test.replace('@ENGINE@', engine)); print('meadow.js', len(engine))
