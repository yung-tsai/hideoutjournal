/* ==========================================================================
   Talio river camp — a flat pixel-art scene (720×405 art pixels) shown with
   nearest-neighbour scaling. Three times of day share one layout, so they
   crossfade. A code-drawn van interior looks out of its window at the live
   scene. Camera moves are CSS placement of the two canvases.
   ========================================================================== */
const clamp=(v,a=0,b=1)=>v<a?a:v>b?b:v,lerp=(a,b,t)=>a+(b-a)*t;
const ease=t=>t<.5?4*t*t*t:1-Math.pow(-2*t+2,3)/2,easeOut=t=>1-Math.pow(1-t,3),easeIn=t=>t*t*t;
function h2(x,y){let h=Math.imul(x|0,374761393)+Math.imul(y|0,668265263)|0;h=Math.imul(h^(h>>>13),1274126177);return((h^(h>>>16))>>>0)/4294967296}

/*@@SETS@@*/
/*@@SKY@@*/
let NW=720,NH=405,S=1.8;                       // the current scene's size in art pixels; S = pixels per 400-wide grid unit
const VAN={x:546,y:228};                       // the camper in scene pixels (per scene)
/* per-scene geometry; the original 720×405 scenes use these defaults */
const GEO0={warm:[43.2,270,.5],sunW:[28.8,270,.4],flow:[414,288],mist:null,focus:[200,300,118],van:[546,228],fishY:[290,370],leafX:[[20/720,230/720],[570/720,700/720]],leafY:[60/405,180/405]};
const geo=k=>(L&&L[k]!==undefined)?L[k]:GEO0[k];
const stageEl=document.getElementById('stage'),cv=document.getElementById('view'),inCv=document.getElementById('inside');
const ctx=cv.getContext('2d',{alpha:false});ctx.imageSmoothingEnabled=false;
const ictx=inCv.getContext('2d',{alpha:false});
/* screen effects chosen in Pixel Tuner: a soft glow (blurred copy, screen-blended) and a vignette, both on the camp only */
const glowCv=document.getElementById('glowfx'),gctx=glowCv.getContext('2d'),artVig=document.getElementById('artvig'),stageFx=document.getElementById('stagefx');let glowOn=false;

const PAL={
  sunrise:{gold:'#ffd8c8',goldDim:'#e0a8a8',lav:'#d6d4f0',lavDim:'#9a9cc8',refl:'#5a6a8a',mist:[214,214,236],smoke:[200,200,214],flame:['#fff0b4','#f8b45c','#d8642e']},
  sunset:{gold:'#f6d8a0',goldDim:'#dca880',lav:'#b8b4d4',lavDim:'#8c8cb4',refl:'#56687a',mist:[214,194,196],smoke:[176,170,184],flame:['#fff0b4','#f8b45c','#d8642e']},
  day:{gold:'#ffffff',goldDim:'#cfe4f4',lav:'#e8f4fc',lavDim:'#9cc4e4',refl:'#4c7c9c',mist:[226,236,244],smoke:[214,216,220],flame:['#fff4c8','#f8c070','#e08040']},
  night:{gold:'#ffc878',goldDim:'#c8885a',lav:'#b4c4ec',lavDim:'#5c6c9c',refl:'#28304c',mist:[120,132,176],smoke:[120,118,140],flame:['#fff0b4','#f8b45c','#d8642e']}};

/* ---------- scene state ---------- */
let L=null,C=PAL.sunset,A=null,sceneMode=null;
/* drifting clouds: a clean sky plate (alpha = open sky) and the free-floating clouds, cut from the painting.
   Clouds tucked behind trees or peaks stay in the plate; night clouds stay put. */
const CLOUD_V=.35,skyCv=document.createElement('canvas');skyCv.width=720;skyCv.height=SKY.h;const sctx=skyCv.getContext('2d');
let waterMask=null,waterIdx=[],sunIdx=[];const glints=[];
const maskAt=(x,y)=>(x<0||y<0||x>=NW||y>=NH)?0:waterMask[(y|0)*NW+(x|0)];
function spawn(g,t,initial){g.lx=undefined;const pool=(Math.random()<.35&&sunIdx.length)?sunIdx:waterIdx;const i=pool[(Math.random()*pool.length)|0];
  g.x=i%NW;g.y=(i/NW)|0;g.len=2+((Math.random()*3)|0);g.t0=t-(initial?Math.random()*6:0);g.life=4+Math.random()*4;
  const f=geo('flow'),j=.95+Math.random()*.1;g.vx=(g.x-f[0])*.0075*j;g.vy=(1+(g.y-f[1])*.011)*j}   // one current: everything slides downstream together, faster nearer the viewer
const mist=Array.from({length:7},(_,i)=>({x:(118+Math.random()*70)*S,y:276+Math.floor(Math.random()*6),len:16+Math.random()*26,v:(.4+Math.random()*.6)*(i%2?1:-1),a:i%3===0?.16:.1}));
const wind=(x,t)=>Math.sin(t*.8-x*.06)*.6+Math.sin(t*.31-x*.018+1.3)*.7;
const swayF=(x,t)=>Math.sin(t*.3-x*.016)+Math.sin(t*.11+x*.04)*.5;
let smoke=[],lastPuff=-10,embers=[],flameFrame=0,nextFlame=0;
const FLAME=[[[0,0,2],[1,0,1],[-1,0,2],[0,1,1],[1,1,2],[0,2,0],[0,3,1],[-1,1,2]],[[0,0,2],[-1,0,1],[1,0,2],[0,1,1],[-1,1,2],[0,2,1],[-1,3,0],[1,2,2]],[[0,0,2],[1,0,2],[-1,0,1],[0,1,0],[1,1,1],[1,2,1],[0,3,2],[-1,2,2]]];

function drawScene(t,still){
  ctx.globalAlpha=1;ctx.drawImage(A.base,0,0);
  if(A.plate){const o=still?0:Math.floor((t*CLOUD_V)%NW);
    if(o!==A.skyO){A.skyO=o;sctx.globalCompositeOperation='source-over';sctx.clearRect(0,0,NW,SKY.h);sctx.drawImage(A.plate,0,0);
      sctx.drawImage(A.clouds,o,0);sctx.drawImage(A.clouds,o-NW,0);sctx.globalCompositeOperation='destination-in';sctx.drawImage(A.plate,0,0);sctx.globalCompositeOperation='source-over'}
    ctx.drawImage(skyCv,0,0)}
  if(!still){const M=geo('mist'),x0=M?M[0]:110*S,span=M?M[1]-M[0]:100*S,my=M?M[2]:null;
    for(const m of mist){let x=m.x+m.v*t;x=x0+((((x-x0)%span)+span)%span);if(x+m.len>x0+span)continue;const y=my!=null?my+(m.y-276):m.y;
    ctx.fillStyle=`rgba(${C.mist[0]},${C.mist[1]},${C.mist[2]},${m.a})`;ctx.fillRect(Math.round(x),y,Math.round(m.len),1);ctx.fillRect(Math.round(x+6),y+1,Math.round(m.len*.6),1)}}
  for(const g of glints){let a=(t-g.t0)/g.life;if(a>=1){spawn(g,t,false);a=0}
    const age=t-g.t0,x=Math.round(g.x+g.vx*age),y=Math.round(g.y+g.vy*age),m0=maskAt(x,y),m1=maskAt(x+g.len-1,y);
    let gx=x,gy=y,g0=m0;if(!m0||!m1){if(g.lx===undefined){if(!still)spawn(g,t,false);continue}gx=g.lx;gy=g.ly;g0=maskAt(gx,gy)}else{g.lx=x;g.ly=y}   // at the water's edge a glint rests until it fades, instead of popping elsewhere
    if(still&&a>.5)continue;const wm=geo('warm'),bright=still||(a>.18&&a<.72),warm=Math.abs(gx-L.sunX)<wm[0]+(gy-wm[1])*wm[2];
    ctx.fillStyle=g0<200?C.refl:(bright?(warm?C.gold:C.lav):(warm?C.goldDim:C.lavDim));ctx.fillRect(gx,gy,bright?g.len:Math.max(1,g.len-1),1)}
  for(const x of L.tipColsB){const o=!still&&wind(x,t)>1.05?1:0;ctx.drawImage(A.tipsB,x,0,1,NH,x+o,0,1,NH)}
  for(const x of L.tipColsA){const w=still?0:wind(x,t),o=w>.6?1:(w<-1.15?-1:0);ctx.drawImage(A.tipsA,x,0,1,NH,x+o,0,1,NH)}
  for(const x of L.spireCols){const w=still?0:swayF(x,t),o=w>.85?1:(w<-1.25?-1:0);ctx.drawImage(A.spires,x,0,1,NH,x+o,0,1,NH)}
  const [fx,fy]=L.fire||[-99,-99],fire=!!L.fire;
  if(!still&&t>nextFlame){flameFrame=(flameFrame+1+((Math.random()*2)|0))%3;nextFlame=t+.18+Math.random()*.2}
  if(!fire){}
  else if(L.paintedFire){ // the fire is painted in: just let its light breathe
    const k=still?.5:.5+.5*Math.sin(t*9.1)*Math.sin(t*5.3+1),g=ctx.createRadialGradient(fx,fy-6,1,fx,fy-6,16);
    g.addColorStop(0,`rgba(255,190,100,${.10+.12*k})`);g.addColorStop(1,'rgba(255,170,90,0)');ctx.fillStyle=g;ctx.fillRect(fx-16,fy-22,32,32)}
  else for(const [dx,dy,c] of FLAME[still?0:flameFrame]){ctx.fillStyle=C.flame[c];ctx.fillRect(fx+dx,fy-2-dy,1,1)}
  if(L.falls&&!still){ // white water: bands of light and shadow travel down the falls (shadow is what reads on white water)
    const FP=10,FS=36,off=x=>Math.sin(x*.55)*1.7+Math.sin(x*.17)*1.3;   // neighbouring columns stay close, so the water reads as sheets, not noise
    ctx.fillStyle='rgba(70,94,134,.1)';
    for(const [x,y] of L.falls){const ph=((((y-t*FS+off(x))%FP)+FP)%FP);if(ph>=4&&ph<5.4)ctx.fillRect(x,y,1,1)}
    ctx.fillStyle='rgba(255,255,255,.26)';
    for(const [x,y] of L.falls){const ph=((((y-t*FS+off(x))%FP)+FP)%FP);if(ph<1.1)ctx.fillRect(x,y,1,1)}}
  if(L.stars)for(const [x,y,r,g,b,br,bg,bb] of L.stars){const p=still?1:Math.sin(t*(.35+(x%7)*.05)+x*1.3+y*.7);if(p<-.55)continue;
    ctx.fillStyle=p>.3?`rgb(${r},${g},${b})`:`rgb(${(r+br)>>1},${(g+bg)>>1},${(b+bb)>>1})`;ctx.fillRect(x,y,1,1)}
  if(still){drawFerns(t,true);return}
  const ey=L.paintedFire?fy-10:fy;if(fire&&Math.random()<.04)embers.push({t0:t,x:fx+(Math.random()*2-1),dx:Math.random()*.8-.3});
  embers=embers.filter(e=>t-e.t0<1.6);ctx.fillStyle=C.flame[1];
  for(const e of embers){const a=t-e.t0;ctx.fillRect(Math.round(e.x+e.dx*a*3),Math.round(ey-6-a*6),1,1)}
  if(fire&&t-lastPuff>1.7){lastPuff=t;smoke.push({t0:t,j:Math.random()*6.28})}
  smoke=smoke.filter(p=>t-p.t0<9);
  for(const p of smoke){const a=t-p.t0,x=Math.round(fx-1+a*1.1+Math.sin(a*.6+p.j)*1.4),y=Math.round(ey-7-a*2.6),sz=a<2.5?2:(a<5.5?3:4),al=a<3?.3:(a<6?.18:.08);
    ctx.fillStyle=`rgba(${C.smoke[0]},${C.smoke[1]},${C.smoke[2]},${al})`;ctx.fillRect(x,y,sz,sz-1)}
  drawLife(t,still);drawFerns(t,false);
}

/* ---------- the nearest ferns sway, the old way: eight steps a second, whole pixels, tips only ----------
   The ferns live on their own layer (the painting behind them was filled in), so a frond can lean a
   pixel or two and show water behind it. The lower part of each fern never moves, so the rocks it
   grows from stay put; the lean grows toward the tips. */
function drawFerns(t,still){
  if(!A||!A.ferns)return;
  if(still){ctx.drawImage(A.ferns,0,0);return}
  const T=Math.floor(t*8)/8;
  for(const g of A.fernG){const h=g.base-g.y0,w=g.x1-g.x0;
    const gust=.62*Math.sin(T*1.25+g.ph)+.38*Math.sin(T*.43+g.ph*1.7);   // a slow push and a slower swell
    let start=g.y0,cur=null;
    for(let y=g.y0;y<=g.y1+1;y++){
      let dx=0;if(y<=g.y1){const k=(g.base-y)/h,lift=Math.max(0,(k-.3)/.7);dx=Math.round(g.A*Math.pow(lift,1.3)*gust)}
      if(y===g.y1+1||dx!==cur){if(cur!==null&&y>start)ctx.drawImage(A.ferns,g.x0,start,w,y-start,g.x0+cur,start,w,y-start);cur=dx;start=y}}}
}

/* ---------- where the water lands: worked out once per scene ---------- */
let fallFoot=[],poolIdx=[];
function buildMotion(){
  // the foot of each fall, where the water lands and throws spray
  fallFoot=[];
  if(L.falls&&L.falls.length){const low=new Map();
    for(const [x,y] of L.falls){const o=low.get(x);if(o===undefined||y>o)low.set(x,y)}
    const xs=[...low.keys()].sort((a,b)=>a-b),runs=[];let run=[xs[0]];
    for(let i=1;i<xs.length;i++){if(xs[i]-xs[i-1]<=3)run.push(xs[i]);else{runs.push(run);run=[xs[i]]}}
    runs.push(run);
    for(const r of runs){if(r.length<6)continue;
      for(const x of r)fallFoot.push([x,low.get(x)])}}
  // the pool just downstream of the falls, where the current shows
  poolIdx=[];
  if(fallFoot.length){const fy=Math.max(...fallFoot.map(f=>f[1])),fx0=Math.min(...fallFoot.map(f=>f[0])),fx1=Math.max(...fallFoot.map(f=>f[0]));
    for(let y=fy-2;y<Math.min(NH,fy+54);y++)for(let x=Math.max(0,fx0-90);x<Math.min(NW,fx1+90);x++)if(waterMask[y*NW+x])poolIdx.push([x,y])}}

/* ---------- small life: birds, leaves, a jumping fish, fireflies and shooting stars ---------- */
const LIFE={birds:null,nextBirds:4,leaves:[],nextLeaf:3,fish:null,nextFish:12,star:null,nextStar:14,flies:null,far:null,nextFar:2,spray:[],cur:[]};
const rr=(a,b)=>a+Math.random()*(b-a);
const BIRD=[['x.....x','.xx.xx.','...x...'],['.......','.xxxxx.','x..x..x']];   // wings up, wings down
function px(x,y,c,a=1){ctx.globalAlpha=a;ctx.fillStyle=c;ctx.fillRect(Math.round(x),Math.round(y),1,1);ctx.globalAlpha=1}
function drawLife(t,still){
  const night=sceneMode==='night',day=sceneMode==='day';
  // birds: a small flock crosses the sky now and then (day and sunset)
  if(!night&&!LIFE.birds&&t>LIFE.nextBirds){const dir=Math.random()<.5?1:-1,n=2+((Math.random()*4)|0),y0=rr(30,110)*NH/405;
    LIFE.birds={t0:t,dir,v:rr(16,24),list:Array.from({length:n},(_,i)=>({dx:-i*rr(7,12)*dir,dy:(i%2?1:-1)*rr(2,6)*Math.ceil(i/2),ph:rr(0,6.3)})),y0}}
  if(LIFE.birds){const B=LIFE.birds,a=t-B.t0,cx=(B.dir>0?-30:NW+30)+B.dir*B.v*a;let any=false;
    const col=day?'#2c3442':'#2a1f2a';
    for(const b of B.list){const x=cx+b.dx,y=B.y0+b.dy+Math.sin(a*1.3+b.ph)*2;if(x<-40||x>NW+40)continue;any=true;
      const fr=BIRD[Math.sin(a*8+b.ph)>0?0:1];ctx.fillStyle=col;
      for(let r=0;r<3;r++)for(let c=0;c<7;c++)if(fr[r][c]==='x')ctx.fillRect(Math.round(x)+c-3,Math.round(y)+r-1,1,1)}
    if(!any&&a>2){LIFE.birds=null;LIFE.nextBirds=t+rr(7,16)}}
  // far off, high up: specks riding a thermal, barely moving
  if(!night&&!LIFE.far&&t>LIFE.nextFar){const dir=Math.random()<.5?1:-1;
    LIFE.far={t0:t,dir,v:rr(6,11),y0:rr(.04,.17)*NH,list:Array.from({length:3+((Math.random()*4)|0)},()=>({dx:rr(-34,34),dy:rr(-9,9),ph:rr(0,6.3),sp:rr(.5,1.1)}))}}
  if(LIFE.far){const B=LIFE.far,a=t-B.t0,cx=(B.dir>0?-50:NW+50)+B.dir*B.v*a;let any=false;
    for(const b of B.list){const x=cx+b.dx,y=B.y0+b.dy+Math.sin(a*.5*b.sp+b.ph)*3;if(x<-10||x>NW+10)continue;any=true;
      px(x,y,day?'#55657a':'#4a3f52',Math.sin(a*2.2*b.sp+b.ph)>-.3?.75:.4)}
    if(!any&&a>3){LIFE.far=null;LIFE.nextFar=t+rr(9,22)}}
  // the falls land hard: spray lifts off the foot, and the current streaks away downstream
  if(fallFoot.length&&!still){
    for(let k=0;k<2;k++)if(Math.random()<.75){const [fx,fy]=fallFoot[(Math.random()*fallFoot.length)|0];
      LIFE.spray.push({t0:t,x:fx+rr(-3,3),y:fy+rr(-2,2),vx:rr(-9,9),vy:-rr(10,26),life:rr(.5,1.2)})}
    LIFE.spray=LIFE.spray.filter(s=>t-s.t0<s.life);
    for(const s of LIFE.spray){const a=(t-s.t0)/s.life,x=s.x+s.vx*(t-s.t0),y=s.y+s.vy*(t-s.t0)+38*(t-s.t0)*(t-s.t0);
      px(x,y,a<.5?'#ffffff':C.lav,(1-a)*.75)}
    // a standing haze where it hits
    const hz=.5+.5*Math.sin(t*1.7);ctx.fillStyle=`rgba(255,255,255,${(night?.05:.09)*(.6+.4*hz)})`;
    for(const [fx,fy] of fallFoot)if(((fx*7)%5)<2)ctx.fillRect(fx-1,fy-1,3,3)}
  if(poolIdx.length&&!still){const f=geo('flow');
    ctx.fillStyle=`rgba(255,255,255,${night?.22:.34})`;
    for(let k=0;k<26;k++){const [x,y]=poolIdx[(Math.random()*poolIdx.length)|0];
      const ph=((y*3+x)%17)/17,a=((t*.9+ph)%1);if(a>.55)continue;
      const dx=Math.sign(x-f[0])*a*14,len=1+((Math.random()*3)|0);
      if(maskAt(x+dx,y))ctx.fillRect(Math.round(x+dx),y,len,1)}}
  // leaves drifting down from the big trees on either side
  if(!night&&t>LIFE.nextLeaf){const left=Math.random()<.55;const lx=geo('leafX'),ly=geo('leafY');LIFE.leaves.push({t0:t,x:(left?rr(lx[0][0],lx[0][1]):rr(lx[1][0],lx[1][1]))*NW,y:rr(ly[0],ly[1])*NH,ph:rr(0,6.3),c:Math.random()<.6?'#d98a3c':(day?'#7f9a4c':'#b0563a')});LIFE.nextLeaf=t+rr(4,9)}
  LIFE.leaves=LIFE.leaves.filter(l=>t-l.t0<14);
  for(const l of LIFE.leaves){const a=t-l.t0,x=l.x+Math.sin(a*1.4+l.ph)*6+a*3,y=l.y+a*13;if(y>NH)continue;const al=a<.6?a/.6:a>12?14-a>0?(14-a)/2:0:1;
    px(x,y,l.c,al);px(x+(Math.sin(a*2.8+l.ph)>0?1:-1),y,l.c,al*.8)}
  // a fish jumps in the river, then a ring spreads
  if(!LIFE.fish&&t>LIFE.nextFish&&waterIdx.length){for(let k=0;k<40;k++){const i=waterIdx[(Math.random()*waterIdx.length)|0];if(waterMask[i]>200){const x=i%NW,y=(i/NW)|0,fyR=geo('fishY');if(y>fyR[0]&&y<fyR[1]){LIFE.fish={t0:t,x,y,d:Math.random()<.5?1:-1};break}}}LIFE.nextFish=t+rr(14,30)}
  if(LIFE.fish){const F=LIFE.fish,a=t-F.t0;
    if(a<.7){const k=a/.7,h=Math.sin(k*Math.PI)*7,x=F.x+F.d*(k*8-4),y=F.y-h;px(x,y,C.lav);px(x-F.d,y+(k<.5?1:-1),C.lavDim)}
    if(a>.6&&a<2.6){const r=(a-.6)*4,al=1-(a-.6)/2;for(let s=0;s<18;s++){const an=s/18*6.283;if(maskAt(F.x+Math.cos(an)*r,F.y+Math.sin(an)*r*.4))px(F.x+Math.cos(an)*r,F.y+Math.sin(an)*r*.4,C.lav,al*.8)}}
    if(a>2.6)LIFE.fish=null}
  // night: fireflies around the camp and banks, and the odd shooting star
  if(night){if(!LIFE.flies){const fb=L.flies||[380,710,225,320];LIFE.flies=Array.from({length:16},()=>({x:rr(fb[0],fb[1]),y:rr(fb[2],fb[3]),ph:rr(0,6.3),sp:rr(.4,.9)}))}
    for(const f of LIFE.flies){const x=f.x+Math.sin(t*.3*f.sp+f.ph)*10,y=f.y+Math.sin(t*.47*f.sp+f.ph*2)*5,g=Math.sin(t*1.6*f.sp+f.ph);
      if(g>.1){px(x,y,'#e8f59a',Math.min(1,g*1.4));if(g>.6){ctx.globalAlpha=(g-.6)*.5;ctx.fillStyle='#d8f070';ctx.fillRect(Math.round(x)-1,Math.round(y)-1,3,3);ctx.globalAlpha=1}}}
    if(!LIFE.star&&t>LIFE.nextStar){LIFE.star={t0:t,x:rr(180,560),y:rr(8,60),dx:rr(.8,1.2)*(Math.random()<.5?1:-1)};LIFE.nextStar=t+rr(22,50)}
    if(LIFE.star){const st=LIFE.star,a=(t-st.t0)/.8;if(a>1)LIFE.star=null;else for(let i=0;i<12;i++){const k=a*40-i*1.6;if(k<0)continue;px(st.x+st.dx*k,st.y+k*.45,'#f4f0ff',(1-i/12)*(1-a*.6))}}}
  else LIFE.flies=null;
  drawSquirrel(t,still,night);
}

/* ==========================================================================
   A squirrel. It comes out from behind the big tree, crosses the grass in
   front of the fire, stops to look both ways, sits and flicks its tail,
   sometimes turns something over in its paws, then goes back the way it came.
   Morning and midday only (by sunset the fire is lit and squirrels are
   home), and never while the scene is held still.
   geo('squirrel') = [homeX, groundY, scale, nearestStop, farthestStop, trunkEdge]
   ========================================================================== */
const SQW=22,SQH=19,SQI=new Image();SQI.src='/*@@SQIMG@@*/';
const SQA={run:[[2,0],[2,1],[2,2],[2,3],[2,4],[2,5],[2,6],[2,7]],   // 8-frame scamper
           rear:[[5,1],[5,2],[5,3],[5,2]],                          // up on its back legs
           sit:[[0,0],[0,1],[0,2],[0,3],[0,4],[0,5]],               // sitting, tail flicking
           eat:[[4,0],[4,1]]};
const sqBuf=document.createElement('canvas'),sqx=sqBuf.getContext('2d');
const SQTINT={day:'rgba(150,172,196,.12)',sunrise:'rgba(96,112,160,.30)',sunset:'rgba(246,186,128,.20)',night:null};
let squirrel=null,nextSq=16;
function sqDraw(fr,x,by,sc,flip,tint,edge){
  const dw=Math.max(1,Math.round(SQW*sc)),dh=Math.max(1,Math.round(SQH*sc));
  if(sqBuf.width!==dw||sqBuf.height!==dh){sqBuf.width=dw;sqBuf.height=dh}
  sqx.clearRect(0,0,dw,dh);sqx.imageSmoothingEnabled=false;sqx.save();
  if(flip){sqx.translate(dw,0);sqx.scale(-1,1)}
  sqx.drawImage(SQI,fr[1]*SQW,fr[0]*SQH,SQW,SQH,0,0,dw,dh);sqx.restore();
  if(tint){sqx.globalCompositeOperation='source-atop';sqx.fillStyle=tint;sqx.fillRect(0,0,dw,dh);sqx.globalCompositeOperation='source-over'}
  const px0=Math.round(x-dw/2);
  ctx.save();if(edge){ctx.beginPath();ctx.rect(0,0,edge,NH);ctx.clip()}
  ctx.globalAlpha=.22;ctx.fillStyle='#1c2418';ctx.fillRect(px0+1,Math.round(by)-1,dw-2,1);ctx.globalAlpha=1;   // it keeps its feet on the grass
  ctx.drawImage(sqBuf,px0,Math.round(by)-dh);ctx.restore();
}
function drawSquirrel(t,still,night){
  const G=geo('squirrel');
  if(!G||still||night||L.fire||!SQI.naturalWidth){squirrel=null;return}   // not past a lit fire, and squirrels are home by dusk
  if(!squirrel){
    if(t<nextSq)return;
    squirrel={s:'in',t0:t,x:G[0],stop:rr(G[3],G[4]),meal:Math.random()<.45};
  }
  const q=squirrel,gy=G[1],sc=G[2],a=t-q.t0,cyc=(k,n)=>k[((a*n)|0)%k.length],step=Math.floor(a*8)/8;   // it moves in 8-a-second hops, like an old sprite
  let fr,flip=true;
  if(q.s==='in'){
    q.x=Math.max(q.stop,G[0]-step*24);fr=cyc(SQA.run,8);
    if(q.x<=q.stop){q.s='look';q.t0=t}
  }else if(q.s==='look'){                       // one way, then the other
    flip=a<1.15;fr=a<.25?SQA.sit[0]:cyc(SQA.rear,4);
    if(a>2.3){q.s=q.meal?'eat':'sit';q.t0=t}
  }else if(q.s==='eat'){
    fr=cyc(SQA.eat,3);if(a>2.6){q.s='sit';q.t0=t}
  }else if(q.s==='sit'){
    fr=cyc(SQA.sit,4);if(a>(q.meal?2.2:3.4)){q.s='perk';q.t0=t}
  }else if(q.s==='perk'){                       // something startles it
    flip=false;fr=cyc(SQA.rear,5);if(a>.8){q.s='out';q.t0=t}
  }else{
    flip=false;q.x=q.stop+step*32;fr=cyc(SQA.run,8);
    if(q.x>G[0]+8){squirrel=null;nextSq=t+rr(42,95);return}
  }
  sqDraw(fr,q.x,gy,sc,flip,SQTINT[sceneMode],G[5]);   // the trunk hides it as it comes and goes
}

/* The van is part of the painting. (Its paint and add-ons were removed; see IDEAS.md and the tag van-upgrades-v1.) */
const Van={dress:(which,base)=>base,set(){},whenReady:f=>f()};

/* ---------- loading a time of day (crossfades from the last frame) ---------- */
const fadeCv=document.createElement('canvas');fadeCv.width=NW;fadeCv.height=NH;let fctx=fadeCv.getContext('2d');
let fadeAt=-1,loadTok=0;
const img=src=>new Promise(r=>{const i=new Image();i.onload=()=>r(i);i.src=src});
function loadScene(which,instant){
  if(which===sceneMode&&A)return;const my=++loadTok;
  const Ls=SETS[which];
  const Sk=SKY.sets[which];
  Promise.all([img(Ls.base),img(Ls.tipsA),img(Ls.tipsB),img(Ls.spires),img(Ls.water),Sk&&!Ls.w?img(Sk.skyplate):null,Sk&&!Ls.w?img(Sk.clouds):null,Ls.ferns?img(Ls.ferns):null]).then(([base,tipsA,tipsB,spires,water,plate,clouds,fernImg])=>{
    if(my!==loadTok)return;
    if(A&&!instant){fadeCv.width=cv.width;fadeCv.height=cv.height;fctx=fadeCv.getContext('2d');fctx.drawImage(cv,0,0);fadeAt=performance.now()}
    sceneMode=which;L=Ls;C=Ls.pal?{...PAL[which],...Ls.pal}:PAL[which];A={base,tipsA,tipsB,spires,plate,clouds,skyO:-1};
    A.raw=base;A.base=Van.dress(which,base);A.ferns=fernImg;A.fernG=(Ls.fernGroups||[]).map(g=>({x0:g[0],y0:g[1],x1:g[2],y1:g[3],base:g[4],A:g[5],ph:g[0]*.021+Math.random()*.6}));
    NW=Ls.w||720;NH=Ls.h||405;S=Ls.s||1.8;const v=geo('van');VAN.x=v[0];VAN.y=v[1];
    if(cv.width!==NW||cv.height!==NH){cv.width=NW;cv.height=NH;ctx.imageSmoothingEnabled=false;pc.e.k=''}
    glowCv.width=NW;glowCv.height=NH;glowOn=!!(Ls.fx&&Ls.fx.glow);glowCv.style.opacity=glowOn?Ls.fx.glow:0;artVig.style.opacity=Ls.fx&&Ls.fx.vig?1:0;
    if(Ls.fx&&Ls.fx.vig)artVig.style.background=`radial-gradient(120% 110% at 50% 48%,transparent 40%,rgba(0,0,0,${Ls.fx.vig}) 100%)`;
    const oc=document.createElement('canvas');oc.width=NW;oc.height=NH;const o=oc.getContext('2d');o.drawImage(water,0,0);
    const d=o.getImageData(0,0,NW,NH).data;waterMask=new Uint8Array(NW*NH);waterIdx=[];sunIdx=[];
    for(let i=0;i<NW*NH;i++)if(d[i*4+3]>0){waterMask[i]=d[i*4];waterIdx.push(i);const x=i%NW,y=(i/NW)|0;if(d[i*4]>200&&Math.abs(x-L.sunX)<geo('sunW')[0]+(y-geo('sunW')[1])*geo('sunW')[2])sunIdx.push(i)}
    glints.length=0;const n=innerWidth<700?140:200;for(let i=0;i<n;i++){const g={};spawn(g,0,true);glints.push(g)}
    buildMotion();
    buildInterior();drawNow();ready=true});
}

/* ==========================================================================
   Van interior: painted layers per time of day (sky, clouds, mountains, lake,
   trees, the van's window wall, and a foreground of blanket and mug).
   Clouds drift on a mirrored loop, the lake shimmers, treetops sway, and at
   night the stars twinkle and the string lights and lamp glow.
   ========================================================================== */
/*@@INSIDE@@*/
const IN={mode:null,want:null,L:null,port:false,glints:[],birds:null,nextBirds:4,fade:document.createElement('canvas'),fadeAt:-1};
IN.fade.width=720;IN.fade.height=405;
const inCache={};
function loadInside(m){
  if(inCache[m])return inCache[m];const S=INS.sets[m],keys=Object.keys(S);
  return inCache[m]=Promise.all(keys.map(k=>img(S[k]))).then(ims=>{const o={};keys.forEach((k,i)=>o[k]=ims[i]);
    // a mirrored copy after the clouds makes a seamless loop
    if(o.clouds){const c=document.createElement('canvas');c.width=1440;c.height=405;const g=c.getContext('2d');
    g.drawImage(o.clouds,0,0);g.save();g.translate(1440,0);g.scale(-1,1);g.drawImage(o.clouds,0,0);g.restore();o.strip=c}return o})}
function buildInterior(){
  IN.port=innerHeight>innerWidth*1.05;const m=sceneMode||'sunset';if(IN.want===m)return;
 IN.want=m;
  loadInside(m).then(o=>{if(IN.want!==m)return;
    if(IN.L&&IN.mode!==m){IN.fade.getContext('2d').drawImage(inCv,0,0);IN.fadeAt=performance.now()}
    const M=(INS.meta||{})[m],w=M?M.w:720,h=M?M.h:405;
    if(inCv.width!==w||inCv.height!==h){inCv.width=w;inCv.height=h;pc.i.k='';IN.fadeAt=-1}
    if(IN.fade.width!==w){IN.fade.width=w;IN.fade.height=h}
    IN.L=o;IN.mode=m;IN.M=M;IN.glints=[];if(mode!=='out'||tr)drawInside((performance.now()-T0)/1000,reducedMotion)})}
const GLINT={sunset:'#ffe6ae',sunrise:'#ffe2ea',day:'#ffffff',night:'#cfd9ff'};
function drawInside(t,still){
  const o=IN.L;if(!o)return;const g=ictx,m=IN.mode,night=m==='night';g.imageSmoothingEnabled=false;g.globalAlpha=1;
  const M=IN.M,full=!!o.full,water=M?M.water:full?INS.waterRef:INS.water,CW=inCv.width;
  if(full)g.drawImage(o.full,0,0);   // one finished painting: the sky holds still, small things move on top
  else{
  g.drawImage(o.sky,0,0);
  if(night)for(const [x,y,r,gg,b,sz] of INS.stars){const p=still?1:Math.sin(t*(.4+(x%5)*.07)+x*.9+y*1.7);if(p<-.6)continue;
    g.fillStyle=`rgb(${r},${gg},${b})`;g.globalAlpha=p>.2?1:.5;g.fillRect(x,y,1,1);
    if(sz>1&&p>.55){g.globalAlpha=.3;g.fillRect(x-1,y,3,1);g.fillRect(x,y-1,1,3)}g.globalAlpha=1}
  const off=still?0:(t*.7)%1440;g.drawImage(o.strip,-Math.floor(off),0);g.drawImage(o.strip,1440-Math.floor(off),0);
  g.drawImage(o.mount,0,0);if(o.lake)g.drawImage(o.lake,0,0);}
  if(!still){ // lake shimmer
    while(IN.glints.length<22){const w=water[(Math.random()*water.length)|0];IN.glints.push({x:w[0],y:w[1],t0:t+Math.random()*2,life:1.5+Math.random()*2.5,len:1+((Math.random()*3)|0)})}
    g.fillStyle=GLINT[m];
    for(const s of IN.glints){const a=(t-s.t0)/s.life;if(a<0)continue;g.globalAlpha=Math.sin(Math.min(1,a)*Math.PI)*(night?.6:.85);g.fillRect(s.x,s.y,s.len,1)}
    g.globalAlpha=1;IN.glints=IN.glints.filter(s=>t-s.t0<s.life)
    // birds now and then (day and sunset)
    if(!night&&!IN.birds&&t>IN.nextBirds){const dir=Math.random()<.5?1:-1;IN.birds={t0:t,dir,v:14+Math.random()*8,y0:(M?M.birdY[0]+Math.random()*(M.birdY[1]-M.birdY[0]):50+Math.random()*90),list:Array.from({length:2+((Math.random()*3)|0)},(_,i)=>({dx:-i*(8+Math.random()*5)*dir,dy:(i%2?1:-1)*Math.ceil(i/2)*(2+Math.random()*4),ph:Math.random()*6.3}))}}
    if(IN.birds){const B=IN.birds,a=t-B.t0,cx=(B.dir>0?-30:CW+30)+B.dir*B.v*a;let any=false;g.fillStyle=m==='day'?'#2c3442':'#3a2430';
      for(const b of B.list){const x=cx+b.dx,y=B.y0+b.dy+Math.sin(a*1.3+b.ph)*2;if(x<-20||x>CW+20)continue;any=true;const fr=BIRD[Math.sin(a*8+b.ph)>0?0:1];
        for(let r=0;r<3;r++)for(let c=0;c<7;c++)if(fr[r][c]==='x')g.fillRect(Math.round(x)+c-3,Math.round(y)+r-1,1,1)}
      if(!any&&a>2){IN.birds=null;IN.nextBirds=t+15+Math.random()*25}}}
  // trees: the tops lean a pixel with the wind, the far forest stays still
  if(full){}
  else if(still)g.drawImage(o.trees,0,0);
  else for(let y=0;y<405;y+=3){const k=Math.max(0,(320-y)/320),dx=Math.round(Math.sin(t*.7+y*.03)*k*1.3+Math.sin(t*.21+y*.012)*k*.7);g.drawImage(o.trees,0,y,720,3,dx,y,720,3)}
  if(o.frame)g.drawImage(o.frame,0,0);if(o.fg)g.drawImage(o.fg,0,0);
  const bulbs=M?M.bulbs:INS.bulbs,lampP=M?M.lamp:INS.lamp,lit=night||(M&&M.lit);
  if(lit){ // string lights and lamp breathe a little
    const gk=night?1:.55;
    for(let i=0;i<bulbs.length;i++){const [x,y]=bulbs[i],k=still?.8:.7+.3*Math.sin(t*1.1+i*1.9)*Math.sin(t*.43+i);
      g.globalAlpha=.16*k*gk;g.fillStyle='#ffc46a';g.fillRect(x-4,y-3,9,7);g.fillRect(x-3,y-4,7,9);g.globalAlpha=.3*k*gk;g.fillRect(x-2,y-2,5,5)}
    if(lampP){const [lx,ly]=lampP,k=still?1:.85+.15*Math.sin(t*.9)*Math.sin(t*2.3),rg=g.createRadialGradient(lx,ly,2,lx,ly,70);
      rg.addColorStop(0,'rgba(255,190,110,'+(.22*k*gk)+')');rg.addColorStop(1,'rgba(255,190,110,0)');g.globalAlpha=1;g.fillStyle=rg;g.fillRect(lx-70,ly-70,140,140)}
    g.globalAlpha=1}
  if(!still){ // steam from the mug
    const sx=M?M.steam[0]:full?88:86,sy=M?M.steam[1]:full?337:m==='sunset'?313:318;g.fillStyle=night?'rgba(230,215,200,1)':'rgba(255,250,240,1)';
    if(M){ // steam: 2–3 thin connected wisps that sway in an S-curve and thin out as they rise
      const col=night?[226,212,200]:[255,238,218],H=58;
      g.fillStyle=`rgb(${col[0]},${col[1]},${col[2]})`;
      for(let w=0;w<3;w++){const ph=w*2.3,off=(w-1)*5,life=.55+.45*Math.sin(t*.33+w*1.9);   // each wisp swells and fades on its own
        if(life<.15)continue;
        const lean=Math.sin(t*.21+w)*3;
        for(let h=0;h<H;h++){const u=h/H,
            x=sx+off*(1-u*.4)+lean*u+Math.sin(u*5.2-t*1.05+ph)*(1.2+u*6)+Math.sin(u*11-t*1.7+ph)*u*1.5,
            a=Math.pow(1-u,1.15)*(u<.05?u/.05:1)*life*(night?.38:.5)*(.7+.3*Math.sin(u*14-t*2.2+ph));
          if(a<.02)continue;g.globalAlpha=a;const wd=u<.45?2:1;g.fillRect(Math.round(x)-(wd>1?1:0),sy-1-h,wd,1)}}}
    else for(let i=0;i<5;i++){const a=((t*.4+i/5)%1),y=sy-a*30,x=sx+Math.sin(a*6+i*1.3)*3;g.globalAlpha=(1-a)*(night?.22:.32);g.fillRect(Math.round(x),Math.round(y),2,2)}g.globalAlpha=1}
  if(IN.fadeAt>0){const k=(performance.now()-IN.fadeAt)/1400;if(k>=1)IN.fadeAt=-1;else{g.globalAlpha=1-ease(k);g.drawImage(IN.fade,0,0);g.globalAlpha=1}}
}

/* ==========================================================================
   Camera: each canvas is placed with CSS. A pose is a focus point (canvas px)
   pinned to a screen point, at a zoom relative to "cover" scale.
   ========================================================================== */
let mode='out',tr=null,quickVisit=false,reducedMotion=false,renderPaused=false,ready=false;
const viewK={panel:0,panelT:0,bottom:0,bottomT:0,focus:0,focusT:0,pf:0,pfT:0};
function place(el,w,h,P,cache,ri=0,bi=0){ // ri/bi: screen covered by a panel, which the art may leave bare
  const W=innerWidth,H=innerHeight,s=Math.max(W/w,H/h)*P.z;
  let x=P.sx-P.fx*s,y=P.sy-P.fy*s;x=Math.min(0,Math.max(W-ri-w*s,x));y=Math.min(0,Math.max(H-bi-h*s,y));
  const k=`${(w*s).toFixed(1)}|${x.toFixed(1)}|${y.toFixed(1)}`;if(cache.k===k)return;cache.k=k;
  el.style.width=(w*s)+'px';el.style.height=(h*s)+'px';el.style.left=x+'px';el.style.top=y+'px'}
function extRest(){
  const W=innerWidth,H=innerHeight,s0=Math.max(W/NW,H/NH),visW=W/s0,k=clamp((350*S-visW)/((350-130)*S));
  const F=geo('focus'),fx0=lerp(F[0]*S,F[1]*S,k),fy0=F[2]*S,free=W-viewK.panel,freeH=H-viewK.bottom;
  return{fx:lerp(fx0,VAN.x,viewK.pf),fy:lerp(fy0,VAN.y,viewK.pf*.8),sx:free/2,sy:viewK.bottom?Math.max(90,freeH*.55):H/2,z:lerp(1,1.75,ease(viewK.focus))}}
function inRest(){const M=IN.M;return{fx:inCv.width/2,fy:M?inCv.height*(IN.port?.42:.5):(IN.port?178:202),sx:innerWidth/2,sy:innerHeight/2,z:1}}
const lp=(a,b,k)=>({fx:lerp(a.fx,b.fx,k),fy:lerp(a.fy,b.fy,k),sx:lerp(a.sx,b.sx,k),sy:lerp(a.sy,b.sy,k),z:lerp(a.z,b.z,k)});
const DUR={enter:2.4,exit:1.9,fade:1.0};
function poseAt(t){ // t on the entering timeline (0 = outside, end = inside); exit plays it backwards
  if(reducedMotion){const k=clamp(t/DUR.fade);return{ext:extRest(),eo:1-k,int:inRest(),io:k}}
  // a plain fade out of camp, then the van fades in with a barely-there settle
  const eo=1-ease(clamp(t/.85)),io=ease(clamp((t-.42)/.85)),dk=easeOut(clamp((t-.42)/1.6));   // overlap the fades: no dark gap now the card comes up straight away
  return{ext:extRest(),eo,int:{...inRest(),z:lerp(1.035,1,dk)},io}}
const pc={e:{},i:{}};let lastEo=-1,lastIo=-1;
function placeViews(){
  let P;
  if(tr){const total=reducedMotion?DUR.fade:DUR.enter,tt=tr.dir>0?tr.t:total-tr.t*(total/(reducedMotion?DUR.fade:DUR.exit));P=poseAt(Math.max(0,tt))}
  else if(mode==='in')P={ext:extRest(),eo:0,int:inRest(),io:1};
  else P={ext:extRest(),eo:1,int:inRest(),io:0};
  place(cv,NW,NH,P.ext,pc.e,viewK.panel*.72,viewK.bottom);place(inCv,inCv.width,inCv.height,P.int,pc.i);   // the art may run partly under a side panel; its glass shows it
  if(pc.e.k!==pc.g){pc.g=pc.e.k;for(const el of [glowCv,artVig]){el.style.left=cv.style.left;el.style.top=cv.style.top;el.style.width=cv.style.width;el.style.height=cv.style.height}
    glowCv.style.filter=`blur(${Math.max(2,parseFloat(cv.style.width)/NW*1.6)}px)`}
  if(P.eo!==lastEo){cv.style.opacity=P.eo;stageFx.style.opacity=P.eo;lastEo=P.eo}
  if(P.io!==lastIo){inCv.style.opacity=P.io;inCv.style.visibility=P.io>0?'visible':'hidden';lastIo=P.io}
}
function startEnter(done){
  if(tr||mode!=='out')return false;mode='entering';buildInterior();
  const today=new Date().toDateString();quickVisit=state.meta.walkDay===today;   // the full move once a day; a quicker one after that
  if(!quickVisit){state.meta.walkDay=today;persist()}
  tr={t:0,dur:reducedMotion?DUR.fade:DUR.enter,dir:1,done,speed:quickVisit&&!reducedMotion?1.5:1};drawNow();return true}
function startExit(done){
  if(tr||mode!=='in')return false;mode='exiting';tr={t:0,dur:reducedMotion?DUR.fade:DUR.exit,dir:-1,done,speed:quickVisit&&!reducedMotion?1.3:1};return true}
document.addEventListener('pointerdown',()=>{if(tr&&(mode==='entering'||mode==='exiting'))tr.speed=Math.max(tr.speed||1,5)},true);   // tap to skip
function finishTr(m){const d=tr.done;tr=null;mode=m;if(d)setTimeout(d,0)}
function size(){IN.port=innerHeight>innerWidth*1.05;pc.e.k=pc.i.k='';placeViews();if(A)drawNow()}

/* ---------- loop: camera at display rate, art at a steppy 12 fps ---------- */
const STEP=1000/12,T0=performance.now();let lastF=0,lastDraw=0;
function drawNow(){if(!A)return;const t=(performance.now()-T0)/1000,still=reducedMotion;const outside=mode!=='in'||tr;
  if(outside)drawScene(t,still);   // the camp isn't visible from inside the van
  if(outside&&fadeAt>0){const k=(performance.now()-fadeAt)/1400;if(k>=1)fadeAt=-1;else{ctx.globalAlpha=1-ease(k);ctx.drawImage(fadeCv,0,0,NW,NH);ctx.globalAlpha=1}}
  if(outside&&glowOn){gctx.clearRect(0,0,NW,NH);gctx.drawImage(cv,0,0)}
  if(mode!=='out'||tr)drawInside(t,still)}
function frame(now){
  requestAnimationFrame(frame);
  const dt=Math.min(.1,(now-(lastF||now))/1000);lastF=now;
  if(tr){tr.t+=dt*(tr.speed||1);if(tr.t>=tr.dur)finishTr(tr.dir>0?'in':'out')}
  const k=1-Math.exp(-dt*(reducedMotion?14:4.5));
  for(const n of ['panel','bottom','focus','pf'])viewK[n]+=(viewK[n+'T']-viewK[n])*k;
  placeViews();
  if(!A||(renderPaused&&!tr))return;
  if(reducedMotion&&fadeAt<0&&!tr&&now-lastDraw<1000)return;
  if(now-lastDraw>=STEP||(fadeAt>0||IN.fadeAt>0)&&now-lastDraw>=33){lastDraw=now;drawNow()}
}
function applyState(){loadScene(ST.time==='night'?'night':ST.time==='golden'?'sunset':ST.time==='morning'&&SETS.sunrise?'sunrise':'day');if(A)drawNow()}
