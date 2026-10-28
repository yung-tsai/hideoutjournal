/* ==========================================================================
   The fire: somewhere to let an entry go. Always night.
   The painting supplies the meadow, river and sky; the campfire (stones, logs,
   coals, flames) and the light it throws are drawn here, so it is one light.
   Burn.open({text, concern, onExit}) — onExit('inside' | 'camp' | 'burned').
   Nothing here saves or sends the words anywhere.
   ========================================================================== */
const Burn=(()=>{
const PWD=952,FULLH=1428,EXT=840,VIEWH=536;          // painting size; top of the resting window; its height on desktop
const clamp=(v,a=0,b=1)=>v<a?a:v>b?b:v,lerp=(a,b,k)=>a+(b-a)*k,ease=k=>k*k*(3-2*k);
let seed=5;const rnd=()=>{seed|=0;seed=seed+0x6D2B79F5|0;let t=Math.imul(seed^seed>>>15,1|seed);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296};
const hash=(x,y)=>{let h=(x|0)*374761393+(y|0)*668265263;h=(h^(h>>>13))*1274126177;return((h^(h>>>16))>>>0)/4294967296};
function vn(x,y){const xi=Math.floor(x),yi=Math.floor(y),xf=x-xi,yf=y-yi,u=xf*xf*(3-2*xf),v=yf*yf*(3-2*yf);
  const a=hash(xi,yi),b=hash(xi+1,yi),c=hash(xi,yi+1),d=hash(xi+1,yi+1);return a+(b-a)*u+(c-a)*v+(a-b-c+d)*u*v}
const fbm=(x,y)=>vn(x,y)*.55+vn(x*2.1+7,y*2.1+3)*.3+vn(x*4.3+1,y*4.3+9)*.15;
const BAY=[0,8,2,10,12,4,14,6,3,11,1,9,15,7,13,5].map(v=>(v+.5)/16),bay=(x,y)=>BAY[(y&3)*4+(x&3)];
const mix=(a,b,k)=>[lerp(a[0],b[0],k),lerp(a[1],b[1],k),lerp(a[2],b[2],k)];

/* ---------- the campfire's layout, in resting-window coordinates (add EXT for the painting) ---------- */
const FCX=476,FCY=458,RRX=168,RRY=47,BASEY=FCY-4;
const LEVELS=4,LF=[.6,.76,.9,1.04];
let COOL=[[12,15,22],[28,31,39],[40,43,50],[51,54,60],[63,66,73],[80,83,92],[102,104,113]];
const WARM=[[48,27,22],[84,47,32],[120,70,45],[156,98,62],[192,130,84],[222,164,110],[240,196,142]];
const FIREC=[null,[92,18,14],[150,32,16],[204,64,22],[236,112,32],[250,166,54],[254,214,104],[255,242,190]];
const FIRE_T=[0,8,12,17,22,28,33,38];
const fireCol=h=>{let i=0;while(i<7&&h>=FIRE_T[i+1])i++;return FIREC[i]};
const GX0=110,GY0=296,GX1=842,GY1=VIEWH;

/* ---------- DOM ---------- */
const $=s=>document.querySelector(s);
const layer=$('#fire'),cv=$('#fireCv'),cx=cv.getContext('2d',{alpha:false}),veil=$('#fireVeil'),hint=$('#fireHint');
const barA=$('#fireBar'),barB=$('#fireBar2'),care=$('#fireCare'),backMenu=$('#fBackMenu'),backBtn=$('#fBack');

/* ---------- building the scene, once ---------- */
const scenes={};let SC=null,bg=null,ground=[],stB=[],stF=[],stBox=null,logCv=null,logBox=null,cracks=[],coalCv=null,coalImg=null,coalPts=[],coalBox=null,shared=false;
let SMOKE_C=[74,80,104],LFK=1;
function build(key){
  if(!scenes[key])scenes[key]=new Promise(res=>{const im=new Image();im.onload=()=>{setTimeout(()=>{res(make(im))},0)};im.src=BURN_BG[key]});
  return scenes[key].then(sc=>{SC=sc;({bg,ground,stB,stF,stBox}=sc);COOL=sc.cool;SMOKE_C=sc.smoke;LFK=sc.lfk})}
function make(img){bg=img;ground=[];stB=[];stF=[];
  const o=document.createElement('canvas');o.width=PWD;o.height=VIEWH;const g=o.getContext('2d',{willReadFrequently:true});
  g.drawImage(bg,0,EXT,PWD,VIEWH,0,0,PWD,VIEWH);
  const D=g.getImageData(0,0,PWD,VIEWH).data,px=(x,y)=>{const i=(y*PWD+x)*4;return[D[i],D[i+1],D[i+2]]};
  const lumC=c=>c[0]*.3+c[1]*.59+c[2]*.11,rock=[];let amb=0,an=0;
  for(let y=300;y<VIEWH;y+=1)for(let x=0;x<PWD;x+=1){const c=px(x,y);if(Math.abs(x-FCX)<200&&y>380)continue;
    const L0=lumC(c);if(y>360){amb+=L0;an++}
    if(c[2]>c[1]+5&&L0>12&&Math.max(...c)-Math.min(...c)<70)rock.push(c)}   // painted boulders carry more blue than green; grass never does
  amb/=Math.max(1,an);
  // the painting's boulders are the lit, low-colour shapes in the grass; their middle tone anchors a full shading ramp
  rock.sort((a,b)=>lumC(a)-lumC(b));
  const anchor=rock.length>400?rock[Math.floor(rock.length*.72)]:[51,54,60];   // the lit faces of those boulders
  const cool=[.24,.55,.78,1,1.24,1.58,2].map(f=>anchor.map(v=>Math.min(255,Math.round(v*f))));
  COOL=cool;
  const lfk=clamp(1.3-amb/80,.5,1);LFK=lfk;
  let smoke=[74,80,104];
  {const t=document.createElement('canvas');t.width=PWD;t.height=240;const tg=t.getContext('2d',{willReadFrequently:true});tg.drawImage(img,0,EXT-280,PWD,240,0,0,PWD,240);
   const sd=tg.getImageData(0,0,PWD,240).data;let r=0,gg=0,b=0,n=0;for(let i=0;i<sd.length;i+=16){r+=sd[i];gg+=sd[i+1];b+=sd[i+2];n++}
   const avg=[r/n,gg/n,b/n];smoke=mix(avg.map(v=>Math.min(255,v*1.5+22)),[100,100,106],.45)}
  // stones: lumpy domes, lit cool from the sky and warm from the fire on whichever side faces it
  const stones=[],N=13;
  for(let k=0;k<N;k++){const ang=k/N*Math.PI*2+(hash(k,1)-.5)*.16+.12,s=Math.sin(ang),front=s>0,depth=(s+1)/2;
    stones.push({k,x:FCX+Math.cos(ang)*RRX+(hash(k,4)-.5)*8,y:FCY+s*RRY+(hash(k,5)-.5)*4,rw:21+depth*15+hash(k,2)*5,rh:13+depth*10+hash(k,3)*3,front,tone:(hash(k,6)-.5)*.16})}
  stones.sort((a,b)=>a.y-b.y);
  const pts=st=>{const out=[],dxf=FCX-st.x,dyf=(FCY-14)-st.y,dl=Math.hypot(dxf,dyf)||1,fx=dxf/dl,fy=dyf/dl;
    for(let y=Math.floor(st.y-st.rh*1.25);y<=st.y+st.rh;y++)for(let x=Math.floor(st.x-st.rw*1.1);x<=st.x+st.rw*1.1;x++){
      const u=(x-st.x)/st.rw,v=(y-st.y)/st.rh,an=Math.atan2(v,u),rm=1+(fbm(Math.cos(an)*1.7+st.k*3,Math.sin(an)*1.7+st.k)-.5)*.46;
      const vv=v<0?v*.82:v,d=Math.hypot(u,vv)/rm;if(d>1)continue;
      const nz=Math.sqrt(Math.max(0,1-d*d)),nx=u/rm,ny=vv/rm;
      out.push({x,y,v:vv,d,moon:clamp(nx*.22-ny*.78+nz*.55)*.9,fire:clamp(nx*fx+ny*fy*.85+nz*.28),
        mott:(fbm(x*.12+st.k*7,y*.15)-.5)*.3+(hash(x*3,y*5)-.5)*.1+st.tone,chip:hash(x*11+st.k,y*13)>.975})}
    return out};
  const all=stones.map(st=>({st,p:pts(st)}));
  let x0=1e9,y0=1e9,x1=-1,y1=-1;for(const s of all)for(const p of s.p){x0=Math.min(x0,p.x);y0=Math.min(y0,p.y);x1=Math.max(x1,p.x);y1=Math.max(y1,p.y)}
  stBox={x:x0,y:y0,w:x1-x0+1,h:y1-y0+1};
  for(let L=0;L<LEVELS;L++){const mk=()=>{const c=document.createElement('canvas');c.width=stBox.w;c.height=stBox.h;return c};
    const back=mk(),fr=mk(),bd=back.getContext('2d').createImageData(stBox.w,stBox.h),fd=fr.getContext('2d').createImageData(stBox.w,stBox.h);
    for(const {st,p:ps} of all){const tgt=st.front?fd:bd;
      for(const p of ps){const b=clamp(.04+p.moon*.52+p.mott),q=bay(p.x,p.y);let c=COOL[Math.min(6,Math.max(0,Math.floor(b*6.6+(q-.5)*.95)))];
        const w=p.fire*LF[L]*lfk*(st.front?.55:1.15),wq=Math.floor(clamp(w*1.05)*3+q*.999)/3;
        if(wq>0)c=mix(c,WARM[Math.min(6,Math.max(0,Math.floor(clamp(b*.55+w*.75)*6.6+(q-.5)*.9)))],Math.min(1,wq*1.15));
        if(p.chip)c=mix(c,[8,10,14],.7);
        if(p.d>.84&&p.v>0)c=[10,12,18];else if(p.d>.9&&p.v<-.35)c=mix(c,COOL[6],.35);
        const i=((p.y-stBox.y)*stBox.w+(p.x-stBox.x))*4;tgt.data[i]=c[0];tgt.data[i+1]=c[1];tgt.data[i+2]=c[2];tgt.data[i+3]=255}}
    back.getContext('2d').putImageData(bd,0,0);fr.getContext('2d').putImageData(fd,0,0);stB.push(back);stF.push(fr)}
  // the ground: dirt and ash inside the ring, shadows under the stones, firelight in dithered bands
  const base=[];for(let y=GY0;y<GY1;y++)for(let x=GX0;x<GX1;x++){let c=px(x,y);
    const dx=(x-FCX)/(RRX*.86),dy=(y-(FCY+3))/(RRY*.84),dd=dx*dx+dy*dy;
    if(dd<1.18){const f=fbm(x*.16,y*.3),dirt=f>.62?[40,33,30]:f>.44?[29,24,23]:[21,18,18];
      if(clamp((1.18-dd)/.22)>=bay(x,y))c=hash(x*7,y*3)>.955?[70,66,63]:hash(x*5,y*9)>.985?[96,90,84]:dirt}
    for(const st of stones)if(st.front){const sx=(x-st.x)/(st.rw*1.05),sy=(y-(st.y+st.rh*.62))/(st.rh*.55);if(sx*sx+sy*sy<1)c=c.map(v=>v*.5)}
    base.push(c)}
  for(let L=0;L<LEVELS;L++){const c=document.createElement('canvas');c.width=GX1-GX0;c.height=GY1-GY0;const gg=c.getContext('2d'),id=gg.createImageData(c.width,c.height);let n=0;
    for(let y=GY0;y<GY1;y++)for(let x=GX0;x<GX1;x++){const b=base[n],i=n*4;n++;
      const I=Math.min(.78,Math.pow(clamp(1-Math.hypot(x-FCX,(y-(FCY-6))*2.5)/330),1.7)*LF[L]*lfk),Iq=Math.floor(I*5+bay(x,y)*.999)/5;
      id.data[i]=b[0]*(1+Iq)+Iq*46;id.data[i+1]=b[1]*(1+Iq*.42)+Iq*17;id.data[i+2]=b[2]*(1+Iq*.06)+Iq*3;id.data[i+3]=255}
    gg.putImageData(id,0,0);ground.push(c)}
  if(shared)return{bg:img,ground,stB,stF,stBox,cool,smoke,lfk};shared=true;
  // coals: charcoal, some of it glowing
  coalBox={x:FCX-96,y:FCY-20,w:192,h:44};
  for(let y=FCY-20;y<FCY+24;y++)for(let x=FCX-96;x<FCX+96;x++){const dx=(x-FCX)/92,dy=(y-(FCY+2))/21;if(dx*dx+dy*dy>1)continue;
    if(fbm(x*.5+3,y*.8)<.32)continue;coalPts.push({i:((y-coalBox.y)*coalBox.w+(x-coalBox.x))*4,h:fbm(x*.21,y*.38)*(1-Math.min(1,dx*dx+dy*dy)*.55),ph:hash(x,y)*6.28})}
  coalCv=document.createElement('canvas');coalCv.width=coalBox.w;coalCv.height=coalBox.h;coalImg=coalCv.getContext('2d').createImageData(coalBox.w,coalBox.h);
  // logs: barked, charred where they meet the fire, cracks that glow
  logBox={x:360,y:420,w:240,h:90};logCv=document.createElement('canvas');logCv.width=logBox.w;logCv.height=logBox.h;
  const ld=logCv.getContext('2d').createImageData(logBox.w,logBox.h);
  for(const [ax,ay,bx,by,th] of [[398,452,546,468,10],[388,488,540,446,13],[566,490,414,447,13]]){const Lg=Math.hypot(bx-ax,by-ay),ux=(bx-ax)/Lg,uy=(by-ay)/Lg,nx=-uy,ny=ux;
    for(let s=-2;s<=Lg+2;s+=.5)for(let o2=-th/2;o2<=th/2;o2+=.5){const endR=Math.min(s,Lg-s);if(endR<0)continue;if(endR<th/2&&Math.hypot(th/2-endR,o2)>th/2)continue;
      const x=Math.round(ax+ux*s+nx*o2),y=Math.round(ay+uy*s+ny*o2),w=(o2+th/2)/th,near=1-clamp(Math.hypot(x-FCX,(y-FCY)*1.6)/86),q=bay(x,y);
      const ring=hash(Math.round(s/5),ay)>.55;let c=w<.22?[138,100,66]:w<.5?(ring?[84,56,36]:[112,78,50]):w<.8?[84,56,36]:[48,32,22];
      if(hash(Math.round(s*1.3),Math.round(o2*2))>.9)c=[58,38,26];
      if(near*1.25>q){c=w<.3?[52,42,40]:w<.75?[30,24,23]:[17,14,14];if(near>.35&&hash(Math.round(s/2.2),Math.round(o2))>.84&&w>.12&&w<.88)cracks.push({x,y,ph:hash(x,y)*6.28,k:near})}
      if(endR<1.2&&s>Lg/2)c=[40,30,26];
      const lx=x-logBox.x,ly=y-logBox.y;if(lx<0||ly<0||lx>=logBox.w||ly>=logBox.h)continue;
      const i=(ly*logBox.w+lx)*4;ld.data[i]=c[0];ld.data[i+1]=c[1];ld.data[i+2]=c[2];ld.data[i+3]=255}}
  logCv.getContext('2d').putImageData(ld,0,0);
  return{bg:img,ground,stB,stF,stBox,cool,smoke,lfk}}

/* ---------- flames: a heat simulation at half resolution, as chunky as the painting ---------- */
const CELL=2,FX=296,FY=EXT+BASEY-372,SW=180,SH=190,BROW=((EXT+BASEY-FY)/CELL)|0;
const heat=new Float32Array(SW*SH),fcv=document.createElement('canvas');fcv.width=SW;fcv.height=SH;const fctx=fcv.getContext('2d'),fimg=fctx.createImageData(SW,SH);
const SOURCES=[[-38,.62,1.7],[-22,.84,2.3],[-6,1,1.9],[9,.96,2.6],[24,.82,2.1],[39,.6,1.5]];
function seedFire(t,boost){for(let c=0;c<SW;c++){const wx=FX+c*CELL-FCX;let h=0;
    for(const [off,amp,sp] of SOURCES){const sx=off+Math.sin(t*.7+off)*5,d=(wx-sx)/10;h=Math.max(h,amp*Math.exp(-d*d)*(.78+.22*Math.sin(t*sp+off)))}
    const bed=Math.abs(wx)<74?(.24+.2*fbm(c*.3,t*2.6)):0,v=Math.max(h*44,bed*30)*boost*(.86+.14*FLICK)+rnd()*3;
    heat[BROW*SW+c]=v;heat[(BROW+1)*SW+c]=v}}
function fireStep(t){const wind=Math.sin(t*.55)*.12+Math.sin(t*1.7)*.05;
  for(let y=1;y<SH;y++)for(let x=1;x<SW-1;x++){const s=y*SW+x,v=heat[s];if(v<=0&&heat[s-SW]<=0)continue;
    const r=rnd(),dx=r<.27+wind?-1:r<.73+wind?0:1;heat[(y-1)*SW+Math.max(0,Math.min(SW-1,x+dx))]=Math.max(0,v-(.38+rnd()*.82))}}
function paintFire(){const d=fimg.data;for(let i=0;i<SW*SH;i++){const c=fireCol(heat[i]);if(!c){d[i*4+3]=0;continue}d[i*4]=c[0];d[i*4+1]=c[1];d[i*4+2]=c[2];d[i*4+3]=255}fctx.putImageData(fimg,0,0)}
const heatAt=(x,y)=>{const c=((x-FX)/CELL)|0,r=((y-FY)/CELL)|0;return(c<0||r<0||c>=SW||r>=SH)?0:heat[r*SW+c]};
const addHeat=(x,y,v)=>{const c=((x-FX)/CELL)|0,r=((y-FY)/CELL)|0;if(c>0&&r>0&&c<SW&&r<SH)heat[r*SW+c]=Math.max(heat[r*SW+c],v)};

/* ---------- the page: your words, on a torn, ruled sheet ---------- */
const PW=134,PH=168,paper=new Int16Array(PW*PH*3),pmask=new Uint8Array(PW*PH),isInk=new Uint8Array(PW*PH);
const pcv=document.createElement('canvas');pcv.width=PW;pcv.height=PH;const pctx=pcv.getContext('2d'),pimg=pctx.createImageData(PW,PH);
const burnB=new Float32Array(PW*PH),gone=new Uint8Array(PW*PH);
function makePage(text){pmask.fill(0);isInk.fill(0);
  // the writing: drawn small, then snapped to whole pixels so it reads as ink on a page, not screen text
  const tc=document.createElement('canvas');tc.width=PW;tc.height=PH;const tg=tc.getContext('2d',{willReadFrequently:true});
  tg.fillStyle='#000';tg.font='italic 9px Newsreader, Georgia, serif';tg.textBaseline='alphabetic';
  const words=text.replace(/\s+/g,' ').trim().split(' '),maxW=PW-30,lines=[];let cur='';
  for(const w of words){const t=cur?cur+' '+w:w;if(tg.measureText(t).width>maxW&&cur){lines.push(cur);cur=w}else cur=t;if(lines.length>=10)break}
  if(lines.length<10&&cur)lines.push(cur);
  if(lines.length>=10&&words.join(' ').length>lines.join(' ').length){let l=lines[9];while(l&&tg.measureText(l+'…').width>maxW)l=l.slice(0,-1);lines[9]=l+'…'}
  lines.slice(0,10).forEach((l,i)=>tg.fillText(l,24,33+i*13));
  const ink=tg.getImageData(0,0,PW,PH).data;
  for(let v=0;v<PH;v++)for(let u=0;u<PW;u++){const j=v*PW+u,tear=2+fbm(u*.22,40)*6+(hash(u,41)>.8?2:0);if(v<tear)continue;pmask[j]=1;
    const n=hash(u*3,v*5)*6+fbm(u*.08,v*.08)*10,edge=Math.min(u,PW-1-u,v-tear,PH-1-v);
    let c=[214+n*.4-8,202+n*.4-8,174+n*.4-6];if(edge<3)c=c.map(x=>x-14);
    if(v>22&&(v-22)%13===0)c=[168,172,188];if(u===19||u===20)c=[178,106,100];
    if(ink[j*4+3]>105){c=[54,48,72];isInk[j]=1}
    paper[j*3]=c[0];paper[j*3+1]=c[1];paper[j*3+2]=c[2]}}
function seedBurn(su,sv){let M=0;
  for(let v=0;v<PH;v++)for(let u=0;u<PW;u++){const j=v*PW+u;if(!pmask[j]){burnB[j]=9;continue}
    const dx=u-su,dy=v-sv,dyc=dy<0?dy*.52:dy*1.5,d=Math.sqrt(dx*dx+dyc*dyc)+(fbm(u*.045,v*.045)-.5)*30+(fbm(u*.16,v*.16)-.5)*8;burnB[j]=d;if(d>M)M=d}
  for(let j=0;j<PW*PH;j++)if(pmask[j])burnB[j]=Math.max(0,burnB[j])/M}
const SCORCH=.13,EDGE=.016,CHAR=.062,RIM=.012,BURN_DUR=6.6;

/* ---------- view: always fills the screen; tall screens see more of the tall painting ---------- */
let VW=952,VH=536,camL=0,camT=EXT,restT=EXT,endT=190;
const smk=document.createElement('canvas'),smx=smk.getContext('2d');let smImg=null;
const gA=document.createElement('canvas'),gB=document.createElement('canvas'),ga=gA.getContext('2d'),gb=gB.getContext('2d');
const FILTER_OK=(()=>{try{ga.filter='blur(1px)';const ok=ga.filter==='blur(1px)';ga.filter='none';return ok}catch(e){return false}})();
function sizeView(){const a=innerWidth/Math.max(1,innerHeight);
  if(a>=PWD/VIEWH){VW=PWD;VH=Math.round(PWD/a)}else{VH=VIEWH;VW=Math.round(VIEWH*a);if(VW<540){VW=540;VH=Math.min(FULLH,Math.round(540/a))}}
  cv.width=VW;cv.height=VH;cx.imageSmoothingEnabled=false;
  camL=clamp(FCX-VW/2,0,PWD-VW);restT=clamp(EXT+VIEWH-VH,0,FULLH-VH);endT=Math.max(0,Math.min(restT-260,190-(VH-VIEWH)));
  smk.width=Math.ceil(VW/2);smk.height=Math.ceil(VH/2);smImg=smx.createImageData(smk.width,smk.height);
  gA.width=gB.width=Math.ceil(VW/2);gA.height=gB.height=Math.ceil(VH/2)}

/* ---------- state ---------- */
let active=false,phase='arrive',P,heldAt,flakes,sparks,smoke,T,burnt,tCatch,panT,doneT,drag=false,grab=[0,0],FLICK=.6,onExit=null,sitting=false,showT=0,hintDone=false;
const HOLD_Y=()=>EXT+BASEY-212,AWAY_Y=()=>camT+VH+PH;
function resetSim(){seed=5;heat.fill(0);gone.fill(0);heldAt=new Float32Array(16);flakes=[];sparks=[];smoke=[];T=0;burnt=0;tCatch=0;panT=-1;doneT=-1;drag=false;
  P={x:FCX,y:EXT+VIEWH+200,a:-.05,tx:FCX,ty:EXT+VIEWH+200}}
function toWorld(u,v){const c=Math.cos(P.a),s=Math.sin(P.a),lx=u-PW/2,ly=v-PH/2;return[P.x+lx*c-ly*s,P.y+lx*s+ly*c]}
const frontAt=t=>phase==='caught'||phase==='rising'?Math.pow(clamp((t-tCatch)/BURN_DUR),1.7)*(1+EDGE+CHAR+RIM):-9;
const DT=1/30;
function step(){T+=DT;const t=T;
  FLICK=clamp(.5+.38*Math.sin(t*6.7)*Math.sin(t*3.9+1)+.3*(fbm(t*2.6,2)-.5)+(phase==='caught'&&burnt<.95?.18:0));
  seedFire(t,phase==='caught'&&burnt<.95?1.12:1);fireStep(t);
  const out=phase==='out'||phase==='stowing'||phase==='caught'||phase==='rising';
  if(phase==='out'){P.tx=clamp(P.tx,camL+PW*.45,camL+VW-PW*.45);P.ty=clamp(P.ty,camT+PH*.45,camT+VH-PH*.3)}
  if(out){P.x+=(P.tx-P.x)*.16;P.y+=(P.ty-P.y)*.16;P.a=lerp(P.a,-.05+Math.sin(t*.8)*.02+(P.tx-P.x)*.0016,.2)}
  if(phase==='stowing'&&P.y>camT+VH+PH*.6){phase='arrive';showBars()}
  if(phase==='out'){let best=-1,bi=0;   // the edge nearest the flames soaks up heat until it takes; pull away in time and it cools
    for(let i=0;i<16;i++){const u=10+i*((PW-20)/15),[wx,wy]=toWorld(u,PH-3),h=heatAt(wx,wy)+heatAt(wx,wy-6)*.5;
      heldAt[i]=Math.max(0,heldAt[i]+(h>10?h*DT*.5:-DT*5));if(heldAt[i]>best){best=heldAt[i];bi=i}}
    if(best>5){phase='caught';tCatch=t;seedBurn(10+bi*((PW-20)/15),PH-6);drag=false;cv.classList.remove('held');hideBars()}}
  if(phase==='caught'||phase==='rising'){const front=frontAt(t);let gn=0,tot=0;
    for(let v=0;v<PH;v++)for(let u=0;u<PW;u++){const j=v*PW+u;if(!pmask[j])continue;tot++;if(gone[j]){gn++;continue}const d=burnB[j]-front;
      if(d<=0&&d>-EDGE){if(rnd()<.2){const [wx,wy]=toWorld(u,v);addHeat(wx,wy,12+rnd()*16)}}
      else if(d<=-EDGE-CHAR-RIM){gone[j]=1;if(rnd()<.045){const [wx,wy]=toWorld(u,v);
        flakes.push({x:wx,y:wy,vx:(rnd()-.5)*14,vy:-(14+rnd()*26),t0:t,life:2.4+rnd()*3,ph:rnd()*6.3,glow:rnd()<.5,big:rnd()<.45})}}}
    burnt=gn/tot;P.y-=DT*5*burnt;P.a+=Math.sin(t*1.3)*.0025*burnt;
    if(burnt>.93&&panT<0){panT=t+.5;phase='rising'}}
  for(const f of flakes){const a=t-f.t0;f.vy+=(a<.9?-5:3)*DT;f.vx+=Math.sin(t*1.6+f.ph)*9*DT;f.x+=f.vx*DT;f.y+=f.vy*DT}
  flakes=flakes.filter(f=>t-f.t0<f.life&&f.y>-40);
  if(rnd()<(phase==='caught'?.6:.36))sparks.push({x:FCX+(rnd()-.5)*90,y:EXT+BASEY-30-rnd()*40,vx:(rnd()-.5)*16,vy:-(50+rnd()*46),t0:t,life:.7+rnd()*.9,ph:rnd()*6});
  for(const s of sparks){s.x+=(s.vx+Math.sin(t*12+s.ph)*18)*DT;s.y+=s.vy*DT;s.vy*=.985}
  sparks=sparks.filter(s=>t-s.t0<s.life);
  const burning=phase==='caught'||phase==='rising';
  if(rnd()<.14+(burning?.8:0)){let pt=null;
    if(burning&&burnt<.99){const front=frontAt(t);for(let k=0;k<40&&!pt;k++){const u=(rnd()*PW)|0,v=(rnd()*PH)|0,j=v*PW+u;
      if(pmask[j]&&!gone[j]&&burnB[j]-front<.01&&burnB[j]-front>-EDGE-CHAR)pt=toWorld(u,v-6)}}
    const [sx,sy]=pt||[FCX-24+rnd()*48,EXT+BASEY-104];
    smoke.push({x:sx,y:sy,r:6+rnd()*6,t0:t,life:10+rnd()*4,vx:1.5+rnd()*3.5,vy:-(34+rnd()*18),ph:rnd()*6.3})}
  for(const s of smoke){s.x+=(s.vx+Math.sin(t*.55+s.ph)*4)*DT;s.vy*=1.004;s.y+=s.vy*DT;s.r+=DT*(s.y<EXT?7:4.4)}
  smoke=smoke.filter(s=>t-s.t0<s.life&&s.y>-60);
  if(phase==='rising'&&doneT<0&&t>panT+(reducedMotion?1.6:7.1))doneT=t;
  camT=phase==='rising'&&!reducedMotion?Math.round(lerp(restT,endT,ease(clamp((t-panT)/5.8)))):restT}
const fadeK=t=>phase!=='rising'?1:1-ease(clamp((t-panT-(reducedMotion?.2:5.6))/(reducedMotion?1.2:1.4)));

/* ---------- drawing ---------- */
function paintPaper(t){const d=pimg.data,front=frontAt(t),burning=phase==='caught'||phase==='rising';
  for(let v=0;v<PH;v++)for(let u=0;u<PW;u++){const j=v*PW+u,i=j*4;if(!pmask[j]||gone[j]){d[i+3]=0;continue}
    const dd=burnB[j]-front,under=clamp((v/PH-.35)*1.7)*(.7+.3*FLICK),base=[paper[j*3],paper[j*3+1],paper[j*3+2]];
    const hk=burning?0:clamp((heldAt[Math.min(15,Math.max(0,Math.round((u-10)/((PW-20)/15))))]||0)/7)*.5;let c;
    if(!burning||dd>SCORCH)c=isInk[j]?base:[lerp(base[0],204,hk)+under*20,lerp(base[1],168,hk)+under*5,lerp(base[2],118,hk)-under*24];
    else if(dd>0){const k=1-dd/SCORCH,m=ease(clamp(k*1.4)),s=k<.4?[204,170,118]:k<.72?[148,96,50]:[94,50,26];c=isInk[j]?[60,50,58]:mix(base,s,m)}
    else if(dd>-EDGE){const f=fbm(u*.22+t*6,v*.22);c=f>.62?[255,242,190]:f>.45?[250,166,54]:[204,64,22]}
    else if(dd>-EDGE-CHAR){const k=(-dd-EDGE)/CHAR,vein=fbm(u*.24+t*1.4,v*.24-t)>.68-k*.18&&k<.75;c=vein?(k<.35?[236,112,32]:[150,32,16]):(k<.55?[32,25,23]:[17,13,13])}
    else c=hash(u+Math.floor(t*6),v)>.35?[172,166,160]:[88,84,82];
    d[i]=c[0];d[i+1]=c[1];d[i+2]=c[2];d[i+3]=255}
  pctx.putImageData(pimg,0,0)}
function paintSmoke(t){const d=smImg.data;d.fill(0);const W2=smk.width,H2=smk.height;
  for(const s of smoke){const a=(t-s.t0)/s.life,dens=Math.sin(Math.min(1,a*4)*Math.PI/2)*Math.pow(1-a,1.3)*.9;
    const cx2=(s.x-camL)/2,cy2=(s.y-camT)/2,r2=s.r/2;
    for(let y=Math.max(0,(cy2-r2)|0);y<=Math.min(H2-1,(cy2+r2)|0);y++)for(let x=Math.max(0,(cx2-r2)|0);x<=Math.min(W2-1,(cx2+r2)|0);x++){
      const q=Math.hypot(x-cx2,y-cy2)/r2;if(q>1)continue;const wx=x*2+camL,wy=y*2+camT;
      if(dens*(1-q*q)+(fbm(wx*.055,wy*.055-t*.4)-.5)*.5<bay(x,y))continue;
      const warm=clamp((wy-(EXT+150))/240),i=(y*W2+x)*4;d[i]=lerp(SMOKE_C[0],110,warm);d[i+1]=lerp(SMOKE_C[1],98,warm);d[i+2]=lerp(SMOKE_C[2],98,warm);d[i+3]=150}}
  smx.putImageData(smImg,0,0)}
function postFX(){const w=gA.width,h=gA.height;
  ga.globalCompositeOperation='copy';ga.imageSmoothingEnabled=true;if(FILTER_OK)ga.filter='brightness(1.05) contrast(1.8)';ga.drawImage(cv,0,0,w,h);ga.filter='none';
  ga.globalCompositeOperation='multiply';ga.drawImage(gA,0,0);ga.globalCompositeOperation='source-over';
  gb.globalCompositeOperation='copy';gb.imageSmoothingEnabled=true;
  if(FILTER_OK){gb.filter='blur(3.5px)';gb.drawImage(gA,0,0);gb.filter='none'}else{gb.drawImage(gA,0,0,w/6,h/6);gb.drawImage(gB,0,0,w/6,h/6,0,0,w,h)}
  gb.globalCompositeOperation='source-over';
  cx.save();cx.globalCompositeOperation='screen';cx.globalAlpha=.34;cx.imageSmoothingEnabled=true;cx.drawImage(gB,0,0,VW,VH);cx.restore();cx.imageSmoothingEnabled=false;
  cx.save();cx.translate(VW/2,VH*.48);cx.scale(1.2*VW,1.1*VH);const vg=cx.createRadialGradient(0,0,0,0,0,1);vg.addColorStop(.4,'rgba(0,0,0,0)');vg.addColorStop(1,'rgba(0,0,0,.8)');
  cx.fillStyle=vg;cx.fillRect(-1,-1,2,2);cx.restore()}
function render(){const t=T,L=Math.min(LEVELS-1,Math.floor(FLICK*LEVELS*.999));
  cx.setTransform(1,0,0,1,-camL,-camT);
  cx.drawImage(bg,0,0);
  cx.drawImage(ground[L],GX0,EXT+GY0);
  cx.drawImage(stB[L],stBox.x,EXT+stBox.y);
  {const d=coalImg.data;for(const c of coalPts){const g=c.h+FLICK*.28+Math.sin(t*1.3+c.ph)*.1-.36;
      const col=g<.05?[26,20,20]:g<.16?[42,32,30]:g<.27?[120,24,14]:g<.38?[194,62,20]:g<.48?[236,116,32]:[252,196,88];
      d[c.i]=col[0];d[c.i+1]=col[1];d[c.i+2]=col[2];d[c.i+3]=255}
    coalCv.getContext('2d').putImageData(coalImg,0,0);cx.drawImage(coalCv,coalBox.x,EXT+coalBox.y)}
  cx.drawImage(logCv,logBox.x,EXT+logBox.y);
  for(const k of cracks){const g=k.k*.7+FLICK*.35+Math.sin(t*1.9+k.ph)*.14;cx.fillStyle=g<.45?'#5a160e':g<.65?'#b4320f':g<.85?'#ec7420':'#fcc458';cx.fillRect(k.x,EXT+k.y,1,1)}
  paintSmoke(t);cx.drawImage(smk,camL,camT,smk.width*2,smk.height*2);
  paintFire();cx.drawImage(fcv,FX,FY,SW*CELL,SH*CELL);
  cx.drawImage(stF[L],stBox.x,EXT+stBox.y);
  if(phase!=='arrive'&&burnt<.999){paintPaper(t);cx.save();cx.translate(P.x,P.y);cx.rotate(P.a);cx.drawImage(pcv,-PW/2,-PH/2);cx.restore()}
  for(const s of sparks){const a=(t-s.t0)/s.life;cx.fillStyle=a<.4?'#fff2be':a<.75?'#faa636':'#962010';cx.fillRect(s.x|0,s.y|0,1,1)}
  for(const f of flakes){const a=(t-f.t0)/f.life,x=f.x|0,y=f.y|0;if(a>.8&&((x+y+Math.floor(t*8))&1))continue;
    cx.fillStyle=f.glow&&a<.5?(a<.18?'#fed668':a<.32?'#ec7020':'#68120a'):(a<.6?'#221917':'#40424e');
    cx.fillRect(x,y,1,1);if(f.big){const fl=Math.sin(t*9+f.ph)>0;cx.fillRect(fl?x+1:x,fl?y:y+1,1,1)}}
  cx.setTransform(1,0,0,1,0,0);postFX();
  const fk=fadeK(t);if(fk<1){cx.fillStyle=`rgba(4,5,9,${1-fk})`;cx.fillRect(0,0,VW,VH)}}

/* ---------- loop: steps at 12 a second, like the camp ---------- */
let start=0,last=-1,raf=0;
function tick(now){if(!active)return;if(!start)start=now-T*1000;const t=(now-start)/1000,f=Math.floor(t*12);
  if(f!==last){last=f;while(T+DT<=t)step();render()}
  if(doneT>0&&T>doneT+.2){finish('burned');return}
  raf=requestAnimationFrame(tick)}

/* ---------- the choices ---------- */
function showBars(){barB.hidden=phase!=='out';barA.hidden=phase!=='arrive'||!care.hidden;layer.dataset.ui='on'}
function hideBars(){barA.hidden=true;barB.hidden=true;hint.dataset.show='false';closeBack()}
function say(msg){hint.textContent=msg;hint.dataset.show='true'}
function takeOut(){if(phase!=='arrive'||!P||!SC)return;sit(false);phase='out';P.x=P.tx=FCX;P.y=camT+VH+PH;P.ty=HOLD_Y();P.a=-.05;showBars();
  if(!hintDone)setTimeout(()=>{if(phase==='out'&&!hintDone)say('Hold it over the fire. Pull it away and it won’t catch.')},700);
  setTimeout(()=>{try{$('#fPut').focus({preventScroll:true})}catch(e){}},50)}
function stow(){if(phase!=='out')return;phase='stowing';P.ty=camT+VH+PH*1.2;hint.dataset.show='false';barB.hidden=true}
function lower(){if(phase!=='out')return;hintDone=true;hint.dataset.show='false';P.tx=FCX+(rnd()-.5)*30;P.ty=EXT+BASEY-150}   // for keyboards, and anyone who'd rather not drag
function sit(on){sitting=on;layer.dataset.sit=on?'1':'';if(on){closeBack();hint.dataset.show='false'}}
function openBack(){backMenu.hidden=false;backBtn.setAttribute('aria-expanded','true');try{$('#fInside').focus()}catch(e){}}
function closeBack(){backMenu.hidden=true;backBtn.setAttribute('aria-expanded','false')}
function leave(where){if(!active||phase==='leaving')return;phase='leaving';hideBars();veil.style.opacity='1';setTimeout(()=>finish(where),reducedMotion?60:620)}
function finish(where){active=false;cancelAnimationFrame(raf);veil.style.opacity='1';const cb=onExit;onExit=null;if(cb)cb(where)}
function hide(){layer.style.opacity='0';setTimeout(()=>{layer.hidden=true;layer.style.opacity='';delete layer.dataset.sit},reducedMotion?60:900)}

$('#fTake').addEventListener('click',takeOut);
$('#fSit').addEventListener('click',()=>sit(true));
$('#fPut').addEventListener('click',stow);
$('#fLower').addEventListener('click',lower);
backBtn.addEventListener('click',e=>{e.stopPropagation();backMenu.hidden?openBack():closeBack()});
$('#fInside').addEventListener('click',()=>leave('inside'));
$('#fCamp').addEventListener('click',()=>leave('camp'));
$('#fCareGo').addEventListener('click',()=>{care.hidden=true;showBars()});
$('#fCareBack').addEventListener('click',()=>leave('inside'));
layer.addEventListener('pointerdown',e=>{if(!backMenu.hidden&&!e.target.closest('.fback'))closeBack();if(sitting){sit(false);e.preventDefault()}},true);
function toW(e){const r=cv.getBoundingClientRect(),s=Math.max(r.width/VW,r.height/VH),ox=(r.width-VW*s)/2,oy=(r.height-VH*s)/2;return[(e.clientX-r.left-ox)/s+camL,(e.clientY-r.top-oy)/s+camT]}
cv.addEventListener('pointerdown',e=>{if(phase!=='out')return;const [x,y]=toW(e);grab=[P.x-x,P.y-y];drag=true;hintDone=true;hint.dataset.show='false';cv.classList.add('held');try{cv.setPointerCapture(e.pointerId)}catch(_){}});
cv.addEventListener('pointermove',e=>{if(!drag||phase!=='out')return;const [x,y]=toW(e);P.tx=x+grab[0];P.ty=y+grab[1]});
const up=()=>{drag=false;cv.classList.remove('held')};cv.addEventListener('pointerup',up);cv.addEventListener('pointercancel',up);
addEventListener('keydown',e=>{if(!active)return;
  if(e.key==='Escape'){e.stopImmediatePropagation();e.preventDefault();
    if(!backMenu.hidden)closeBack();else if(sitting)sit(false);else if(phase==='out')stow();else if(phase==='arrive')leave('inside');return}
  if(phase==='out'&&/^Arrow/.test(e.key)&&!e.target.closest('button')){e.preventDefault();const s=e.shiftKey?40:16;
    if(e.key==='ArrowLeft')P.tx-=s;if(e.key==='ArrowRight')P.tx+=s;if(e.key==='ArrowUp')P.ty-=s;if(e.key==='ArrowDown')P.ty+=s;hintDone=true;hint.dataset.show='false'}},true);
addEventListener('resize',()=>{if(active&&phase!=='rising'){sizeView();camT=restT}});

return{
  get active(){return active},
  open(o){if(active)return;onExit=o.onExit;active=true;phase='arrive';sitting=false;hintDone=false;delete layer.dataset.sit;
    layer.hidden=false;layer.style.opacity='1';veil.style.transition='none';veil.style.opacity='1';hideBars();care.hidden=!o.concern;
    build(BURN_BG[o.time]?o.time:'night').then(()=>{if(!active)return;sizeView();resetSim();makePage(o.text||'');camT=restT;
      for(let i=0;i<45;i++)step();             // let the fire get going before the veil lifts
      start=0;last=-1;render();raf=requestAnimationFrame(tick);
      requestAnimationFrame(()=>{veil.style.transition='';veil.style.opacity='0';setTimeout(()=>{if(active&&phase==='arrive'){showBars();if(o.concern)try{$('#fCareGo').focus()}catch(e){}else try{$('#fTake').focus({preventScroll:true})}catch(e){}}},reducedMotion?60:900)})})},
  hide};
})();
