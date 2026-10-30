"""One left sidebar and a minimal scene switcher (after the UI refresh).
   - The menu icon (top left, it never moves) opens and closes one sidebar; Esc closes it too. Its top row, beside the menu icon:
     Journal | Tasks as a small segmented control (a green dot on Tasks when new tasks were caught) and a Settings gear at the end.
     Under it, the page (the old panels' headings and close buttons are hidden). The last page opened is remembered (state.meta.lastPage).
   - Desktop: an inset rounded card on the left, about 400 px, full height. The postcard, the field and the logo slide right and
     re-centre in the room left (one translate + scale, so every scene's canvases move together), scaling down only if they must.
     Phones: the sidebar fills the screen; the logo and volume step out of its way.
   - A thin, light scrollbar in the sidebar (and a light colour-scheme, so the browser never draws a dark one).
   - The scene caption is gone (name, description, weather line).
   - The switcher in its place: on hover, soft chevrons fade in inside the frame's left and right edges and a tiny row of dots
     under the card shows which scene this is. A chevron (or the left/right arrow keys, when not typing) crossfades to the
     previous/next scene, wrapping around; on phones, swipe the scene. It drives Settings > Scene, so the choice is remembered.
   python3 nav.py <in.html> <out.html>"""
import sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n: sys.exit(f'nav.py: expected {n} got {c}: {a[:90]!r}')
    s = s.replace(a, b)

CHEV = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="{}"/></svg>'
rep('<aside class="sheet" id="sheet" aria-label="Panel">',
    '<div class="scnav" id="scnav"><button type="button" class="scgo prev" data-d="-1" aria-label="Previous scene" tabindex="-1">' + CHEV.format('M14.5 6 8.5 12l6 6') + '</button>'
    '<button type="button" class="scgo next" data-d="1" aria-label="Next scene" tabindex="-1">' + CHEV.format('M9.5 6l6 6-6 6') + '</button></div>\n'
    '<div class="scdots" id="scdots" aria-hidden="true"><i data-v="meadow"></i><i data-v="camp"></i><i data-v="waterfall"></i><i data-v="desert"></i></div>\n'
    '<aside class="sheet" id="sheet" aria-label="Sidebar">'
    '<div class="sbnav" id="sbnav"><div class="seg sbseg" role="group" aria-label="Section"><button type="button" data-sb="memories">Journal</button>'
    '<button type="button" data-sb="tasks">Tasks<i class="mndot in" id="menuDotT" hidden aria-hidden="true"></i></button></div>'
    '<button type="button" class="sbgear" data-sb="settings" aria-label="Settings"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg></button></div>')

# ---------- behaviour ----------
rep("let meadowOn=false;", r"""/* ---------- one left sidebar: the menu icon opens it; the postcard, field and logo step aside ---------- */
function pcShift(){const R=document.documentElement.style,cs=getComputedStyle(document.documentElement),px=v=>parseFloat(cs.getPropertyValue(v))||0;
  let dx=0,k=1,lx=0;const L=px('--pc-left'),w=px('--pc-w'),h=px('--pc-h');
  if(body.dataset.sheet&&!narrow()){const x0=sheet.offsetLeft+sheet.offsetWidth+24,x1=innerWidth-24,room=x1-x0;lx=(x0+innerWidth)/2-innerWidth/2;
    if(pcOn()&&w){k=Math.min(1,room/w);dx=x0+room/2-(L+w/2)}}
  R.setProperty('--shx',dx+'px');R.setProperty('--shk',String(k));R.setProperty('--shdy',(-h*(1-k)/2)+'px');R.setProperty('--shlx',lx+'px')}
function sbSync(){$$('#sbnav [data-sb]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.sb===page)));$('#menuBtn').setAttribute('aria-expanded',String(!!page))}
{const _open=openPage;openPage=function(n){_open(n);if(n&&page===n&&state.meta.lastPage!==n){state.meta.lastPage=n;persist()}sbSync();pcShift()}}
$('#menuBtn').addEventListener('click',()=>openPage(page?null:(state.meta.lastPage||'memories')));
$$('#sbnav [data-sb]').forEach(b=>b.addEventListener('click',()=>openPage(b.dataset.sb)));
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&page&&body.dataset.focus!=='journal'){openPage(null);$('#menuBtn').focus({preventScroll:true})}});
addEventListener('resize',()=>requestAnimationFrame(pcShift));
/* ---------- the scene switcher: chevrons on hover, dots under the card, arrow keys, swipes ---------- */
const SCENES=['meadow','camp','waterfall','desert'],SC_LAYER={meadow:'#meadow',camp:'#stage',waterfall:'#waterfall',desert:'#desert'};
const curScene=()=>{const v=document.body.dataset.scene;return SCENES.includes(v)?v:'meadow'};
const scBusy=()=>body.dataset.focus==='journal'||!$('#fire').hidden||(body.dataset.sheet&&narrow());
function scDots(){$$('#scdots i').forEach(i=>i.classList.toggle('on',i.dataset.v===curScene()))}
let scDotT=0;function scFlash(){scDots();body.dataset.scdots='1';clearTimeout(scDotT);scDotT=setTimeout(()=>{if(!body.dataset.schover)delete body.dataset.scdots},1600)}
function scSnap(){   // a still of the scene as it is now, laid over it and faded out: the crossfade
  const L=$(SC_LAYER[curScene()]);if(!L)return;const r=L.getBoundingClientRect();if(!r.width)return;
  const dpr=devicePixelRatio||1,c=document.createElement('canvas'),g=c.getContext('2d');c.width=Math.round(r.width*dpr);c.height=Math.round(r.height*dpr);g.imageSmoothingEnabled=false;
  L.querySelectorAll('canvas').forEach(cv=>{const st=getComputedStyle(cv);if(st.display==='none'||st.visibility==='hidden'||!cv.width||!cv.height)return;
    const q=cv.getBoundingClientRect();let sx=0,sy=0,sw=cv.width,sh=cv.height;
    if(st.objectFit==='cover'){const a=q.width/q.height,b=cv.width/cv.height;if(b>a){sw=cv.height*a;sx=(cv.width-sw)/2}else{sh=cv.width/a;sy=(cv.height-sh)/2}}
    g.globalAlpha=+st.opacity;g.globalCompositeOperation=st.mixBlendMode==='normal'?'source-over':st.mixBlendMode;
    try{g.drawImage(cv,sx,sy,sw,sh,(q.left-r.left)*dpr,(q.top-r.top)*dpr,q.width*dpr,q.height*dpr)}catch(_){}});
  c.className='scsnap';Object.assign(c.style,{left:r.left+'px',top:r.top+'px',width:r.width+'px',height:r.height+'px'});document.body.appendChild(c);
  requestAnimationFrame(()=>requestAnimationFrame(()=>{c.style.opacity='0';setTimeout(()=>c.remove(),700)}))}
function goScene(d){if(scBusy())return;const v=SCENES[(SCENES.indexOf(curScene())+d+SCENES.length)%SCENES.length],b=$('#setScene button[data-v="'+v+'"]');if(!b)return;
  scSnap();b.click();scFlash()}
(function(){const nav=$('#scnav');
  nav.querySelectorAll('.scgo').forEach(b=>b.addEventListener('click',e=>{e.stopPropagation();goScene(+b.dataset.d);b.blur()}));
  const over=e=>{const r=$(SC_LAYER[curScene()]).getBoundingClientRect(),t=e.target;
    return e.clientX>=r.left&&e.clientX<=r.right&&e.clientY>=r.top&&e.clientY<=r.bottom&&!(t.closest&&t.closest('.top,.dock,.journal,.sheet'))};
  const hover=on=>{if(on===!!body.dataset.schover)return;if(on){body.dataset.schover='1';scDots();body.dataset.scdots='1'}else{delete body.dataset.schover;delete body.dataset.scdots}};
  document.addEventListener('pointermove',e=>{if(e.pointerType==='mouse')hover(!scBusy()&&over(e))});
  document.documentElement.addEventListener('pointerleave',()=>hover(false));
  document.addEventListener('keydown',e=>{if(e.key!=='ArrowLeft'&&e.key!=='ArrowRight'||e.altKey||e.ctrlKey||e.metaKey||e.shiftKey||e.defaultPrevented)return;
    const a=document.activeElement;if(a&&(a.matches('input,textarea,select')||a.isContentEditable))return;
    goScene(e.key==='ArrowLeft'?-1:1)});
  let t0=null;   // swipes on the scene
  document.addEventListener('touchstart',e=>{t0=null;if(e.touches.length!==1||scBusy())return;const p=e.touches[0];if(!over({clientX:p.clientX,clientY:p.clientY,target:e.target}))return;t0={x:p.clientX,y:p.clientY,t:Date.now()}},{passive:true});
  document.addEventListener('touchend',e=>{if(!t0)return;const p=e.changedTouches[0],dx=p.clientX-t0.x,dy=p.clientY-t0.y;
    if(Math.abs(dx)>44&&Math.abs(dx)>Math.abs(dy)*1.5&&Date.now()-t0.t<800)goScene(dx<0?1:-1);t0=null},{passive:true});
  scDots()})();
let meadowOn=false;""")

# ---------- styles ----------
rep('</style>', """
/* ---------- no caption ---------- */
.s3cap{display:none!important}
/* ---------- one left sidebar ---------- */
:root{--sb-w:min(400px,calc(100vw - 24px))}
.sheet{right:auto;left:calc(12px + var(--sa-l,0px));top:calc(12px + var(--sa-t));bottom:12px;width:var(--sb-w);z-index:19;transform:translateX(calc(-100% - 40px));color-scheme:light}
body[data-sheet] .sheet{transform:none}
.sheet[data-wide="true"]{width:var(--sb-w)}
.sheet[data-wide="true"] .pat{display:flex;flex-direction:column}
.sheet .grip,.sheet .phead h2,.sheet .phead .close,#pg-settings>.phead{display:none}
.sbnav{display:flex;align-items:center;gap:10px;min-height:40px;padding:8px 14px 4px 64px;flex:none}
.sheet .pwide{display:none}   /* the sidebar keeps one width, so Patterns' Expand would cover the scene */
.sbseg{display:inline-flex!important;padding:3px!important;gap:2px}
.sbseg button{height:32px!important;padding:0 14px!important;font:500 14px/1 var(--ui)!important}
.sbgear{margin-left:auto;width:36px;height:36px;border:0;border-radius:50%;background:none;color:var(--ink-2);display:grid;place-items:center;cursor:pointer;transition:background .2s ease,color .2s ease}
.sbgear svg{width:20px;height:20px}
.sbgear:hover{background:var(--paper-2)}
.sbgear[aria-pressed="true"]{color:var(--green,#2f5d3e);background:var(--green-2,#e7efe9)}
#pg-tasks .phead{padding-top:10px;padding-bottom:4px}
#pg-memories .phead{padding-top:8px}
#pg-memories .phead .memseg{margin-top:4px}
/* a thin, light scrollbar, inset a little from the edge */
.sheet .pbody{scrollbar-width:thin;scrollbar-color:var(--line-2,rgba(30,38,34,.18)) transparent;margin-right:5px;padding-right:17px}
.sheet .pbody::-webkit-scrollbar{width:8px;background:transparent}
.sheet .pbody::-webkit-scrollbar-track{background:transparent}
.sheet .pbody::-webkit-scrollbar-thumb{background:var(--line-2,rgba(30,38,34,.18));border-radius:8px;border:2px solid transparent;background-clip:padding-box}
@media (min-width:761px){body .top .wmark{translate:var(--shlx,0px) 0;transition:translate .55s cubic-bezier(.2,.8,.2,1)}}
@media (max-width:760px){
  .sheet{left:0;right:0;top:0;bottom:0;width:auto;border-radius:0;border:0;box-shadow:none;transform:translateX(-100%)}
  body[data-sheet] .sheet{transform:none}
  .sbnav{padding:calc(14px + var(--sa-t)) 14px 6px calc(68px + var(--sa-l,0px))}
  .sheet .pbody{margin-right:3px;padding-right:15px}
  .top .wmark,.top .tools{transition:opacity .3s ease}
  body[data-sheet] .top .wmark,body[data-sheet] .top .tools{opacity:0;pointer-events:none}}
/* ---------- the postcard steps aside on desktop (pcShift) ---------- */
@media (min-width:761px){
body[data-frame="postcard"] :is(#meadow,#waterfall,#desert,#stage,#scnav){translate:var(--shx,0px) 0;scale:var(--shk,1);clip-path:inset(2px);transition:translate .55s cubic-bezier(.2,.8,.2,1),scale .55s cubic-bezier(.2,.8,.2,1)}
body[data-frame="postcard"] .dock{transform:translateX(-50%) translateY(var(--dock-y,0px));translate:var(--shx,0px) 0;scale:var(--shk,1);transform-origin:50% 100%;
  transition:opacity .7s ease,transform .8s cubic-bezier(.2,.8,.2,1),translate .55s cubic-bezier(.2,.8,.2,1),scale .55s cubic-bezier(.2,.8,.2,1)}
body[data-frame="postcard"] .scdots{translate:var(--shx,0px) var(--shdy,0px);transition:opacity .35s ease,translate .55s cubic-bezier(.2,.8,.2,1)}}
/* ---------- the scene switcher ---------- */
.scnav{position:fixed;inset:0;z-index:4;pointer-events:none}
body[data-frame="postcard"] .scnav{inset:auto;left:var(--pc-left,50%);top:var(--pc-top,84px);width:var(--pc-w,952px);height:var(--pc-h,536px)}
body[data-scene="stream"] .scnav,body[data-scene="stream"] .scdots{display:none}
.scgo{position:absolute;top:50%;width:38px;height:38px;margin-top:-19px;border:0;border-radius:50%;display:grid;place-items:center;cursor:pointer;
  background:rgba(255,255,255,.62);color:#1e2622;-webkit-backdrop-filter:blur(8px);backdrop-filter:blur(8px);box-shadow:0 2px 10px rgba(0,0,0,.10);
  opacity:0;pointer-events:none;transition:opacity .35s ease,background .2s ease}
.scgo svg{width:20px;height:20px}
.scgo:hover{background:rgba(255,255,255,.85)}
.scgo.prev{left:30px}.scgo.next{right:30px}
body[data-schover] .scgo{opacity:1;pointer-events:auto}
.scdots{position:fixed;left:50%;bottom:calc(120px + var(--sa-b));transform:translateX(-50%);z-index:4;display:flex;gap:7px;pointer-events:none;opacity:0;transition:opacity .35s ease}
body[data-frame="postcard"] .scdots{left:calc(var(--pc-left,0px) + var(--pc-w,952px)/2);bottom:auto;top:calc(var(--pc-top,84px) + var(--pc-h,536px) + 16px)}
.scdots i{width:6px;height:6px;border-radius:50%;background:var(--ink-3,#8c948f);opacity:.35;transition:opacity .3s ease,background .3s ease}
.scdots i.on{opacity:1;background:var(--green,#2f5d3e)}
body[data-frame="full"] .scdots i{background:#fff}
body[data-scdots] .scdots{opacity:1}
body[data-focus="journal"] .scnav,body[data-focus="journal"] .scdots{display:none}
.scsnap{position:fixed;z-index:3;pointer-events:none;image-rendering:pixelated;opacity:1;transition:opacity .6s ease}
@media (hover:none){.scgo{display:none}}
</style>""")

open(dst, 'w').write(s)
print('nav ok', len(s))
