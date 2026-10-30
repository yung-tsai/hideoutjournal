"""A notebook-style left sidebar, pages as cards in the main area, and a minimal scene switcher (after the UI refresh).
   - Sidebar (#sb), top to bottom: Home, Journal, Patterns, Tasks (green dot when new tasks were caught), Dev (the dev controls, once a floating badge); the recent entries, grouped
     This week / Last week / one group per month under collapsible headers (state.meta.sbFold), each row a mood-coloured dot (a
     stand-in for weather icons), the title and a short date; Settings pinned at the bottom. The menu icon (top left, it never moves)
     collapses and expands it (state.meta.sbOpen). The active item is highlighted.
   - Pages, like Claude's: each replaces the main area right of the sidebar; the scene shows only on Home (and the 2D scenes pause
     while a page covers them; the sound carries on). Hash routes: #/ (Home), #/journal, #/patterns, #/tasks, #/settings,
     #/dev, #/entry/<id>, so back and refresh work. The old panel (#sheet) is the page: its Journal list (search on top), entry view
     (with Edit and a back link to Journal), Patterns, Tasks and Settings are reused as they are, in a centred column (860 px)
     under a large serif title. The logo goes Home.
   - Desktop: the sidebar sits flush left; the postcard, the field and the logo slide right and re-centre in the room left
     (one translate + scale, so every scene's canvases move together), scaling down only if they must.
   - Phones: the sidebar fills the screen; choosing an item closes it and shows that page.
   - A thin, light scrollbar (and a light colour-scheme, so the browser never draws a dark one).
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
    '<nav class="sb" id="sb" aria-label="Sidebar"><div class="sbtop">'
    '<button type="button" class="sbi" data-act="home"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3.5 11 12 4l8.5 7"/><path d="M6 9.5V20h12V9.5"/></svg><span>Home</span></button>'
    '<button type="button" class="sbi" data-act="journal"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="5" y="3.5" width="14" height="17" rx="2"/><path d="M9 8h6M9 12h6M9 16h3"/></svg><span>Journal</span></button>'
    '<button type="button" class="sbi" data-act="patterns"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 19h16"/><path d="M5 15l4-5 4 3 6-7"/></svg><span>Patterns</span></button>'
    '<button type="button" class="sbi" data-act="tasks"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="4" y="5" width="4" height="4" rx="1"/><path d="M11 7h9"/><rect x="4" y="14" width="4" height="4" rx="1"/><path d="M11 16h9"/></svg><span>Tasks</span><i class="mndot in" id="menuDotT" hidden aria-hidden="true"></i></button>'
    '<button type="button" class="sbi" data-act="dev"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m8 8-4 4 4 4M16 8l4 4-4 4M13.5 5.5l-3 13"/></svg><span>Dev</span></button>'
    '</div><div class="sblist" id="sbList"></div>'
    '<div class="sbbot"><button type="button" class="sbi" data-act="settings"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg><span>Settings</span></button></div></nav>\n'
    '<aside class="sheet" id="sheet" aria-label="Page">'
    '<div class="cardbar"><button type="button" class="cback" id="cardBack" aria-label="Back" hidden><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 5.5 8.5 12l6.5 6.5"/></svg></button>'
    '<h2 id="cardTitle"></h2>'
    '<button type="button" class="cclose" id="cardClose" aria-label="Close"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6.5 6.5l11 11M17.5 6.5l-11 11"/></svg></button></div>')

# ---------- behaviour ----------
rep("let meadowOn=false;", r"""/* ---------- the sidebar: collapses and expands; the postcard, field and logo step aside ---------- */
const sbNarrow=()=>matchMedia('(max-width:760px)').matches;
function pcShift(){const B=document.body,R=document.documentElement.style,cs=getComputedStyle(document.documentElement),px=v=>parseFloat(cs.getPropertyValue(v))||0;
  let dx=0,k=1,x0=0;const L=px('--pc-left'),w=px('--pc-w'),h=px('--pc-h');
  if(B.dataset.sb==='open'&&!sbNarrow()){x0=$('#sb').offsetWidth;const room=innerWidth-x0-48;
    if(B.dataset.frame==='postcard'&&B.dataset.scene!=='stream'&&w){k=Math.min(1,room/w);dx=x0+24+room/2-(L+w/2)}}
  R.setProperty('--shx',dx+'px');R.setProperty('--shk',String(k));R.setProperty('--shdy',(-h*(1-k)/2)+'px');R.setProperty('--shlx',x0/2+'px');R.setProperty('--mainL',x0+'px')}
{const _pl=pcLayout;pcLayout=function(){_pl();pcShift()}}
function sbSet(open,keep){const B=document.body;if(open)B.dataset.sb='open';else delete B.dataset.sb;$('#menuBtn').setAttribute('aria-expanded',String(!!open));
  if(!keep&&!sbNarrow()){state.meta.sbOpen=!!open;persist()}pcShift()}
document.body.classList.add('sbinit');sbSet(!sbNarrow()&&state.meta.sbOpen!==false,true);
requestAnimationFrame(()=>requestAnimationFrame(()=>document.body.classList.remove('sbinit')));
$('#menuBtn').addEventListener('click',()=>sbSet(document.body.dataset.sb!=='open'));
addEventListener('resize',()=>requestAnimationFrame(pcShift));
/* ---------- the entry list: This week, Last week, then months; folds remembered ---------- */
const fSbDay=new Intl.DateTimeFormat(undefined,{month:'short',day:'numeric'}),fSbWk=new Intl.DateTimeFormat(undefined,{weekday:'short'}),fSbMon=new Intl.DateTimeFormat(undefined,{month:'long',year:'numeric'});
function sbGroups(list){const d=new Date(),t0=new Date(d.getFullYear(),d.getMonth(),d.getDate()).getTime(),wk=t0-((d.getDay()+6)%7)*864e5,lw=wk-7*864e5,out=[];
  for(const e of list){let k,l;if(e.at>=wk){k='this';l='This week'}else if(e.at>=lw){k='last';l='Last week'}else{const m=new Date(e.at);k='m'+m.getFullYear()+'-'+m.getMonth();l=fSbMon.format(m)}
    const g=out[out.length-1];if(g&&g.k===k)g.items.push(e);else out.push({k,l,items:[e],wk:k==='this'})}
  return out}
let sbSig='';
function renderSb(force){const q='',act=document.body.dataset.sheet&&$('#sheet').dataset.card==='entry'?openId:null;
  const sig=state.entries.map(e=>e.id+'|'+e.title+'|'+e.mood+'|'+(e.concern?1:0)+'|'+(e.archived?1:0)).join('~')+'#'+q+'#'+act+'#'+JSON.stringify(state.meta.sbFold||{});
  if(!force&&sig===sbSig)return;sbSig=sig;const host=$('#sbList');
  if(!state.entries.length){host.innerHTML='<p class="sbempty">Your entries will appear here as you write.</p>';return}
  let list=state.entries.slice().sort((a,b)=>b.at-a.at);list=q?list.filter(e=>matchesQ(e,q)):list.filter(e=>!e.archived);
  if(!list.length){host.innerHTML=`<p class="sbempty">${q?'Nothing matches “'+esc(q)+'”.':'Everything is archived.'}</p>`;return}
  const fold=state.meta.sbFold||{};let html='';
  for(const g of sbGroups(list)){const shut=!q&&fold[g.k];
    html+=`<section class="sbg"><button type="button" class="sbgh" data-k="${g.k}" aria-expanded="${!shut}"><svg viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4.5 2.5 8 6l-3.5 3.5"/></svg>${esc(g.l)}</button>`;
    if(!shut){html+='<ul>';for(const e of g.items){const m=e.concern?{c:'#6f6a8c'}:(MOODS[e.mood]||MOODS.calm);
      html+=`<li><button type="button" class="sbe${e.id===act?' on':''}" data-id="${esc(e.id)}"${e.id===act?' aria-current="true"':''}><i style="--m:${m.c}"></i><span class="t">${esc(e.title||'Untitled')}</span><span class="d">${esc((g.wk?fSbWk:fSbDay).format(new Date(e.at)))}</span></button></li>`}
      html+='</ul>'}
    html+='</section>'}
  host.innerHTML=html}
$('#sbList').addEventListener('click',e=>{const h=e.target.closest('.sbgh');if(h){const f=state.meta.sbFold||(state.meta.sbFold={});if(f[h.dataset.k])delete f[h.dataset.k];else f[h.dataset.k]=1;persist();renderSb();return}
  const r=e.target.closest('.sbe');if(r)go('entry/'+r.dataset.id)});
{const _persist=persist;persist=function(){_persist();if(window.requestAnimationFrame)requestAnimationFrame(()=>renderSb())}}
/* ---------- pages, with hash routes: #/ #/journal #/patterns #/tasks #/settings #/entry/<id> ---------- */
const PAGE_TITLE={patterns:'Patterns',tasks:'Tasks',settings:'Settings',journal:'Journal',dev:'Dev',entry:''};
{const pd=document.createElement('section');pd.className='page';pd.id='pg-dev';pd.innerHTML='<div class="pbody"></div>';$('#sheet').appendChild(pd);pd.firstChild.appendChild($('#devP'))}   // the dev controls live on their own page
let routing=false;
function go(r){if(sbNarrow()&&document.body.dataset.sb==='open')sbSet(false,true);const h='#/'+r;if(location.hash!==h)location.hash=h;else route()}
function routeNow(){const h=location.hash.replace(/^#\/?/,''),[a,b]=h.split('/');return a==='entry'&&b?'entry/'+b:['journal','patterns','tasks','settings','dev'].includes(a)?a:''}
function route(){const r=routeNow();if(document.body.dataset.focus==='journal'&&r)return;routing=true;
  try{if(r.startsWith('entry/')){const id=decodeURIComponent(r.slice(6));if(state.entries.some(e=>e.id===id)){setMemView('entries');openDetail(id)}else history.replaceState(null,'','#/journal'),route()}
    else if(r==='journal'){setMemView('entries');memView='entries';openPage('memories')}
    else if(r==='patterns'){memView='patterns';openPage('memories')}
    else if(r){openPage(r);if(r==='dev'&&typeof renderDev==='function')renderDev()}
    else if(page)openPage(null)}
  finally{routing=false}pageMark()}
function pageMark(){const sh=$('#sheet');let k='';
  if(page==='memories')k=$('#memDetail').style.display!=='none'?'entry':memView==='patterns'?'patterns':'journal';else if(page)k=page;
  if(k)sh.dataset.card=k;else delete sh.dataset.card;$('#cardTitle').textContent=PAGE_TITLE[k]||'';
  $$('#sb .sbi[data-act]').forEach(b=>b.setAttribute('aria-current',String(b.dataset.act===(k==='entry'?'':k||'home'))));renderSb();pcShift()}
{const _open=openPage;openPage=function(n){_open(n);if(!routing){const want=n==='memories'?(memView==='patterns'?'patterns':'journal'):n||'';
    if(routeNow()!==want&&!(want==='journal'&&routeNow().startsWith('entry/')))history.replaceState(null,'','#/'+want)}
  pageMark();if(page)$('#sheet').scrollTop=0}}
{const _od=openDetail;openDetail=function(id){_od(id);if(!routing&&routeNow()!=='entry/'+id)location.hash='#/entry/'+id;pageMark();$('#sheet').scrollTop=0}}
{const _sl=showList;showList=function(){_sl();if(!routing&&routeNow().startsWith('entry/'))setTimeout(()=>go('journal'),0)}}   // back from an entry (or deleting it): the Journal page
addEventListener('hashchange',route);
$$('#sb .sbi[data-act]').forEach(b=>b.addEventListener('click',()=>{const a=b.dataset.act;go(a==='home'?'':a)}));
$('.wmark').addEventListener('click',()=>go(''));
setTimeout(route,0);
setTimeout(()=>renderSb(true),0);   // after the rest of the app has loaded (MOODS, page)
/* ---------- the scene switcher: chevrons on hover, dots under the card, arrow keys, swipes ---------- */
const SCENES=['meadow','camp','waterfall','desert'],SC_LAYER={meadow:'#meadow',camp:'#stage',waterfall:'#waterfall',desert:'#desert'};
const curScene=()=>{const v=document.body.dataset.scene;return SCENES.includes(v)?v:'meadow'};
const scBusy=()=>body.dataset.focus==='journal'||!$('#fire').hidden||body.dataset.sheet||(body.dataset.sb==='open'&&narrow());
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
    return e.clientX>=r.left&&e.clientX<=r.right&&e.clientY>=r.top&&e.clientY<=r.bottom&&!(t.closest&&t.closest('.top,.dock,.journal,.sheet,.sb,.cardscrim'))};
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
/* ---------- the sidebar: a notebook's table of contents ---------- */
:root{--sbw:284px}
.sb{position:fixed;z-index:19;left:0;top:0;bottom:0;width:var(--sbw);display:flex;flex-direction:column;padding:calc(76px + var(--sa-t,0px)) 0 0;
  background:#f0efea;border-right:1px solid rgba(30,38,34,.06);color-scheme:light;transform:translateX(-100%);visibility:hidden;
  transition:transform .45s cubic-bezier(.2,.8,.2,1),visibility 0s .45s}
body[data-sb="open"] .sb{transform:none;visibility:visible;transition:transform .45s cubic-bezier(.2,.8,.2,1),visibility 0s}
body.sbinit .sb,body.sbinit :is(#meadow,#waterfall,#desert,#stage,#scnav,.dock,.scdots,.top .wmark){transition:none!important}
.sbtop{padding:0 12px 10px;display:flex;flex-direction:column;gap:2px;flex:none}
.sbi{display:flex;align-items:center;gap:12px;width:100%;min-height:40px;padding:0 12px;border:0;border-radius:10px;background:none;color:var(--ink-2,#5b6560);
  font:500 14.5px/1.2 var(--ui);text-align:left;cursor:pointer;transition:background .15s ease,color .15s ease}
.sbi svg{width:19px;height:19px;flex:none;color:var(--ink-3,#8c948f)}
.sbi:hover{background:rgba(30,38,34,.045);color:var(--ink,#1e2622)}
.sbi[aria-current="true"],.sbi[aria-expanded="true"]{background:rgba(47,93,62,.09);color:var(--green,#2f5d3e)}
.sbi[aria-current="true"] svg,.sbi[aria-expanded="true"] svg{color:var(--green,#2f5d3e)}
.sbi .mndot.in{margin-left:auto}
.sbq{padding:4px 2px 6px}
.sbq input{width:100%;height:38px;padding:0 12px;border:1px solid var(--line,rgba(30,38,34,.10));border-radius:10px;background:#fff;color:var(--ink);font:400 14px/1 var(--ui);outline:none}
.sbq input:focus{border-color:rgba(47,93,62,.45)}
.sblist{flex:1;min-height:0;overflow-y:auto;overscroll-behavior:contain;padding:6px 7px 18px 12px;margin-right:5px}
.sbg+.sbg{margin-top:14px}
.sbgh{display:flex;align-items:center;gap:6px;width:100%;padding:8px 12px 6px;border:0;background:none;cursor:pointer;color:var(--ink-3,#8c948f);font:600 11.5px/1 var(--ui);letter-spacing:.08em;text-transform:uppercase;text-align:left}
.sbgh svg{width:11px;height:11px;flex:none;transition:transform .2s ease;transform:rotate(90deg)}
.sbgh[aria-expanded="false"] svg{transform:none}
.sbgh:hover{color:var(--ink-2)}
.sbg ul{list-style:none;margin:0;padding:0}
.sbe{display:flex;align-items:center;gap:11px;width:100%;min-height:40px;padding:0 12px;border:0;border-radius:10px;background:none;cursor:pointer;text-align:left;color:var(--ink-2,#5b6560);font:400 14.5px/1.3 var(--ui)}
.sbe:hover{background:rgba(30,38,34,.045);color:var(--ink)}
.sbe.on{background:#fff;color:var(--ink);box-shadow:0 1px 3px rgba(30,38,34,.07)}
.sbe i{width:8px;height:8px;border-radius:50%;flex:none;background:var(--m);opacity:.6}
.sbe .t{flex:1;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.sbe .d{flex:none;font-size:12.5px;color:var(--ink-3,#8c948f)}
.sbempty{margin:6px 12px;color:var(--ink-3);font:400 14px/1.5 var(--ui)}
.sbbot{flex:none;padding:8px 12px calc(14px + var(--sa-b,0px))}
/* a thin, light scrollbar, inset a little from the edge */
.sblist,.sheet .pbody{scrollbar-width:thin;scrollbar-color:var(--line-2,rgba(30,38,34,.18)) transparent}
.sblist::-webkit-scrollbar,.sheet .pbody::-webkit-scrollbar{width:8px;background:transparent}
.sblist::-webkit-scrollbar-track,.sheet .pbody::-webkit-scrollbar-track{background:transparent}
.sblist::-webkit-scrollbar-thumb,.sheet .pbody::-webkit-scrollbar-thumb{background:var(--line-2,rgba(30,38,34,.18));border-radius:8px;border:2px solid transparent;background-clip:padding-box}
.sheet .pbody{margin-right:5px;padding-right:21px}
/* ---------- pages: the main area right of the sidebar ---------- */
html,body{overflow-x:hidden}
#devChip{display:none!important}
.sheet[data-page="dev"] #pg-dev{display:flex}
#pg-dev .devp{position:static;width:auto;max-height:none;overflow:visible;padding:4px 0;background:none;border:0;color:var(--ink);border-radius:0;box-shadow:none;display:flex;flex-direction:column;gap:18px}
#pg-dev .devp h4{color:var(--ink-3);margin-bottom:8px}
#pg-dev .devp p{color:var(--ink-2)}
#pg-dev .devp button{font:500 13px/1 var(--ui);border:1px solid var(--line-2);background:var(--paper,#fff);color:var(--ink);border-radius:8px;padding:8px 12px}
#pg-dev .devp button[aria-pressed="true"]{background:var(--green,#2f5d3e);border-color:var(--green,#2f5d3e);color:#fff}
#pg-dev .devp .dseg{gap:6px}
.wmark{cursor:pointer}
.sheet{position:fixed;z-index:18;left:var(--mainL,0px);right:0;top:0;bottom:0;width:auto;max-height:none;display:block;overflow-y:auto;overscroll-behavior:contain;
  border:0;border-radius:0;box-shadow:none;background:var(--ground,#f7f6f2);-webkit-backdrop-filter:none;backdrop-filter:none;color-scheme:light;
  transform:none;opacity:0;visibility:hidden;transition:opacity .22s ease,left .45s cubic-bezier(.2,.8,.2,1),visibility 0s .22s}
body[data-sheet] .sheet{transform:none;opacity:1;visibility:visible;transition:opacity .22s ease,left .45s cubic-bezier(.2,.8,.2,1),visibility 0s}
body.sbinit .sheet{transition:none!important}
.sheet::before{content:'';position:sticky;top:0;display:block;height:calc(72px + var(--sa-t,0px));margin-bottom:calc(-72px - var(--sa-t,0px));background:linear-gradient(var(--ground,#f7f6f2) 72%,rgba(247,246,242,0));z-index:3;pointer-events:none}   /* pages fade out under the header */
.sheet[data-wide="true"]{width:auto}
.cardbar,.sheet .page{max-width:860px;margin:0 auto;box-sizing:border-box}
.cardbar{display:block;padding:calc(92px + var(--sa-t,0px)) 40px 10px}
.cardbar h2{margin:0;font:400 40px/1.1 var(--serif);color:var(--ink);letter-spacing:-.01em}
.cback,.cclose{display:none!important}
.sheet .page{padding:0 18px 80px}
.sheet[data-page] .page{flex-direction:column}
.sheet .pbody{flex:none;overflow:visible;min-height:0;margin-right:0!important;padding-right:22px!important}
.sheet .grip,.sheet .phead h2,.sheet .phead .close,#pg-settings>.phead,.sheet .pwide,#pg-memories #memList>.phead{display:none}
.sheet[data-card="patterns"] #pg-memories .tools-row{display:none!important}
.sheet[data-card="entry"] .cardbar{display:none}
.sheet[data-card="entry"] #memDetail>.phead{display:flex;padding:calc(84px + var(--sa-t,0px)) 22px 4px}
#memDetail .back{display:inline-flex;align-items:center;gap:6px;border:0;background:none;padding:6px 0;color:var(--ink-2);font:500 14px/1 var(--ui);cursor:pointer}
#memDetail .back:hover{color:var(--green,#2f5d3e)}
#pg-tasks .phead{padding-top:0;padding-bottom:4px}
#pg-memories .tools-row{padding:6px 22px 6px}
.sheet[data-card="journal"] .mem{grid-template-columns:1fr!important;grid-template-areas:"top" "h" "p" "meta"!important;padding:14px 16px!important}
.sheet[data-card="journal"] .mthumb{display:none}
.sheet .dtitle{font:400 34px/1.15 var(--serif)!important}
@media (min-width:900px){.sheet #setScene{grid-template-columns:repeat(4,1fr)!important}}
@media (min-width:1100px){.sheet[data-card="patterns"] .pat{display:grid;grid-template-columns:1fr 1fr;align-items:start;gap:14px}
  .sheet[data-card="patterns"] .pat>.prange,.sheet[data-card="patterns"] .pat>.pchart,.sheet[data-card="patterns"] .pat>.pcols,.sheet[data-card="patterns"] .pat>.pfoot{grid-column:1/-1}}
.sheet{scrollbar-width:thin;scrollbar-color:var(--line-2,rgba(30,38,34,.18)) transparent}
.sheet::-webkit-scrollbar{width:10px;background:transparent}
.sheet::-webkit-scrollbar-track{background:transparent}
.sheet::-webkit-scrollbar-thumb{background:var(--line-2,rgba(30,38,34,.18));border-radius:8px;border:3px solid transparent;background-clip:padding-box}
@media (min-width:761px){body .top .wmark{translate:var(--shlx,0px) 0;transition:translate .45s cubic-bezier(.2,.8,.2,1)}}
/* ---------- phones: the sidebar and its cards fill the screen ---------- */
@media (max-width:760px){
  .sb{width:auto;right:0;border-right:0;background:var(--ground,#f7f6f2);padding-top:calc(72px + var(--sa-t,0px))}
  .top .wmark,.top .tools{transition:opacity .3s ease}
  body[data-sb="open"] .top .wmark,body[data-sb="open"] .top .tools{opacity:0;pointer-events:none}
  .sheet{left:0;z-index:18}
  .cardbar{padding:calc(76px + var(--sa-t,0px)) 22px 6px}
  .cardbar h2{font-size:32px}
  .sheet .page{padding:0 4px 60px}
  .sheet[data-card="entry"] #memDetail>.phead{padding:calc(70px + var(--sa-t,0px)) 18px 4px}
  .sheet .pbody{padding-right:18px!important}}
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

# ---------- the 2D scenes rest while a page covers them (the sound carries on) ----------
for k in ('meadow', 'waterfall', 'desert'):
    rep(f"()=>document.body.dataset.scene==='{k}'&&!document.hidden)", f"()=>document.body.dataset.scene==='{k}'&&!document.hidden&&!document.body.dataset.sheet)")

open(dst, 'w').write(s)
print('nav ok', len(s))
