"""Patterns you can read: a colour key, plain wording, hover/tap details on every check-in, and a wide view.
   Demo entries are marked as demo, never count as days journaled, and can be removed on their own.
   python3 patterns.py <in.html> <out.html>"""
import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__)) + '/'   # src/
A = HERE + '../assets/'   # art, sound and scene data
import sys, json
src, dst = sys.argv[1], sys.argv[2]
s = open(src).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n: sys.exit(f'patterns.py: expected {n} got {c}: {a[:90]!r}')
    s = s.replace(a, b)
DEMO = json.load(open(A+'up/demo_bodies.json'))

# ---------------- demo entries: marked, not counted, removable ----------------
rep("let state=load();",
    "let state=load();\n"
    "const DEMO_TEXT=new Set(" + json.dumps(DEMO) + ");\n"
    "function markDemo(){let n=0;for(const e of state.entries)if(e&&!e.demo&&DEMO_TEXT.has(e.body)){e.demo=true;n++}if(n)persist()}\n"
    "const demoCount=()=>state.entries.filter(e=>e&&e.demo).length;\n"
    "markDemo();")
rep("for(const e of state.entries){if(!e||typeof e.at!=='number')continue;k.add(dayKey(e.at));",
    "for(const e of state.entries){if(!e||e.demo||typeof e.at!=='number')continue;k.add(dayKey(e.at));")   # demo never counts as days journaled
rep("seg('sim',[['null','Real ('+realDays()+')'],",
    "seg('sim',[['null','Real ('+realDays()+(demoCount()?', demo not counted':'')+')'],")
rep('<button type="button" id="devDemo">Load demo memories</button>',
    '<button type="button" id="devDemo">Load demo memories</button>${demoCount()?\'<button type="button" id="devDemoOff">Remove demo memories (\'+demoCount()+\')</button>\':\'\'}')
rep("$('#devDemo').addEventListener('click',()=>{loadDemo();renderDev();updateDock();if(page)openPage(page)});",
    "$('#devDemo').addEventListener('click',()=>{loadDemo();markDemo();renderDev();updateDock();if(page)openPage(page)});\n"
    "  $('#devDemoOff')&&$('#devDemoOff').addEventListener('click',()=>{const gone=new Set(state.entries.filter(e=>e.demo).map(e=>e.id));\n"
    "    state.entries=state.entries.filter(e=>!e.demo);\n"
    "    state.tasks=state.tasks.filter(t=>!(Array.isArray(t.sources)&&t.sources.length&&t.sources.every(x=>gone.has(x.entryId))));\n"
    "    persist();updateCustDot();renderDev();updateDock();if(page)openPage(page)});")

# ---------------- Patterns ----------------
i = s.index("function renderPatterns(){")
j = s.index("$$('.prange button',host).forEach(b=>b.addEventListener('click',()=>{patRange=b.dataset.r;renderPatterns()}))}", i)
j += len("$$('.prange button',host).forEach(b=>b.addEventListener('click',()=>{patRange=b.dataset.r;renderPatterns()}))}")
old = s[i:j]
# keep the parts that don't change (lighter / themes / feelings) by lifting them out of the old function
def between(a, b):
    x = old.index(a); y = old.index(b, x); return old[x:y]
lift_themes_feels = between("  // lighter", "  // week") + between("  // themes: what you were writing about on good and hard days", "  const rng=")
new = r"""var patWide=false;   // var: openPage can run before this line during start-up
const fTip=new Intl.DateTimeFormat(undefined,{weekday:'short',month:'short',day:'numeric',hour:'numeric',minute:'2-digit'});
const MOOD_KEY=['happy','calm','okay','frustrated','low'];
function setPatWide(on){patWide=!!on&&!narrow();if(patWide){sheet.dataset.wide='true';body.dataset.patwide='1'}else{delete sheet.dataset.wide;delete body.dataset.patwide}
  if(page&&!narrow())viewK.panelT=sheet.offsetWidth+36}
function patTipHTML(e){const L=k=>MOODS[k]?MOODS[k].l.toLowerCase():'',dot=(k,ring)=>k?`<i class="${ring?'ring':'dot'}" style="--c:${MOODS[k].c}"></i>`:'';
  const b=e.moodBefore,a=e.moodAfter;
  const line=b&&a?(b===a?`Arrived and left ${L(a)}`:`Arrived ${L(b)}, left ${L(a)}`):b?`Arrived ${L(b)}`:`Left ${L(a)}`;
  return `<small>${esc(fTip.format(new Date(e.at)))}</small><b>${dot(b,1)}${dot(a,0)}${esc(line)}</b>${e.title?`<span>${esc(e.title)}</span>`:''}<button type="button" class="ptopen" data-id="${e.id}">Read entry</button>`}
// hover (mouse) or tap (touch) a check-in to see it; a click keeps it open so "Read entry" can be reached
function wireTips(card,list){const tip=card.querySelector('.ptip');let pinned=null;
  const clear=()=>card.querySelectorAll('[data-i].on').forEach(x=>x.classList.remove('on'));
  const show=t=>{clear();t.classList.add('on');tip.innerHTML=patTipHTML(list[+t.dataset.i]);tip.hidden=false;
    const r=t.getBoundingClientRect(),c=card.getBoundingClientRect(),tw=tip.offsetWidth,th=tip.offsetHeight;
    let x=r.left+r.width/2-c.left,y=r.top-c.top,yb=r.bottom-c.top;
    if(t.dataset.y&&t.ownerSVGElement){const sv=t.ownerSVGElement,b=sv.getBoundingClientRect(),k=b.height/sv.viewBox.baseVal.height;
      y=b.top+(+t.dataset.y)*k-c.top-6;yb=y+14}x=Math.max(tw/2+6,Math.min(c.width-tw/2-6,x));
    const below=y-th-12<0;tip.classList.toggle('below',below);tip.style.left=x+'px';tip.style.top=(below?yb:y)+'px'};
  const hide=()=>{clear();tip.hidden=true;pinned=null};
  card.addEventListener('pointerover',ev=>{if(ev.pointerType!=='mouse'||pinned)return;const t=ev.target.closest('[data-i]');
    if(t)show(t);else if(!ev.target.closest('.ptip'))hide()});
  card.addEventListener('pointerleave',()=>{if(!pinned)hide()});
  card.addEventListener('click',ev=>{const o=ev.target.closest('.ptopen');
    if(o){setPatWide(false);setMemView('entries');openDetail(o.dataset.id);return}
    const t=ev.target.closest('[data-i]');if(t){if(pinned===t){hide();return}pinned=t;show(t)}else if(!ev.target.closest('.ptip'))hide()})}
function renderPatterns(){const host=$('#patBody'),all=state.entries.filter(e=>!e.archived&&(e.moodBefore||e.moodAfter)),MIN=5;
  if(all.length<MIN){host.innerHTML=`<div class="pempty"><p class="pt">Your patterns will show up here.</p><p class="note">Each time you note how you are, before or after writing, it adds a point. Once there are a few, you’ll see your highs and lows, whether writing leaves you lighter, and what tends to come up on your good and hard days.</p><div class="pbar"><i style="width:${all.length/MIN*100}%"></i></div><p class="note" style="margin-top:8px">${all.length} of ${MIN} check-ins so far</p></div>`;return}
  const now=Date.now(),DAY=864e5,span={month:30,'8w':56,all:0}[patRange],first=Math.min(...all.map(e=>e.at));
  const from=span?Math.max(now-span*DAY,first-DAY):first-DAY,pts=all.filter(e=>e.at>=from).sort((a,b)=>a.at-b.at);
  const val=e=>e.moodAfter||e.moodBefore,wide=patWide&&!narrow(),touch=matchMedia('(hover: none)').matches;
  // the chart is drawn at the size it's shown, so the labels stay readable in the panel and in the wide view
  const W=Math.round(Math.max(340,Math.min(1100,(host.clientWidth||420)-34))),H=wide?270:212,PL=62,PR=10,PT=14,PB=28,iw=W-PL-PR,ih=H-PT-PB,
    X=t=>PL+(t-from)/Math.max(1,now-from)*iw,Y=m=>PT+(2-BAND[m])/2*ih+(OFF[m]||0);
  let g='';['High','Neutral','Low'].forEach((l,i)=>{const y=PT+i/2*ih;g+=`<line x1="${PL}" y1="${y}" x2="${W-PR}" y2="${y}" stroke="rgba(232,236,242,.09)"/><text x="${PL-10}" y="${y+4}" text-anchor="end" fill="#8f97a3" font-size="11.5" font-family="Figtree,system-ui">${l}</text>`});
  {const d=new Date(from);d.setDate(1);d.setMonth(d.getMonth()+1);const fm=new Intl.DateTimeFormat(undefined,{month:'short'});
    for(;d.getTime()<now;d.setMonth(d.getMonth()+1)){const x=X(d.getTime());g+=`<line x1="${x}" y1="${PT}" x2="${x}" y2="${H-PB}" stroke="rgba(232,236,242,.05)"/><text x="${x+3}" y="${H-8}" fill="#8f97a3" font-size="11" font-family="Figtree,system-ui">${fm.format(d)}</text>`}}
  const YV=v=>PT+(2-v)/2*ih,cl=y=>Math.max(PT,Math.min(H-PB,y));
  const trend=k=>{const days=new Map();for(const e of pts)if(e[k]){const d=dayNum(e.at),o=days.get(d)||{t:0,v:0,n:0};o.t+=e.at;o.v+=BAND[e[k]];o.n++;days.set(d,o)}
    const p=[...days.values()].map(o=>({at:o.t/o.n,v:o.v/o.n}));if(p.length<3)return'';const v=p.map(o=>o.v);
    const sm=v.map((_,i)=>{const w=v.slice(Math.max(0,i-2),Math.min(v.length,i+3));return w.reduce((a,b)=>a+b,0)/w.length});
    const q=p.map((o,i)=>[X(o.at),YV(sm[i])]);let d=`M${q[0][0].toFixed(1)} ${q[0][1].toFixed(1)}`;
    for(let i=0;i<q.length-1;i++){const a=q[i-1]||q[i],b=q[i],c=q[i+1],e2=q[i+2]||c;
      d+=` C${(b[0]+(c[0]-a[0])/6).toFixed(1)} ${cl(b[1]+(c[1]-a[1])/6).toFixed(1)} ${(c[0]-(e2[0]-b[0])/6).toFixed(1)} ${cl(c[1]-(e2[1]-b[1])/6).toFixed(1)} ${c[0].toFixed(1)} ${c[1].toFixed(1)}`}
    return d};
  g+=`<path d="${trend('moodBefore')}" fill="none" stroke="rgba(200,205,212,.42)" stroke-width="1.6" stroke-dasharray="4 5" stroke-linecap="round"/>`;
  g+=`<path d="${trend('moodAfter')}" fill="none" stroke="var(--olive)" stroke-width="2.4" stroke-linecap="round"/>`;
  // each check-in: a ring for how you arrived, a filled dot for how you left
  const hw=Math.max(8,Math.min(18,iw/Math.max(1,pts.length)));
  pts.forEach((e,i)=>{const x=X(e.at);
    const ay=Math.min(e.moodBefore?Y(e.moodBefore):1e9,e.moodAfter?Y(e.moodAfter):1e9);   // the readout sits just above the higher dot
    g+=`<rect class="phit" data-i="${i}" data-y="${ay.toFixed(1)}" x="${(x-hw/2).toFixed(1)}" y="${PT-6}" width="${hw.toFixed(1)}" height="${ih+12}" rx="4"/>`;
    if(e.moodBefore&&e.moodAfter)g+=`<line x1="${x}" y1="${Y(e.moodBefore)}" x2="${x}" y2="${Y(e.moodAfter)}" stroke="rgba(232,236,242,.2)" pointer-events="none"/>`;
    if(e.moodBefore)g+=`<circle cx="${x}" cy="${Y(e.moodBefore)}" r="4.4" fill="none" stroke="${MOODS[e.moodBefore].c}" stroke-width="1.5" pointer-events="none"/>`;
    if(e.moodAfter)g+=`<circle cx="${x}" cy="${Y(e.moodAfter)}" r="3.6" fill="${MOODS[e.moodAfter].c}" pointer-events="none"/>`});
  const key=`<div class="pkey" aria-label="Mood colours">${MOOD_KEY.map(m=>`<span><i style="--c:${MOODS[m].c}"></i>${MOODS[m].l}</span>`).join('')}</div>`;
""" + lift_themes_feels + r"""  // week: every square is one check-in
  const byDay=DAYS.map(()=>[]);pts.forEach((e,i)=>{const d=(new Date(e.at).getDay()+6)%7;byDay[d].push(i)});
  const avg=a=>a.reduce((s,i)=>s+BAND[val(pts[i])],0)/a.length,rated=byDay.map((a,i)=>({i,n:a.length,v:a.length?avg(a):null})).filter(d=>d.n>=2);
  let wk='';if(rated.length>=3){const lo=rated.reduce((a,b)=>b.v<a.v?b:a),hi=rated.reduce((a,b)=>b.v>a.v?b:a);
    if(hi.v-lo.v>=.5)wk=`${fWeek.format(new Date(2024,0,lo.i+1))}s tend to be your lowest, and ${fWeek.format(new Date(2024,0,hi.i+1))}s your highest. `}
  const week=`<div class="pcard pwk"><h3>Your week</h3><p class="pn">Each square is one check-in, coloured by how you felt when you finished writing (or when you started, if that’s all you noted). The newest is on top. ${touch?'Tap':'Point at'} a square to see that day.</p><div class="pweek">${DAYS.map((d,i)=>`<div><div class="d">${d}</div><div class="col">${byDay[i].slice(-7).map(k=>`<i data-i="${k}" style="--c:${MOODS[val(pts[k])].c}"></i>`).join('')}</div></div>`).join('')}</div>${key}<p class="pfoot">${wk}${pts.length<20?'It’s still early, so treat this as a hint rather than a verdict.':''}</p><div class="ptip" hidden role="status"></div></div>`;
  const rng=`<div class="prange"><div class="seg" role="group" aria-label="Range">${[['month','Month'],['8w','8 weeks'],['all','All']].map(([k,l])=>`<button type="button" data-r="${k}" aria-pressed="${k===patRange}">${l}</button>`).join('')}</div>${narrow()?'':`<button type="button" class="btn small pwide" aria-pressed="${wide}">${wide?'Back to the side panel':'Expand'}</button>`}</div>`;
  const chart=`<div class="pcard pchart"><h3>How you’ve been</h3><p class="pn">Every check-in is a pair: a ring for how you felt when you started writing, and a filled dot for how you felt afterwards. The two lines follow your usual drift. ${touch?'Tap':'Point at'} a check-in to see that day.</p><svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Your moods over time">${g}</svg>
    <div class="plegend"><span><i class="ring"></i>Arriving: how you felt when you started</span><span><i class="dot"></i>Leaving: how you felt afterwards</span></div><div class="plegend"><span><i class="dash"></i>Usual arriving</span><span><i class="line"></i>Usual leaving</span></div>${key}<div class="ptip" hidden role="status"></div></div>`;
  host.innerHTML=`<div class="pat">${rng}${chart}${lift}${week}${themes}${feels}<p class="pfoot">Patterns come only from what’s saved on this device. They show what you were writing about, not what caused how you felt.</p></div>`;
  $$('.prange [data-r]',host).forEach(b=>b.addEventListener('click',()=>{patRange=b.dataset.r;renderPatterns()}));
  const pw=$('.pwide',host);if(pw)pw.addEventListener('click',()=>{setPatWide(!patWide);renderPatterns();host.scrollTop=0});
  wireTips($('.pchart',host),pts);wireTips($('.pwk',host),pts)}
addEventListener('resize',(()=>{let t=0;return()=>{clearTimeout(t);t=setTimeout(()=>{if(narrow()&&patWide)setPatWide(false);if(page==='memories'&&memView==='patterns')renderPatterns()},180)}})());"""
s = s[:i] + new + s[j:]
# the wide view ends when you leave Patterns or close the panel
rep("function setMemView(v){memView=v;", "function setMemView(v){memView=v;if(v!=='patterns'&&patWide)setPatWide(false);")
rep("  if(name==='memories'){showList();renderMemories();setMemView(memView)}",
    "  if(name!=='memories'&&patWide)setPatWide(false);\n  if(name==='memories'){showList();renderMemories();setMemView(memView)}")

rep("</style>", """
/* ---------- Patterns: key, tips, wide view ---------- */
.pcard{position:relative}
body[data-patwide] .dock{opacity:0;pointer-events:none}
.plegend+.plegend{margin-top:6px}
.prange{display:flex;align-items:center;justify-content:space-between;gap:10px;flex-wrap:wrap}
.phit{fill:transparent;cursor:pointer}
.phit.on,.phit:hover{fill:rgba(232,236,242,.07)}
.plegend i.ring{width:9px;height:9px;border:1.5px solid var(--ink-2);border-radius:50%;border-top-width:1.5px}
.plegend i.dot{width:8px;height:8px;border:0;border-radius:50%;background:var(--ink-2)}
.plegend i.line{border-top:2.4px solid var(--olive)}
.pkey{display:flex;flex-wrap:wrap;gap:6px 14px;margin-top:10px;font-size:12px;color:var(--ink-2)}
.pkey span{display:inline-flex;align-items:center;gap:6px}
.pkey i{display:block;width:10px;height:10px;border-radius:3px;background:var(--c)}
.pweek .col i{cursor:pointer;transition:transform .12s}
.pweek .col i.on{outline:2px solid var(--ink);outline-offset:1px}
@media (hover:hover){.pweek .col i:hover{transform:scaleX(1.12)}}
.ptip{position:absolute;z-index:5;transform:translate(-50%,calc(-100% - 10px));width:max-content;max-width:260px;padding:10px 12px;border-radius:12px;
  background:var(--glass-strong);border:1px solid var(--line-2);box-shadow:0 10px 30px rgba(0,0,0,.45);-webkit-backdrop-filter:blur(14px);backdrop-filter:blur(14px);
  font-size:13px;line-height:1.4;color:var(--ink)}
.ptip.below{transform:translate(-50%,10px)}
.ptip[hidden]{display:none}
.ptip small{display:block;color:var(--ink-3);font-size:11.5px;margin-bottom:4px}
.ptip b{display:flex;align-items:center;gap:6px;font-weight:600}
.ptip b i{display:block;width:9px;height:9px;border-radius:50%;flex:none}
.ptip b i.ring{border:1.5px solid var(--c)}
.ptip b i.dot{background:var(--c)}
.ptip span{display:block;color:var(--ink-2);margin-top:4px}
.ptip .ptopen{margin-top:8px;border:0;background:none;padding:0;color:var(--olive);font:600 12.5px/1 var(--ui);cursor:pointer}
@media (min-width:761px){
  .sheet[data-wide="true"]{width:min(1080px,calc(100vw - 36px - var(--sa-r,0px)))}
  .sheet[data-wide="true"] .pat{display:grid;grid-template-columns:1fr 1fr;align-items:start}
  .sheet[data-wide="true"] .pat>.prange,.sheet[data-wide="true"] .pat>.pchart,.sheet[data-wide="true"] .pat>.pcols,.sheet[data-wide="true"] .pat>.pfoot{grid-column:1/-1}
}
</style>""")
open(dst, 'w').write(s)
print('patterns ok', len(s))
