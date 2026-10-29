"""Builds the waterfall test page from prep.py's layers: python build.py <step 1-6>
   writes step<N>.html (and index.html, the latest step). Each step adds one thing:
   1 the camp's Amiga look over the whole frame   2 the ferns sway   3 both falls flow   4 foam churns, mist rises
   5 ripples, the reflection streak shimmers, glints twinkle   6 now and then a fish jumps"""
import sys, json, base64, io, numpy as np
from PIL import Image
from scipy import ndimage as nd

STEP = int(sys.argv[1])
M = np.asarray(Image.open('master.png').convert('RGB')).astype(np.uint8)
BG = np.load('bg.npy').astype(np.uint8); FG = np.load('fg.npy'); SW = np.load('sway.npy'); K = np.load('masks.npz')
H, W = M.shape[:2]; AW, AH = 952, 536
def png(a): b = io.BytesIO(); Image.fromarray(a).save(b, 'PNG', optimize=True); return base64.b64encode(b.getvalue()).decode()

sway = SW if STEP >= 2 else np.zeros_like(SW)
base = np.where(sway[..., None], BG, M)                                   # the still picture, with water behind the ferns
ys = np.where(sway.any(1))[0]; Y0 = int(ys.min()) - 2 if len(ys) else H - 2
fgr = np.dstack([M, np.where(sway, 255, 0).astype(np.uint8)])[Y0:]
cols = sway[Y0:].any(0); top = np.where(cols, sway[Y0:].argmax(0), H - Y0 - 1).astype(np.float32)
top = nd.gaussian_filter1d(nd.minimum_filter1d(top, 25), 6)

# ---------- colour-cycling ramps (the colours each part already uses, darkest to brightest) ----------
B = base.astype(np.float32); lum = B @ [.299, .587, .114]; rows = np.arange(H)[:, None]
parts = [('fall1', 12), ('fall2', 10)] if STEP >= 3 else []
if STEP >= 4: parts += [('foam', 10)]
if STEP >= 5: parts += [('pool', 16), ('streak', 12)]
CY = 40; ramps = {}
cmA = np.zeros((H - CY, W, 4), np.uint8); cmA[..., 3] = 255                # R fall1, G fall2, B foam: ramp index + 1
cmB = np.zeros((H - CY, W, 4), np.uint8); cmB[..., 3] = 255                # R pool (1..) or streak (101..), G the falls' fade-in at the lip (1..21)
def ramp(k, m, n, img, ch, off=0):
    L = lum[m]; qs = np.quantile(L, np.linspace(0, 1, n + 1)); idx = np.clip(np.searchsorted(qs, L, 'right') - 1, 0, n - 1)
    ramps[k] = [B[m][idx == i].mean(0).round(1).tolist() for i in range(n)]; img[..., ch][m[CY:]] = (idx + 1 + off).astype(np.uint8)
stillfg = FG & ~sway                                                      # the rocks (and anything else still in front)
if STEP >= 3:
    for k, n, ch, lipk in (('fall1', 12, 0, 'lip1'), ('fall2', 10, 1, 'lip2')):
        m = K[k] & ~sway; ramp(k, m, n, cmA, ch)
        fade = np.clip((rows - K[lipk][None, :] - 3) / 12., 0, 1)        # the top 3 pixels of the fall hold still, the flow fades in below
        cmB[..., 1][m[CY:]] = np.maximum(cmB[..., 1][m[CY:]], (np.round(fade * 20) + 1).astype(np.uint8)[CY:][m[CY:]])
if STEP >= 4: ramp('foam', K['foam'] & ~sway & ~K['fall1'], 10, cmA, 2)
if STEP >= 5:
    pm = K['pool'] & ~stillfg & ~K['foam'] & ~K['fall1']; st = pm & K['streak']; pm = pm & ~K['streak']
    ramp('pool', pm, 16, cmB, 0); ramp('streak', st, 12, cmB, 0, 100)
cm_rgb, cm_b = cmA, cmB
pool_px = np.argwhere(K['pool'] & ~sway & (lum > 110))   # candidate spots for glints
rng = np.random.default_rng(3); glints = pool_px[rng.choice(len(pool_px), 18, replace=False)].tolist() if len(pool_px) else []
fishspots = np.argwhere(K['pool'] & ~nd.binary_dilation(FG, iterations=30) & ~K['streak'])
fishspots = fishspots[(fishspots[:, 0] > 690) & (fishspots[:, 0] < 820)]
fish = fishspots[rng.choice(len(fishspots), 24, replace=False)].tolist() if len(fishspots) else []

# ---------- the Pixel Tuner look (camp settings): a fixed 80-colour palette ----------
TUNE = dict(bright=6, contrast=-4, sat=7, temp=-3, shadows=-16, colors=80, dstr=42)
def tune(a):
    t = TUNE; a = a + t['bright'] / 200; a = (a - .5) * (1 + t['contrast'] / 100) + .5
    l = (a * [.299, .587, .114]).sum(-1, keepdims=True); a = l + (a - l) * (1 + t['sat'] / 100)
    a = a + np.array([1, 0, -1]) * t['temp'] / 100 * .12
    l = np.clip((a * [.299, .587, .114]).sum(-1, keepdims=True), 0, 1); a = a * (1 + t['shadows'] / 100 * (1 - l) ** 2)
    return np.clip(a, 0, 1)
small = np.asarray(Image.fromarray(M).resize((AW, AH), Image.BILINEAR)).astype(np.float32) / 255
pal = Image.fromarray((tune(small) * 255 + .5).astype(np.uint8)).quantize(TUNE['colors'], method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
PAL = np.array(pal.getpalette()[:TUNE['colors'] * 3]).reshape(-1, 3).tolist()

engine = r"""/* The waterfall: a pixel-art morning scene. Made by prototypes/waterfall/build.py from master.png and clean.png.
   WaterfallScene.start(canvas, active) draws into a 952x536 canvas at 7 fps while active() is true. */
window.WaterfallScene={start(v,active=()=>true){const API={ready:false};
const STEP=@STEP@,W=@W@,H=@H@,Y0=@Y0@,AW=@AW@,AH=@AH@,CY=@CY@,TOP=@TOP@,PAL=@PAL@,TUNE=@TUNE@,RAMPS=@RAMPS@,GLINTS=@GLINTS@,FISH=@FISH@;
const vg=v.getContext('2d');
const work=document.createElement('canvas');work.width=W;work.height=H;const g=work.getContext('2d');g.imageSmoothingEnabled=false;
const small=document.createElement('canvas');small.width=AW;small.height=AH;const sg=small.getContext('2d',{willReadFrequently:true});sg.imageSmoothingEnabled=true;sg.imageSmoothingQuality='high';
const glow=document.createElement('canvas');glow.width=AW;glow.height=AH;const gg=glow.getContext('2d');
const load=s=>new Promise(r=>{const i=new Image();i.onload=()=>r(i);i.src='data:image/png;base64,'+s});
const hash=n=>{const s=Math.sin(n*127.1)*43758.5453;return s-Math.floor(s)};
const vn=(x,y)=>{const ix=Math.floor(x),iy=Math.floor(y),fx=x-ix,fy=y-iy,u=fx*fx*(3-2*fx),w=fy*fy*(3-2*fy),h=(a,b)=>hash(a*57.3+b*131.7);
  return (h(ix,iy)*(1-u)+h(ix+1,iy)*u)*(1-w)+(h(ix,iy+1)*(1-u)+h(ix+1,iy+1)*u)*w};
const px=(c,x,y,col)=>{c.fillStyle=col;c.fillRect(Math.round(x/2)*2,Math.round(y/2)*2,2,2)};   // one art pixel, on the grid

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
    vg.save();vg.globalCompositeOperation='screen';vg.globalAlpha=.3;vg.drawImage(glow,0,0);vg.restore();
    const R=Math.hypot(AW*.6,AH*.55),vgr=vg.createRadialGradient(AW*.5,AH*.48,R*.4,AW*.5,AH*.48,R);vgr.addColorStop(0,'rgba(0,0,0,0)');vgr.addColorStop(1,'rgba(0,0,0,.8)');
    vg.fillStyle=vgr;vg.fillRect(0,0,AW,AH)}}

/* ---------- mist: soft puffs rising from the base of the fall and drifting slowly against the cliff ---------- */
const MIST=[];for(let i=0;i<16;i++)MIST.push({ph:hash(i*3.3)*14,x0:1020+hash(i*7.1)*330,dx:(hash(i*1.9)-.5)*70,r:34+hash(i*5.7)*40});
function mist(t){for(const m of MIST){const a=((t+m.ph)%14)/14,x=m.x0+m.dx*a+Math.sin(t*.25+m.ph)*14,y=625-a*170,r=m.r*(1+a*.9),al=.16*Math.sin(Math.PI*a);
  const gr=g.createRadialGradient(x,y,0,x,y,r);gr.addColorStop(0,`rgba(232,240,248,${al})`);gr.addColorStop(1,'rgba(232,240,248,0)');g.fillStyle=gr;g.fillRect(x-r,y-r,r*2,r*2)}}
/* ---------- glints and the fish ---------- */
function glints(t){for(let i=0;i<GLINTS.length;i++){const [y,x]=GLINTS[i],h=hash(i*4.7),k=Math.max(0,Math.sin(t*(.6+h*.9)+h*30));if(k<.92)continue;
  px(g,x,y,'#f4fbff');if(k>.985){px(g,x-2,y,'#cfe6f2');px(g,x+2,y,'#cfe6f2');px(g,x,y-2,'#cfe6f2');px(g,x,y+2,'#cfe6f2')}}}
const JUMPS=[];{let tt=55;for(let i=0;i<200;i++){JUMPS.push({s:tt,i});tt+=50+hash(i*2.3)*50}}   // the first after about a minute, then every 50-100 s
function ring(x,y,a,col){const r=4+a*26,n=Math.round(8+r*.9);for(let k=0;k<n;k++){const an=k/n*6.283;if(hash(k*1.3+a*.0)>1-a*.6)continue;px(g,x+Math.cos(an)*r,y+Math.sin(an)*r*.28,col)}}
function fish(t){for(const j of JUMPS){if(j.s>t)break;const a=t-j.s;if(a>3.4)continue;const [y0,x0]=FISH[j.i%FISH.length],dir=hash(j.i)>.5?1:-1;
  if(a<1){const x=x0+dir*a*30,y=y0-Math.sin(Math.PI*a)*26,c='#c9d6dc',d='#5f7480',up=a<.5;   // a small fish arcs out and back in
    px(g,x,y,c);px(g,x-dir*2,y+(up?2:-2)*.5,c);px(g,x+dir*2,y-(up?1:-1),d);px(g,x-dir*4,y+(up?2:-1),d);
    if(a<.25){px(g,x0-2,y0,'#e8f4f8');px(g,x0+2,y0-2,'#e8f4f8')}}
  ring(x0,y0,Math.min(1,a/2.4),'rgba(220,236,242,.85)');if(a>1)ring(x0+dir*30,y0,Math.min(1,(a-1)/2.4),'rgba(220,236,242,.85)')}}

Promise.all([load('@BASE@'),load('@FGR@'),load('@CMA@'),load('@CMB@')]).then(([bi,fi,ca,cb])=>{
  const fw=W,fh=H-Y0,tc=document.createElement('canvas');tc.width=fw;tc.height=fh;const tx=tc.getContext('2d');tx.drawImage(fi,0,0);
  const src=tx.getImageData(0,0,fw,fh).data,out=new ImageData(fw,fh),O=out.data;
  const wt=new Float32Array(fw*fh);for(let x=0;x<fw;x++){const t=TOP[x],span=Math.max(40,fh-t);for(let y=0;y<fh;y++){const k=Math.min(1,Math.max(0,(fh-y)/span));wt[y*fw+x]=k*k*(3-2*k)*k}}
  const ph=new Float32Array(fw);for(let x=0;x<fw;x++)ph[x]=Math.sin(x*.011)*1.7+Math.sin(x*.027+1.3)*1.1+Math.sin(x*.053+4.)*.6;
  const AMP=6,SNAP=2,FPS=7;let playing=true,t0=performance.now(),last=-1;
  const bc=document.createElement('canvas');bc.width=W;bc.height=H;const bx=bc.getContext('2d',{willReadFrequently:true});bx.drawImage(bi,0,0);const BASE=bx.getImageData(0,0,W,H),ORIG=BASE.data.slice();
  // colour cycling: each pixel keeps its place and only steps along the ramp of colours it belongs to
  const rd=im=>{const c=document.createElement('canvas');c.width=W;c.height=H-CY;const x=c.getContext('2d',{willReadFrequently:true});x.drawImage(im,0,0);return x.getImageData(0,0,W,H-CY).data};
  const A=rd(ca),Bm=rd(cb),L={fall1:[],fall2:[],foam:[]},FOAMPX=new Uint8Array(W*H),FADE=new Float32Array(W*H),KIND=new Uint8Array(W*H),RIDX=new Uint8Array(W*H),PL=[];
  for(let i=0,n=W*(H-CY);i<n;i++){const o=i+CY*W;if(A[i*4])L.fall1.push(o,A[i*4]-1);if(A[i*4+1])L.fall2.push(o,A[i*4+1]-1);if(A[i*4+2]){L.foam.push(o,A[i*4+2]-1);FOAMPX[o]=1}
    if(Bm[i*4+1])FADE[o]=(Bm[i*4+1]-1)/20;const q=Bm[i*4];if(q>100){KIND[o]=2;RIDX[o]=q-101;PL.push(o)}else if(q){KIND[o]=1;RIDX[o]=q-1;PL.push(o)}}
  const DEL={};for(const k in RAMPS){const R=RAMPS[k];DEL[k]=R.map((_,i)=>{const row=[];for(let s=-3;s<=3;s++){const j=Math.min(R.length-1,Math.max(0,i+s));row.push([R[j][0]-R[i][0],R[j][1]-R[i][1],R[j][2]-R[i][2]])}return row})}
  const put=(d,k,o,i,s)=>{const R=DEL[k],D=R[Math.min(i,R.length-1)][Math.max(-3,Math.min(3,s))+3],p=o*4;d[p]=ORIG[p]+D[0];d[p+1]=ORIG[p+1]+D[1];d[p+2]=ORIG[p+2]+D[2]};
  const FX=1172,FY=648;   // the base of the main fall
  function cycle(d,t){
    for(const [k,sp,len] of [['fall1',11,7],['fall2',8,5]]){const P=L[k];if(!P.length)continue;const PAT=[0,1,2,1,0,-1,-2,-1];   // bright and dark streaks running down each fall
      for(let q=0;q<P.length;q+=2){const o=P[q],x=o%W,y=(o/W)|0,c=Math.floor(x/3),h=hash(c*1.7+(k==='fall2'?40:0)),ph2=Math.floor((y+h*60)/(len+h*5)-t*sp*(.8+h*.5));
        put(d,k,o,P[q+1],Math.round(PAT[((ph2%8)+8)%8]*(.6+h*.5)*FADE[o]))}}   // held steady at the lip, flowing just below
    if(L.foam.length){const P=L.foam;for(let q=0;q<P.length;q+=2){const o=P[q],x=o%W,y=(o/W)|0;   // foam churning hard at the base
      const n=vn(x/6+t*2.1,y/4-t*3.3)+vn(x/2.5-t*1.7,y/2.5+t*2.6)*.7;put(d,'foam',o,P[q+1],Math.round((n-.7)*4.8))}}
    if(!PL.length)return;
    for(let q=0;q<PL.length;q++){const o=PL[q],x=o%W,y=(o/W)|0,dx=x-FX,dy=(y-FY)/.24,r=Math.sqrt(dx*dx+dy*dy);
      const near=Math.max(0,1-(y-FY)/280)*(.45+.55*Math.max(0,1-Math.abs(dx)/650));   // busy near the fall, calm toward you
      // the reflections wobble side to side (only ever borrowing water from the same row), the waves travelling toward you with a gentle current
      const wob=(1.5+7*near)*Math.sin(y*.42-t*3.1+Math.sin(x*.012+t*.4)*1.3)+(1+2*near)*Math.sin(y*1.3-t*5.2+x*.02);
      let so=o+Math.round(wob/2)*2;if(so<0||so>=W*H||(so/W|0)!==y||KIND[so]===0)so=o;const ks=KIND[so],ri=RIDX[so];let st;
      if(ks===2){const n=vn(x/8+t*2.4,y/2-t*5.5)+vn(x/3-t*1.8,y/1.6+t*4)*.5;st=Math.round((n-.75)*5.5)}   // the bright streak shimmers fast
      else{const w=Math.sin(r/15-t*2.4),fade=Math.max(0,1-r/820);                                       // rings spreading from the base, fading as they go
        const cur=vn(x/40,y/5-t*1.1)-.5;st=(w>.45?Math.round(3.2*fade):w<-.7?-Math.round(2.2*fade):0)+Math.round(cur*2.2*(.4+.6*near))}
      const RR=DEL[ks===2?'streak':'pool'],D=RR[Math.min(ri,RR.length-1)][Math.max(-3,Math.min(3,st))+3],p=o*4,ps=so*4;d[p]=ORIG[ps]+D[0];d[p+1]=ORIG[ps+1]+D[1];d[p+2]=ORIG[ps+2]+D[2]}}
  /* foam patches breaking off the base and drifting outward over the pool, fading */
  const PATCH=[];for(let i=0;i<46;i++)PATCH.push({ph:hash(i*3.1)*10,ang:(hash(i*5.3)-.5)*2.8,sp:12+hash(i*7.7)*22,sz:3+Math.floor(hash(i*2.2)*5)});
  function churn(t){const f=Math.floor(t*7);   // strong churning white water right where the fall hits the pool
    for(let y=FY-10;y<FY+22;y+=2)for(let x=FX-150;x<FX+150;x+=2){const ex=(x-FX)/150,ey=(y-FY-4)/16,e=ex*ex+ey*ey;if(e>1)continue;const o=y*W+x;if(o<0||o>=W*H||(KIND[o]===0&&!FOAMPX[o]))continue;
      const n=vn(x/6+f*.55,y/3-f*.9)*.65+vn(x/2.6-f*.4,y/2+f*.7)*.35;if(n<.38+.42*e)continue;px(g,x,y,n>.75?'#ffffff':n>.6?'#eef6fb':'#d6e6ef')}}
  function patches(t){for(let i=0;i<PATCH.length;i++){const P=PATCH[i],life=10,a=((t+P.ph)%life)/life,k=Math.floor((t+P.ph)/life);
      const ang=P.ang+(hash(i+k*13.7)-.5)*.6,dist=a*P.sp*life*(1-a*.35),x0=FX+(hash(i*1.3+k)-.5)*130,y0=FY+4;
      const x=x0+Math.sin(ang)*dist,y=y0+Math.abs(Math.cos(ang))*dist*.22+a*14;                              // flattened by perspective, carried toward you
      const vis=1-a*.85,n=Math.max(1,Math.round(P.sz*(1-a*.55)));
      for(let j=0;j<n*n;j++){if(hash(j*1.9+i*7.3+k)>vis*.95)continue;const ox=(j%n)*2-n,oy=Math.floor(j/n)*2-n*.6,o=(Math.round((y+oy)/2)*2)*W+Math.round((x+ox)/2)*2;
        if(o<0||o>=W*H||KIND[o]===0)continue;px(g,x+ox,y+oy,j%3?'#eef6fb':'#cfe2ec')}}}
  function frame(now){requestAnimationFrame(frame);const f=Math.floor((now-t0)/1000*FPS);if(f===last||!playing||!active())return;last=f;const t=f/FPS;
    if(STEP>=3){cycle(BASE.data,t)}g.putImageData(BASE,0,0);
    if(STEP>=5){churn(t);patches(t);glints(t)}if(STEP>=6)fish(t);if(STEP>=4)mist(t);
    if(STEP>=2){O.fill(0);const sw=.7+.3*Math.sin(t*.33);
      const off=new Float32Array(fw);for(let x=0;x<fw;x++)off[x]=AMP*sw*(Math.sin(t*1.2+ph[x])*.8+Math.sin(t*2.05+ph[x]*1.7)*.2);
      for(let y=0;y<fh;y++){const r=y*fw;for(let x=0;x<fw;x++){const d=Math.round(off[x]*wt[r+x]/SNAP)*SNAP,sx=x-d;
        if(sx<0||sx>=fw)continue;const si=(r+sx)*4;if(src[si+3]===0)continue;const o=(r+x)*4;O[o]=src[si];O[o+1]=src[si+1];O[o+2]=src[si+2];O[o+3]=255}}
      tx.putImageData(out,0,0);g.drawImage(tc,0,Y0)}
    finish()}
  requestAnimationFrame(frame);
  API.t=t=>{t0=performance.now()-t*1000;last=-1};API.pause=on=>{playing=!on;last=-1};API.look=on=>{lookOn=on;last=-1};API.ready=true;
});
return API}};
"""
shell = r"""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Waterfall test</title>
<style>
:root{--page:#1b1d22;--ink:#e8e4da}
html,body{margin:0;height:100%;background:var(--page);color:var(--ink);font:13px/1.4 system-ui,sans-serif}
.wrap{display:grid;place-items:center;min-height:100%;padding:16px;box-sizing:border-box}
canvas{display:block;image-rendering:pixelated;image-rendering:crisp-edges}
.bar{margin-top:10px;display:flex;gap:8px;align-items:center;flex-wrap:wrap;justify-content:center}
button{font:inherit;color:var(--ink);background:#2c2f36;border:1px solid #444a55;border-radius:8px;padding:6px 10px;cursor:pointer}
</style></head><body><div class="wrap"><div>
<canvas id="v" width="952" height="536" aria-label="Pixel-art waterfall into a forest pool, morning"></canvas>
<div class="bar"><button id="play" type="button">Pause</button><button id="look" type="button">Amiga look: on</button><span id="info"></span></div>
</div></div>
<script>
@ENGINE@
const v=document.getElementById('v'),S=WaterfallScene.start(v);
function fit(){const AW=952,AH=536,dpr=devicePixelRatio||1,avail=Math.min(innerWidth-32,(innerHeight-70)*AW/AH)*dpr,n=Math.max(1,Math.floor(avail/AW));
  const css=AW*n/dpr<=innerWidth-16?AW*n/dpr:(innerWidth-32);v.style.width=css+'px';v.style.height=(css*AH/AW)+'px'}
addEventListener('resize',fit);fit();
let paused=false,look=true;
document.getElementById('play').onclick=e=>{paused=!paused;S.pause(paused);e.target.textContent=paused?'Play':'Pause'};
document.getElementById('look').onclick=e=>{look=!look;S.look(look);e.target.textContent='Amiga look: '+(look?'on':'off')};
document.getElementById('info').textContent='Step @STEP@ of 6 · 7 fps';
window.__t=t=>S.t(t);
</script></body></html>"""
vals = {'@STEP@': STEP, '@W@': W, '@H@': H, '@Y0@': Y0, '@AW@': AW, '@AH@': AH, '@CY@': CY, '@TOP@': json.dumps([round(float(t), 1) for t in top]),
        '@PAL@': json.dumps(PAL), '@TUNE@': json.dumps(TUNE), '@RAMPS@': json.dumps(ramps), '@GLINTS@': json.dumps(glints), '@FISH@': json.dumps(fish),
        '@BASE@': png(base), '@FGR@': png(fgr), '@CMA@': png(cm_rgb), '@CMB@': png(cm_b)}
for k, val in vals.items(): engine = engine.replace(k, str(val)); shell = shell.replace(k, str(val))
page = shell.replace('@ENGINE@', engine)
open(f'step{STEP}.html', 'w').write(page); open('index.html', 'w').write(page); open('waterfall.js', 'w').write(engine)
print(f'step{STEP}.html', len(page))
