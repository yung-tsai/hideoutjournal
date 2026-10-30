"""Scene frames and their unlocks (after the sidebar).
   - Settings > Frame picks how the postcard is framed: Rounded corners (the default) and Postcard (the deckled edge) are always
     there; Stamp opens at 5 entries, Sketch line and the rubber van window at 10, the riveted metal window at 20, the wood window
     and Dreamy at 50. It counts every entry ever saved (never streaks), and once a frame opens it stays open (state.meta.framesUnlocked).
   - The image area is the same for every frame; borders sit outside it (pcLayout leaves room for them) and every frame is drawn
     in code, SVG or a pixel-aligned canvas, so it's crisp at any size. #pcBack (under the scene) holds shadows and stamp paper,
     #pcFront (over it) holds bezels, rivets, sketch lines and Dreamy's dither.
   - Locked frames show faded with a quiet "After N entries". When one opens, a short note waits in Settings the next time it's opened.
   - The field sits a short way under the card (dockLift; the expanded writing card keeps its place); the wordmark sits a little lower.
   - FRAMES_TEST_ALL unlocks every frame (off). Dev hook: __frames.set(k), __frames.testAll(on).
   python3 frames.py <in.html> <out.html>"""
import sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n: sys.exit(f'frames.py: expected {n} got {c}: {a[:90]!r}')
    s = s.replace(a, b)

# ---------- the card leaves room for the frame ----------
rep("fit=Math.min(Math.max(200,W-32)/AW,Math.max(120,H-top-bottom)/AH)",
    "fit=Math.min(Math.max(200,W-32)/AW/(1+2*pcF()),Math.max(120,H-top-bottom)/AH/(1+3.6*pcF()))")
rep("const y=Math.round((top+Math.max(0,(H-top-bottom-h-70)*.42))*dpr)/dpr;",
    "const y=Math.round((top+pcF()*w+Math.max(0,(H-top-bottom-h-2*pcF()*w-70)*.42))*dpr)/dpr;")
rep("k=Math.min(1,room/w)", "k=Math.min(1,room/(w*(1+2*pcF())))")
rep("clip-path:inset(2px);", "")
rep("top:calc(var(--pc-top,84px) + var(--pc-h,536px) + 16px)", "top:calc(var(--pc-top,84px) + var(--pc-h,536px) + var(--pcft,0px) + 16px)")
rep("g.globalAlpha=+st.opacity;", "g.globalAlpha=+st.opacity;c.style.clipPath=getComputedStyle(L).clipPath;")   # the crossfade still keeps the frame's corners

# ---------- Settings: the Frame section, after Scene; the page switch gets a plainer name ----------
rep('<div><b>Postcard frame</b><span>Shows your scene as a framed print on a light page.</span></div><button class="switch" type="button" role="switch" id="setFrame" aria-label="Postcard frame"></button></div>\n      </section>',
    '<div><b>Scene on the page</b><span>Off lets the scene fill the screen.</span></div><button class="switch" type="button" role="switch" id="setFrame" aria-label="Scene on the page"></button></div>\n      </section>\n'
    '      <section class="sgroup" id="frameGroup"><h3>Frame</h3><p class="frnote" id="frameNote" hidden></p><div class="frgrid" id="setFrameKind" role="group" aria-label="Frame"></div></section>')

# ---------- behaviour ----------
rep("let meadowOn=false;", r"""/* ---------- scene frames ---------- */
var FRAMES_TEST_ALL=false;   // TEST: unlock every frame
var FRAMES=[{k:'rounded',l:'Rounded',at:0},{k:'postcard',l:'Postcard',at:0},{k:'stamp',l:'Stamp',at:5},{k:'sketch',l:'Sketch line',at:10},
  {k:'rubber',l:'Rubber window',at:10},{k:'metal',l:'Riveted window',at:20},{k:'wood',l:'Wood window',at:50},{k:'dreamy',l:'Dreamy',at:50}];
var FR_T={stamp:.03,sketch:.012,rubber:.034,metal:.036,wood:.036};   // how far the frame reaches outside the picture, as a share of its width
function frameUnlocked(k){const f=(FRAMES||[]).find(x=>x.k===k);return !!f&&(FRAMES_TEST_ALL||!f.at||((state.meta.framesUnlocked||[]).includes(k)))}
function frameOn(){const k=state.settings.pcFrame;return k&&frameUnlocked(k)?k:'rounded'}
function pcF(){if(typeof FR_T==='undefined'||!FR_T||document.body.dataset.frame!=='postcard')return 0;return FR_T[frameOn()]||0}
function frameCheck(){const n=state.entries.length,u=state.meta.framesUnlocked||(state.meta.framesUnlocked=[]);let ch=false;
  for(const f of FRAMES)if(f.at&&n>=f.at&&!u.includes(f.k)){u.push(f.k);ch=true}return ch}
{const _p=persist;persist=function(){if(frameCheck()&&renderFrames.on)renderFrames();_p()}}
/* drawing: everything in CSS pixels around the picture at (M,M,w,h) */
function rrP(x,y,w,h,r){r=Math.max(0,Math.min(r,w/2,h/2));return `M${x+r} ${y}H${x+w-r}A${r} ${r} 0 0 1 ${x+w} ${y+r}V${y+h-r}A${r} ${r} 0 0 1 ${x+w-r} ${y+h}H${x+r}A${r} ${r} 0 0 1 ${x} ${y+h-r}V${y+r}A${r} ${r} 0 0 1 ${x+r} ${y}Z`}
function rrAt(x,y,w,h,r,t){   // a point (and its outward normal) at distance t along a rounded rectangle, clockwise from the top-left
  const a=w-2*r,b=h-2*r,c=Math.PI*r/2,P=2*a+2*b+4*c;t=((t%P)+P)%P;
  const arc=(cx,cy,a0,u)=>{const g=a0+u/r;return[cx+r*Math.cos(g),cy+r*Math.sin(g),Math.cos(g),Math.sin(g)]};
  if(t<a)return[x+r+t,y,0,-1];t-=a;if(t<c)return arc(x+w-r,y+r,-Math.PI/2,t);t-=c;
  if(t<b)return[x+w,y+r+t,1,0];t-=b;if(t<c)return arc(x+w-r,y+h-r,0,t);t-=c;
  if(t<a)return[x+w-r-t,y+h,0,1];t-=a;if(t<c)return arc(x+r,y+h-r,Math.PI/2,t);t-=c;
  if(t<b)return[x,y+h-r-t,-1,0];t-=b;return arc(x+r,y+r,Math.PI,t)}
function frameRadius(k,w,q){return k==='rounded'?Math.max(7,14*q):k==='sketch'?Math.max(6,12*q):k==='rubber'||k==='metal'||k==='wood'?w*.055:0}
function frameSVG(k,w,h,M,u,q){   // -> {back, front}: SVG markup (no <svg> wrapper) for under and over the picture
  const t=(FR_T[k]||0)*w,X=M-t,Y=M-t,OW=w+2*t,OH=h+2*t,ri=frameRadius(k,w,q),ro=ri+t*.9,out={back:'',front:''};
  if(k==='rounded'){
    out.back=`<defs><filter id="${u}b" x="-10%" y="-10%" width="120%" height="130%"><feGaussianBlur stdDeviation="${11*q}"/></filter><filter id="${u}c" x="-5%" y="-5%" width="110%" height="115%"><feGaussianBlur stdDeviation="${2.5*q}"/></filter></defs>`+
      `<path d="${rrP(M,M+8*q,w,h,ri)}" fill="rgba(30,38,34,.13)" filter="url(#${u}b)"/><path d="${rrP(M,M+1.5*q,w,h,ri)}" fill="rgba(30,38,34,.10)" filter="url(#${u}c)"/>`}
  else if(k==='stamp'){
    const rb=t*.34,bites=[];const side=(x0,y0,x1,y1)=>{const L=Math.hypot(x1-x0,y1-y0),n=Math.max(3,Math.round(L/(rb*2.75)));for(let i=0;i<n;i++){const f=(i+.5)/n;bites.push(`<circle cx="${x0+(x1-x0)*f}" cy="${y0+(y1-y0)*f}" r="${rb}" fill="#000"/>`)}};
    side(X,Y,X+OW,Y);side(X,Y+OH,X+OW,Y+OH);side(X,Y,X,Y+OH);side(X+OW,Y,X+OW,Y+OH);
    out.back=`<defs><mask id="${u}m" maskUnits="userSpaceOnUse"><rect x="${X}" y="${Y}" width="${OW}" height="${OH}" fill="#fff"/>${bites.join('')}</mask><filter id="${u}b" x="-10%" y="-10%" width="120%" height="130%"><feGaussianBlur stdDeviation="${5*q}"/></filter></defs>`+
      `<g filter="url(#${u}b)" transform="translate(0 ${3*q})"><rect x="${X}" y="${Y}" width="${OW}" height="${OH}" fill="rgba(30,38,34,.20)" mask="url(#${u}m)"/></g>`+
      `<rect x="${X}" y="${Y}" width="${OW}" height="${OH}" fill="#fbf7ec" mask="url(#${u}m)"/>`;
    out.front=`<rect x="${M-.5}" y="${M-.5}" width="${w+1}" height="${h+1}" fill="none" stroke="rgba(70,58,36,.22)" stroke-width="1"/>`}
  else if(k==='sketch'){
    const off=Math.max(4,6*q),line=(seed,o,sw,op)=>{const x=M-off-o,y=M-off-o,W2=w+2*(off+o),H2=h+2*(off+o),r=ri+off+o,a=W2-2*r,b=H2-2*r,P=2*a+2*b+2*Math.PI*r;
        const ph=[seed*1.7,seed*2.9,seed*4.3],amp=Math.max(.8,1.5*q),start=P*((seed*.37)%1),over=Math.max(10,16*q),N=Math.ceil((P+over)/4);let d='';
        for(let i=0;i<=N;i++){const s=start+i*(P+over)/N,[px,py,nx,ny]=rrAt(x,y,W2,H2,r,s),
          wob=amp*(Math.sin(s/41+ph[0])*.6+Math.sin(s/17+ph[1])*.3+Math.sin(s/7.3+ph[2])*.15)+(i<3?(3-i)*.5*amp:0)+(i>N-3?(i-N+3)*.6*amp:0);
          d+=(i?'L':'M')+(px+nx*wob).toFixed(1)+' '+(py+ny*wob).toFixed(1)}
        return `<path d="${d}" fill="none" stroke="#2c2a26" stroke-width="${sw}" stroke-linecap="round" stroke-linejoin="round" opacity="${op}"/>`};
    out.front=line(1,0,Math.max(1.1,1.6*q),.86)+line(2.3,Math.max(.8,1.3*q),Math.max(.8,1.05*q),.32)}
  else if(k==='rubber'||k==='metal'||k==='wood'){   // the van windows share one shape: a thick rounded bezel
    const ring=`${rrP(X,Y,OW,OH,ro)} ${rrP(M,M,w,h,ri)}`,shadow=`<filter id="${u}s" x="-10%" y="-10%" width="120%" height="130%"><feDropShadow dx="0" dy="${5*q}" stdDeviation="${7*q}" flood-color="#1e2622" flood-opacity=".30"/></filter>`,
      clip=`<clipPath id="${u}k"><path d="${ring}" clip-rule="evenodd"/></clipPath>`,mid=t*.5;
    if(k==='rubber'){
      out.front=`<defs>${shadow}${clip}<linearGradient id="${u}g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3b3c40"/><stop offset=".5" stop-color="#2a2b2e"/><stop offset="1" stop-color="#1c1d1f"/></linearGradient>`+
        `<linearGradient id="${u}h" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".28"/><stop offset=".22" stop-color="#fff" stop-opacity="0"/></linearGradient></defs>`+
        `<path d="${ring}" fill="url(#${u}g)" fill-rule="evenodd" filter="url(#${u}s)"/>`+
        `<g clip-path="url(#${u}k)"><path d="${rrP(M-mid,M-mid,w+2*mid,h+2*mid,ri+mid)}" fill="none" stroke="rgba(0,0,0,.35)" stroke-width="${Math.max(.8,1.2*q)}"/>`+
        `<path d="${rrP(M-t*.2,M-t*.2,w+t*.4,h+t*.4,ri+t*.2)}" fill="none" stroke="url(#${u}h)" stroke-width="${t*.22}"/></g>`+
        `<path d="${rrP(M,M,w,h,ri)}" fill="none" stroke="#0b0b0c" stroke-width="${t*.16}"/>`}
    else if(k==='metal'){
      const rv=[],R=Math.max(1.6,t*.13),cx=M-mid,cy=M-mid,cw=w+2*mid,ch=h+2*mid,cr=ri+mid,a=cw-2*cr,b=ch-2*cr,C=Math.PI*cr/2;
      const at=s=>{const[px,py]=rrAt(cx,cy,cw,ch,cr,s);rv.push([px,py])};
      for(let i=1;i<=4;i++){at(a*i/5);at(a+C+b+C+a*i/5)}for(let i=1;i<=2;i++){at(a+C+b*i/3);at(2*a+3*C+b+b*i/3)}
      [a+C/2,a+C+b+C/2,2*a+2*C+b+C/2,2*a+3*C+2*b+C/2].forEach(at);   // one near each corner
      out.front=`<defs>${shadow}${clip}<linearGradient id="${u}g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f1f2f4"/><stop offset=".45" stop-color="#d3d6da"/><stop offset="1" stop-color="#a7abb1"/></linearGradient>`+
        `<linearGradient id="${u}e" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#7b7f86"/></linearGradient>`+
        `<linearGradient id="${u}i" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#6d7178"/><stop offset="1" stop-color="#f4f5f6"/></linearGradient>`+
        `<filter id="${u}n" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="${(.006/q).toFixed(4)} ${(.55/q).toFixed(3)}" numOctaves="2" seed="4"/><feColorMatrix values="0 0 0 0 .4  0 0 0 0 .42  0 0 0 0 .45  0 0 0 .55 0"/></filter>`+
        `<radialGradient id="${u}r" cx=".35" cy=".3" r=".75"><stop offset="0" stop-color="#ffffff"/><stop offset=".55" stop-color="#c4c7cc"/><stop offset="1" stop-color="#7f838a"/></radialGradient></defs>`+
        `<path d="${ring}" fill="url(#${u}g)" fill-rule="evenodd" filter="url(#${u}s)"/>`+
        `<g clip-path="url(#${u}k)"><rect x="${X}" y="${Y}" width="${OW}" height="${OH}" filter="url(#${u}n)" opacity=".35"/></g>`+
        `<path d="${rrP(X+.75,Y+.75,OW-1.5,OH-1.5,ro)}" fill="none" stroke="url(#${u}e)" stroke-width="${Math.max(1,1.6*q)}"/>`+
        `<path d="${rrP(M-1,M-1,w+2,h+2,ri+1)}" fill="none" stroke="url(#${u}i)" stroke-width="${Math.max(1.2,2.2*q)}"/>`+
        `<path d="${rrP(M,M,w,h,ri)}" fill="none" stroke="#4a4d52" stroke-width="${t*.08}"/>`+
        rv.map(([x,y])=>`<circle cx="${x}" cy="${y+R*.35}" r="${R}" fill="rgba(0,0,0,.22)"/><circle cx="${x}" cy="${y}" r="${R}" fill="url(#${u}r)"/>`).join('')}
    else{   // wood
      out.front=`<defs>${shadow}${clip}<linearGradient id="${u}g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9a6a40"/><stop offset=".5" stop-color="#7d5130"/><stop offset="1" stop-color="#633d22"/></linearGradient>`+
        `<filter id="${u}n" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="${(.004/q).toFixed(4)} ${(.09/q).toFixed(3)}" numOctaves="3" seed="7"/><feColorMatrix values="0 0 0 0 .22  0 0 0 0 .12  0 0 0 0 .05  0 0 0 1.6 -.55"/></filter>`+
        `<linearGradient id="${u}e" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e2b88a" stop-opacity=".7"/><stop offset=".5" stop-color="#e2b88a" stop-opacity="0"/><stop offset="1" stop-color="#2d1a0d" stop-opacity=".5"/></linearGradient></defs>`+
        `<path d="${ring}" fill="url(#${u}g)" fill-rule="evenodd" filter="url(#${u}s)"/>`+
        `<g clip-path="url(#${u}k)"><rect x="${X}" y="${Y}" width="${OW}" height="${OH}" filter="url(#${u}n)" opacity=".9"/></g>`+
        `<path d="${rrP(X+.75,Y+.75,OW-1.5,OH-1.5,ro)}" fill="none" stroke="url(#${u}e)" stroke-width="${Math.max(1,1.8*q)}"/>`+
        `<path d="${rrP(M-t*.12,M-t*.12,w+t*.24,h+t*.24,ri+t*.12)}" fill="none" stroke="rgba(255,226,190,.18)" stroke-width="${Math.max(.8,1.2*q)}"/>`+
        `<path d="${rrP(M,M,w,h,ri)}" fill="none" stroke="#3a2212" stroke-width="${t*.2}"/>`}}
  return out}
function dreamyCanvas(cw,ch,col){   // the picture's edge dissolving into the page: an ordered dither stepping out along a cloud-shaped line
  const c=document.createElement('canvas');c.width=cw;c.height=ch;const g=c.getContext('2d'),im=g.createImageData(cw,ch),D=im.data,sc=cw/476;
  const B=[0,8,2,10,12,4,14,6,3,11,1,9,15,7,13,5],base=3*sc,band=26*sc,reach=base+band+30*sc;
  for(let y=0;y<ch;y++)for(let x=0;x<cw;x++){const e=Math.min(x,cw-1-x,y,ch-1-y);if(e>reach){if(x<cw/2)x=Math.max(x,cw-2-Math.ceil(reach));continue}   // skip the untouched middle
    const n=pcVn(x/(26*sc),y/(26*sc))*18*sc+pcVn(x/(9*sc)+40,y/(9*sc)+17)*6*sc,v=(e-base-n)/band;
    if(v<(B[(y&3)*4+(x&3)]+.5)/16){const i=(y*cw+x)*4;D[i]=col[0];D[i+1]=col[1];D[i+2]=col[2];D[i+3]=255}}
  g.putImageData(im,0,0);return c}
function deckleCanvas(cw,ch,col){   // a small copy of the postcard's deckled edge, for thumbnails
  const c=document.createElement('canvas');c.width=cw;c.height=ch;const g=c.getContext('2d'),im=g.createImageData(cw,ch),D=im.data,u=cw/1000*1.6,m=9*u,band=24*u;
  for(let y=0;y<ch;y++)for(let x=0;x<cw;x++){const t=Math.min(x,cw-1-x,y,ch-1-y);if(t>m+band*1.5+19*u)continue;
    const n=pcVn(x/(30*u),y/(30*u))*14*u+pcVn(x/(7*u),y/(7*u))*5*u,k=Math.min(1,Math.max(0,(t-n+band*.5-m)/band)),sm=k*k*(3-2*k);
    if(pcH12(Math.floor(x/Math.max(1,2*u)),Math.floor(y/Math.max(1,2*u)))>sm){const i=(y*cw+x)*4;D[i]=col[0];D[i+1]=col[1];D[i+2]=col[2];D[i+3]=255}}
  g.putImageData(im,0,0);return c}
const pageRGB=()=>getComputedStyle(document.body).backgroundColor.match(/\d+/g).slice(0,3).map(Number);
let frameKey='';
function frameDraw(){const B=document.body,k=frameOn();B.dataset.pcf=k;const R=document.documentElement.style,cs=getComputedStyle(document.documentElement);
  const w=parseFloat(cs.getPropertyValue('--pc-w'))||0,h=parseFloat(cs.getPropertyValue('--pc-h'))||0;if(!w||!h)return;
  const q=Math.max(.55,w/952),t=(FR_T[k]||0)*w,M=Math.ceil(t+30*q);
  R.setProperty('--pcm',M+'px');R.setProperty('--pcr',frameRadius(k,w,q)+'px');R.setProperty('--pcft',Math.round(t)+'px');R.setProperty('--pcin',(k==='postcard'||k==='dreamy'?2:1)+'px');   // the deckle and the dither are page-coloured at the very edge; trimming hides a seam when scaled
  
  const col=pageRGB(),key=[k,w,h,col].join();if(key===frameKey)return;frameKey=key;
  const o=frameSVG(k,w,h,M,'pf',q),W2=w+2*M,H2=h+2*M,sv=x=>x?`<svg viewBox="0 0 ${W2} ${H2}" preserveAspectRatio="none" aria-hidden="true">${x}</svg>`:'';
  $('#pcBack').innerHTML=sv(o.back);$('#pcFront').innerHTML=sv(o.front);
  if(k==='dreamy'){const c=dreamyCanvas(476,268,col);c.className='pcdream';$('#pcFront').appendChild(c)}}
{const _pl=pcLayout;pcLayout=function(){_pl();if(document.body.dataset.frame==='postcard')frameDraw()}}
function applyFrame(){document.body.dataset.pcf=frameOn();frameKey='';if(typeof size==='function')size();frameDraw();renderFrames()}
/* Settings > Frame: thumbnails of each frame on the current scene */
let frameNoteTxt='';
function frameThumb(k){const w=240,h=135,q=w/952*1.5,t=(FR_T[k]||0)*w,M=Math.ceil(t+10),W2=w+2*M,H2=h+2*M,u='ft'+k,o=frameSVG(k,w,h,M,u,q),r=frameRadius(k,w,q);
  const col=pageRGB();let over='';
  if(k==='dreamy')over=`<image href="${dreamyCanvas(240,135,col).toDataURL()}" x="${M}" y="${M}" width="${w}" height="${h}" style="image-rendering:pixelated"/>`;
  if(k==='postcard')over=`<image href="${deckleCanvas(240,135,col).toDataURL()}" x="${M}" y="${M}" width="${w}" height="${h}"/>`;
  return `<svg viewBox="0 0 ${W2} ${H2}" aria-hidden="true">${o.back}<defs><clipPath id="${u}p"><path d="${rrP(M,M,w,h,r)}"/></clipPath></defs>`+
    `<image href="${entryThumb({})}" x="${M}" y="${M}" width="${w}" height="${h}" preserveAspectRatio="xMidYMid slice" clip-path="url(#${u}p)"/>${over}${o.front}</svg>`}
function renderFrames(){renderFrames.on=true;const host=$('#setFrameKind');if(!host)return;const cur=frameOn(),n=state.entries.length;
  host.innerHTML=FRAMES.map(f=>{const ok=frameUnlocked(f.k);return `<button type="button" class="frb" data-k="${f.k}" aria-pressed="${f.k===cur}"${ok?'':' aria-disabled="true"'}>`+
    `<span class="frt">${frameThumb(f.k)}</span><b>${esc(f.l)}</b>${ok?'':`<small>After ${f.at} entries</small>`}</button>`}).join('');
  const note=$('#frameNote');note.hidden=!frameNoteTxt;note.textContent=frameNoteTxt}
$('#setFrameKind').addEventListener('click',e=>{const b=e.target.closest('.frb');if(!b||b.getAttribute('aria-disabled')==='true')return;state.settings.pcFrame=b.dataset.k;persist();applyFrame()});
{const _rs=renderSettings;renderSettings=function(){_rs();renderFrames()}}
{const _o=openPage;openPage=function(nm){if(nm==='settings'&&page!=='settings'){frameCheck();const seen=state.meta.framesSeen||(state.meta.framesSeen=[]),
    fresh=FRAMES.filter(f=>f.at&&(state.meta.framesUnlocked||[]).includes(f.k)&&!seen.includes(f.k));
    frameNoteTxt=fresh.length?(fresh.length===1?`A new frame is ready: ${fresh[0].l}.`:`New frames are ready: ${fresh.map(f=>f.l).join(', ')}.`):'';
    if(fresh.length){fresh.forEach(f=>seen.push(f.k));persist()}}
  _o(nm)}}
setTimeout(()=>{if(state.meta.framesSeen==null){frameCheck();state.meta.framesSeen=(state.meta.framesUnlocked||[]).slice();persist()}},0);   // frames earned before this existed: open, without a note
(function(){const b=document.createElement('div');b.id='pcBack';b.className='pcfx';document.body.prepend(b);
  const f=document.createElement('div');f.id='pcFront';f.className='pcfx';$('#scnav').before(f);document.body.dataset.pcf=frameOn()})();
$('#setFrame').addEventListener('click',()=>setTimeout(()=>{frameKey='';if(typeof size==='function')size()},0));
/* the field sits a short way under the card (the expanded writing card keeps its own place) */
function dockLift(){const B=document.body,R=document.documentElement.style,d=$('#dock');if(B.dataset.frame!=='postcard'||!d){R.removeProperty('--dock-b');return}
  const cs=getComputedStyle(document.documentElement),px=v=>parseFloat(cs.getPropertyValue(v))||0,k=px('--shk')||1,top=px('--pc-top'),h=px('--pc-h'),ft=px('--pcft');if(!h)return;
  const cardBottom=top+h/2+(h/2+ft)*k,want=innerHeight-(cardBottom+46*k)-d.offsetHeight*k,base=26;
  R.setProperty('--dock-b',Math.max(base,Math.round(want))+'px')}
{const _ps=pcShift;pcShift=function(){_ps();dockLift()}}
if(window.ResizeObserver)new ResizeObserver(()=>dockLift()).observe($('#dock'));
setTimeout(dockLift,0);
window.__frames={set:k=>{state.settings.pcFrame=k;persist();applyFrame()},testAll:on=>{FRAMES_TEST_ALL=on!==false;applyFrame()}};
let meadowOn=false;""")

rep('transition:opacity .7s ease,transform .8s cubic-bezier(.2,.8,.2,1),translate .55s cubic-bezier(.2,.8,.2,1),scale .55s cubic-bezier(.2,.8,.2,1)}',
    'transition:opacity .7s ease,transform .8s cubic-bezier(.2,.8,.2,1),translate .55s cubic-bezier(.2,.8,.2,1),scale .55s cubic-bezier(.2,.8,.2,1),bottom .45s cubic-bezier(.2,.8,.2,1)}')   # the field glides when the card moves

# ---------- styles ----------
rep('</style>', """
/* ---------- the field under the card; the wordmark a little lower ---------- */
body[data-frame="postcard"] .dock{bottom:calc(var(--dock-b,26px) + var(--sa-b,0px))}
.top .wmark{margin-top:9px}
/* ---------- scene frames ---------- */
.pcfx{position:fixed;pointer-events:none;display:none;left:calc(var(--pc-left,0px) - var(--pcm,0px));top:calc(var(--pc-top,84px) - var(--pcm,0px));
  width:calc(var(--pc-w,952px) + 2*var(--pcm,0px));height:calc(var(--pc-h,536px) + 2*var(--pcm,0px))}
body[data-frame="postcard"]:not([data-scene="stream"]) .pcfx{display:block}
#pcBack{z-index:0}#pcFront{z-index:4}
.pcfx svg{position:absolute;inset:0;width:100%;height:100%;overflow:visible}
.pcfx .pcdream{position:absolute;left:var(--pcm,0px);top:var(--pcm,0px);width:calc(100% - 2*var(--pcm,0px));height:calc(100% - 2*var(--pcm,0px));image-rendering:pixelated;image-rendering:crisp-edges}
body[data-frame="postcard"] :is(#meadow,#waterfall,#desert,#stage){clip-path:inset(var(--pcin,1px) round var(--pcr,0px))}
body[data-frame="postcard"]:not([data-pcf="postcard"]) canvas.pcEdge{display:none!important}
@media (min-width:761px){body[data-frame="postcard"] .pcfx{translate:var(--shx,0px) 0;scale:var(--shk,1);transition:translate .45s cubic-bezier(.2,.8,.2,1),scale .45s cubic-bezier(.2,.8,.2,1)}}
body.sbinit .pcfx{transition:none!important}
body[data-frame="full"] #frameGroup{display:none}
.frnote{margin:0 0 12px;padding:10px 12px;border-radius:10px;background:var(--green-2,#e7efe9);color:var(--green,#2f5d3e);font:500 13.5px/1.4 var(--ui)}
.frgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(118px,1fr));gap:10px}
.frb{display:flex;flex-direction:column;align-items:stretch;gap:6px;padding:8px 8px 10px;border:1px solid var(--line);border-radius:12px;background:var(--paper,#fff);cursor:pointer;text-align:center;color:var(--ink-2);font:500 13px/1.25 var(--ui)}
.frb .frt{display:block;line-height:0;padding:2px}
.frb svg{width:100%;height:auto;overflow:visible}
.frb b{font-weight:500}
.frb small{font:400 11.5px/1.3 var(--ui);color:var(--ink-3)}
.frb[aria-pressed="true"]{border:2px solid var(--green,#2f5d3e);padding:7px 7px 9px;color:var(--ink)}
.frb[aria-disabled="true"]{cursor:default}
.frb[aria-disabled="true"] .frt,.frb[aria-disabled="true"] b{opacity:.42}
.frb:not([aria-disabled="true"]):hover{border-color:var(--line-2)}
</style>""")

open(dst, 'w').write(s)
print('frames ok', len(s))
