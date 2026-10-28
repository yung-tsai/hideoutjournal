"""Bundle: one bottom bar, resurfacing strip, five-mood vocabulary, Patterns, restore from backup.
   python3 bundle.py <in.html> <out.html>"""
import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__)) + '/'   # src/
A = HERE + '../assets/'   # art, sound and scene data
import sys, re
src, dst = sys.argv[1], sys.argv[2]
s = open(src).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n: sys.exit(f'bundle.py: expected {n} got {c}: {a[:80]!r}')
    s = s.replace(a, b)
def one(pat, flags=re.S):
    m = re.findall(pat, s, flags)
    if not m: sys.exit(f'bundle.py: no match for {pat[:60]!r}')
    return m[0]

# ---------- moods: Okay joins the vocabulary everywhere ----------
rep("const MOODS={calm:{l:'Calm',c:'#7c9a86'},happy:{l:'Happy',c:'#d0a03e'},low:{l:'Low',c:'#7d8bb0'},frustrated:{l:'Frustrated',c:'#c0714a'}};",
    "const MOODS={calm:{l:'Calm',c:'#7c9a86'},happy:{l:'Happy',c:'#d0a03e'},okay:{l:'Okay',c:'#a39e94'},low:{l:'Low',c:'#7d8bb0'},frustrated:{l:'Frustrated',c:'#c0714a'}};")
rep('- mood: exactly one of "calm", "happy", "low", "frustrated", whichever fits best.',
    '- mood: exactly one of "happy", "calm", "okay", "low", "frustrated", whichever fits best ("okay" for an ordinary, neutral day).')
rep("const mood=['calm','happy','low','frustrated'].includes(r.mood)?r.mood:local.mood;",
    "const mood=['calm','happy','okay','low','frustrated'].includes(r.mood)?r.mood:local.mood;")
rep("let mood='calm',best=.5;", "let mood='okay',best=.5;")
rep("const ADJ={calm:'A quiet',low:'A heavy',frustrated:'A rough',happy:'A good'};",
    "const ADJ={calm:'A quiet',okay:'An ordinary',low:'A heavy',frustrated:'A rough',happy:'A good'};")
rep("    calm:['What helped today feel steady?',",
    "    okay:['What took up most of today?','Anything small worth noticing?'],\n    calm:['What helped today feel steady?',")

# ---------- one bottom bar: Memories · Reflect · Tasks; no logo; Your van moves to Settings ----------
reflect = one(r'<button class="start" type="button" data-start="reflect"[^>]*>.*?</button>')
memtab  = one(r'<button class="tab" type="button" data-tab="memories">.*?</button>')
tasktab = one(r'<button class="tab" type="button" data-tab="tasks">.*?</button>')
m = re.search(r'  <div class="dock-row">\n.*?\n  </div>\n</div>', s, re.S)
if not m: sys.exit('bundle.py: dock-row not found')
s = s[:m.start()] + '  <div class="dock-row">\n    ' + memtab + '\n    ' + reflect + '\n    ' + tasktab + '\n  </div>\n</div>' + s[m.end():]
rep("$$('.tab').forEach(t=>t.addEventListener('click',()=>openPage(t.dataset.tab==='home'?null:t.dataset.tab)));",
    "$$('.tab').forEach(t=>t.addEventListener('click',()=>openPage(t.dataset.tab==='home'?null:(t.closest('.dock')&&page===t.dataset.tab?null:t.dataset.tab))));   // the bar's buttons toggle")
rep('      <section class="sgroup"><h3>Your data</h3>',
    '      <section class="sgroup"><h3>Your van</h3>\n'
    '        <div class="toggle-row"><div><b>Looks for your van</b><span>New paint and gear open up as you journal.</span></div>'
    '<button class="btn small" type="button" id="custBtn" style="position:relative">Open<i class="dotnew" id="custDot" hidden></i></button></div>\n      </section>\n'
    '      <section class="sgroup"><h3>Your data</h3>')

# ---------- "A week ago today" grows out of the top of the bar ----------
strip = one(r'<div class="toast resurf" id="resurf".*?</button></div>')
rep(strip, '')
rep('<div class="dock" id="dock">\n  <p class="dock-q" id="dockQ">How did today go?</p>\n',
    '<div class="dock" id="dock">\n  <p class="dock-q" id="dockQ">How did today go?</p>\n  ' + strip.replace('class="toast resurf"', 'class="strip"') + '\n')

# ---------- Patterns, beside the entries ----------
rep('<div class="phead"><div><h2 id="memH">Memories</h2></div>',
    '<div class="phead"><div><h2 id="memH">Memories</h2><div class="seg memseg" role="group" aria-label="View"><button type="button" data-mv="entries" aria-pressed="true">Entries</button><button type="button" data-mv="patterns" aria-pressed="false">Patterns</button></div></div>')
rep('<div class="pbody" id="memBody"></div>', '<div class="pbody" id="memBody"></div>\n      <div class="pbody" id="patBody" style="display:none"></div>')
rep("if(name==='memories'){showList();renderMemories()}", "if(name==='memories'){showList();renderMemories();setMemView(memView)}")
rep('<span>${esc(fFull.format(d))} · ${esc(fTime.format(d))}</span>${moodHTML(e)}',
    '<span>${esc(fFull.format(d))} · ${esc(fTime.format(d))}</span>${moodHTML(e)}${checkinHTML(e)}')

# ---------- restore from a backup ----------
rep('<button class="btn small" type="button" id="backupBtn">Download a backup</button>',
    '<button class="btn small" type="button" id="backupBtn">Download a backup</button><button class="btn small" type="button" id="restoreBtn">Restore from a backup</button>'
    '<input type="file" id="restoreFile" accept="application/json,.json" hidden>')
rep("const filename='talio-backup-'+stamp+'.json'", "const filename='hideout-backup-'+stamp+'.json'")

# ---------- demo data gets check-ins, so Patterns can be tried ----------
rep("if(done){done.done=true;done.doneAt=now}\n  persist();updateCustDot()}",
    "if(done){done.done=true;done.doneAt=now}\n  addDemoCheckins();persist();updateCustDot()}")

# ---------- styles ----------
rep('</style>', r'''
/* ---------- one bottom bar ---------- */
.top .brand,.top .tabs{display:none}
.top{display:flex;justify-content:flex-end}   /* just sound and settings, top right */
.bottomnav{display:none!important}
.dock .dock-row{gap:4px}
.dock .tab{display:flex;align-items:center;gap:8px;border:0;background:none;padding:12px 16px;border-radius:var(--r);font:500 14.5px/1 var(--ui);color:var(--ink-2);cursor:pointer;transition:background .2s,color .2s}
.dock .tab svg{width:18px;height:18px}
.dock .tab:hover{background:var(--paper-2);color:var(--ink)}
.dock .tab[aria-current="page"]{background:var(--paper-3);color:var(--ink)}
/* the resurfacing strip, attached to the top of the bar */
.strip{display:none;align-self:stretch;width:0;min-width:100%;box-sizing:border-box;align-items:center;gap:10px;margin-bottom:-11px;padding:10px 8px 14px 16px;
  border-radius:var(--r) var(--r) 0 0;background:var(--frost);border:1px solid var(--frost-line);border-bottom:0;-webkit-backdrop-filter:blur(12px);backdrop-filter:blur(12px)}
.strip[data-show="true"]{display:flex;animation:stripIn .45s cubic-bezier(.2,.8,.2,1)}
.strip .tt{display:flex;flex-direction:column;gap:3px;min-width:0;flex:1}
.strip small{color:var(--olive);font:600 11px/1 var(--ui);letter-spacing:.07em;text-transform:uppercase}
.strip b{font:500 15px/1.2 var(--serif);color:var(--ink)}
.strip span{font-size:13px;color:var(--ink-2);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.strip .btn{border-radius:999px;white-space:nowrap}
.strip .x{border:0;background:none;color:var(--ink-3);width:32px;height:32px;border-radius:999px;display:grid;place-items:center;cursor:pointer}
.strip .x:hover{background:var(--paper-2);color:var(--ink)}.strip .x svg{width:12px;height:12px}
.dock:has(.strip[data-show="true"]) .dock-q{display:none}
.dock:has(.strip[data-show="true"]) .dock-row{border-top-left-radius:6px;border-top-right-radius:6px}
@keyframes stripIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
@media (prefers-reduced-motion:reduce){.strip[data-show="true"]{animation:none}}
@media (max-width:760px){
  .dock{bottom:calc(10px + var(--sa-b))}
  .dock .dock-row{gap:2px}
  .dock .tab{flex:0 0 auto;flex-direction:column;gap:4px;padding:8px 10px;min-width:74px;font-size:12px}
  .dock .tab svg{width:20px;height:20px}
  .sheet{bottom:calc(84px + var(--sa-b))}
  .strip{padding:9px 6px 13px 12px}
}
/* ---------- Patterns ---------- */
.memseg{display:flex;margin-top:10px}
.memseg button{padding:7px 14px;font-size:13.5px}
.pat{display:flex;flex-direction:column;gap:14px;padding-top:4px}
.pcard{background:var(--paper-2);border:1px solid var(--line);border-radius:14px;padding:16px}
.pcard h3{margin:0 0 2px;font:400 19px/1.25 var(--serif)}
.pcard .pn{margin:0 0 12px;color:var(--ink-3);font-size:13px}
.pcard svg{display:block;width:100%;height:auto;overflow:visible}
.plegend{display:flex;gap:14px;flex-wrap:wrap;margin-top:10px;font-size:12px;color:var(--ink-2)}
.plegend span{display:inline-flex;align-items:center;gap:7px}
.plegend i{display:block;width:16px;height:0;border-top:2px solid var(--olive)}
.plegend i.dash{border-top:2px dashed rgba(200,205,212,.5)}
.plift{display:flex;gap:16px;align-items:center;flex-wrap:wrap}
.plift .big{font:400 38px/1 var(--serif);color:var(--olive)}
.plift p{margin:0;color:var(--ink-2);font-size:14px;line-height:1.45;flex:1;min-width:180px}
.pweek{display:grid;grid-template-columns:repeat(7,1fr);gap:6px;text-align:center}
.pweek .d{font-size:11.5px;color:var(--ink-3);margin-bottom:6px}
.pweek .col{display:flex;flex-direction:column-reverse;gap:3px;height:84px;padding:4px;border-radius:8px;background:rgba(0,0,0,.14)}
.pweek .col i{display:block;height:10px;border-radius:3px;background:var(--c)}
.pfoot{margin:10px 0 0;font-size:12.5px;color:var(--ink-3);line-height:1.45}
.pcols{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.ptheme{margin:0 0 9px}
.ptheme .r1{display:flex;justify-content:space-between;gap:8px;font-size:14px}
.ptheme small{color:var(--ink-3);font-size:12px;white-space:nowrap}
.ptheme .bar{height:5px;border-radius:999px;background:rgba(0,0,0,.18);margin-top:5px;overflow:hidden}
.ptheme .bar i{display:block;height:100%;border-radius:999px;background:var(--c)}
.pchips{display:flex;gap:6px;flex-wrap:wrap}
.pchips span{padding:6px 11px;border-radius:999px;background:rgba(0,0,0,.16);font-size:13px;color:var(--ink-2)}
.pchips b{color:var(--ink);font-weight:500}
.pempty{padding:18px 4px}
.pempty .pt{font:400 21px/1.3 var(--serif);margin:0 0 8px}
.pbar{height:6px;border-radius:999px;background:var(--paper-2);overflow:hidden;margin-top:12px;max-width:260px}
.pbar i{display:block;height:100%;background:var(--olive);border-radius:999px}
.prange{display:flex;justify-content:flex-end}
@media (max-width:760px){.pcols{grid-template-columns:1fr}.plift .big{font-size:32px}}
</style>''')

# ---------- behaviour ----------
glue = r'''
/* ---------- the bundle: Patterns, restore, and a few hooks ---------- */
const BAND_C=['#7d8bb0','#a39e94','#8fae8c'],DAYS=['Mon','Tue','Wed','Thu','Fri','Sat','Sun'];
const OFF={happy:-6,calm:6,frustrated:-6,low:6,okay:0};   // two moods share a band; nudge them apart a little
function checkinHTML(e){if(!e.moodBefore&&!e.moodAfter)return'';const L=k=>MOODS[k]?MOODS[k].l.toLowerCase():k;
  const t=(e.moodBefore?'arrived '+L(e.moodBefore)+(e.feelBefore?' ('+e.feelBefore+')':''):'')+(e.moodBefore&&e.moodAfter?', ':'')+(e.moodAfter?'left '+L(e.moodAfter)+(e.feelAfter?' ('+e.feelAfter+')':''):'');
  return'<span>'+esc(t.charAt(0).toUpperCase()+t.slice(1))+'</span>'}
let memView='entries',patRange='8w';
function setMemView(v){memView=v;$$('.memseg button').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.mv===v)));
  const pat=v==='patterns',tr=$('#memList .tools-row');if(tr)tr.style.display=pat?'none':'';$('#memBody').style.display=pat?'none':'';$('#patBody').style.display=pat?'':'none';
  if(pat)renderPatterns()}
$$('.memseg button').forEach(b=>b.addEventListener('click',()=>setMemView(b.dataset.mv)));
const STOP=new Set(('the and that this with have just about from they them then than when what were been really today tonight morning evening night after before into over some more much very also still back again feel felt feeling think thought know want going gonna made make like little bit kind sort things thing stuff because could would should there their here where which while your youre mine ours ourselves myself something nothing everything anything always never ever only even well good great nice okay fine long lots time times week weekend days dont didnt cant wasnt isnt its im ive id spent moved loud whole another lately already came went took late early every since said told getting trying tried messy').split(' '));
function words(t){return[...new Set((t.toLowerCase().replace(/[’']/g,'').match(/[a-z]{4,}/g)||[]).filter(w=>!STOP.has(w)))]}
function renderPatterns(){const host=$('#patBody'),all=state.entries.filter(e=>!e.archived&&(e.moodBefore||e.moodAfter)),MIN=5;
  if(all.length<MIN){host.innerHTML=`<div class="pempty"><p class="pt">Your patterns will show up here.</p><p class="note">Each time you note how you are, before or after writing, it adds a point. Once there are a few, you’ll see your highs and lows, whether writing leaves you lighter, and what tends to come up on your good and hard days.</p><div class="pbar"><i style="width:${all.length/MIN*100}%"></i></div><p class="note" style="margin-top:8px">${all.length} of ${MIN} check-ins so far</p></div>`;return}
  const now=Date.now(),DAY=864e5,span={month:30,'8w':56,all:0}[patRange],first=Math.min(...all.map(e=>e.at));
  const from=span?Math.max(now-span*DAY,first-DAY):first-DAY,pts=all.filter(e=>e.at>=from).sort((a,b)=>a.at-b.at);
  const val=e=>e.moodAfter||e.moodBefore;
  // chart
  const W=640,H=212,PL=62,PR=10,PT=14,PB=28,iw=W-PL-PR,ih=H-PT-PB,X=t=>PL+(t-from)/Math.max(1,now-from)*iw,Y=m=>PT+(2-BAND[m])/2*ih+(OFF[m]||0);
  let g='';['High','Neutral','Low'].forEach((l,i)=>{const y=PT+i/2*ih;g+=`<line x1="${PL}" y1="${y}" x2="${W-PR}" y2="${y}" stroke="rgba(232,236,242,.09)"/><text x="${PL-10}" y="${y+4}" text-anchor="end" fill="#8f97a3" font-size="11.5" font-family="Figtree,system-ui">${l}</text>`});
  {const d=new Date(from);d.setDate(1);d.setMonth(d.getMonth()+1);const fm=new Intl.DateTimeFormat(undefined,{month:'short'});
    for(;d.getTime()<now;d.setMonth(d.getMonth()+1)){const x=X(d.getTime());g+=`<line x1="${x}" y1="${PT}" x2="${x}" y2="${H-PB}" stroke="rgba(232,236,242,.05)"/><text x="${x+3}" y="${H-8}" fill="#8f97a3" font-size="11" font-family="Figtree,system-ui">${fm.format(d)}</text>`}}
  // a gentle trend through the points (moods jump between bands, so joining every dot just zigzags)
  const YV=v=>PT+(2-v)/2*ih,cl=y=>Math.max(PT,Math.min(H-PB,y));
  const trend=k=>{const days=new Map();for(const e of pts)if(e[k]){const d=dayNum(e.at),o=days.get(d)||{t:0,v:0,n:0};o.t+=e.at;o.v+=BAND[e[k]];o.n++;days.set(d,o)}
    const p=[...days.values()].map(o=>({at:o.t/o.n,v:o.v/o.n}));if(p.length<3)return'';const v=p.map(o=>o.v);   // one point a day, so close check-ins can't loop the curve
    const sm=v.map((_,i)=>{const w=v.slice(Math.max(0,i-2),Math.min(v.length,i+3));return w.reduce((a,b)=>a+b,0)/w.length});
    const q=p.map((o,i)=>[X(o.at),YV(sm[i])]);let d=`M${q[0][0].toFixed(1)} ${q[0][1].toFixed(1)}`;
    for(let i=0;i<q.length-1;i++){const a=q[i-1]||q[i],b=q[i],c=q[i+1],e2=q[i+2]||c;
      d+=` C${(b[0]+(c[0]-a[0])/6).toFixed(1)} ${cl(b[1]+(c[1]-a[1])/6).toFixed(1)} ${(c[0]-(e2[0]-b[0])/6).toFixed(1)} ${cl(c[1]-(e2[1]-b[1])/6).toFixed(1)} ${c[0].toFixed(1)} ${c[1].toFixed(1)}`}
    return d};
  g+=`<path d="${trend('moodBefore')}" fill="none" stroke="rgba(200,205,212,.42)" stroke-width="1.6" stroke-dasharray="4 5" stroke-linecap="round"/>`;
  g+=`<path d="${trend('moodAfter')}" fill="none" stroke="var(--olive)" stroke-width="2.4" stroke-linecap="round"/>`;
  for(const e of pts){const x=X(e.at);
    if(e.moodBefore&&e.moodAfter)g+=`<line x1="${x}" y1="${Y(e.moodBefore)}" x2="${x}" y2="${Y(e.moodAfter)}" stroke="rgba(232,236,242,.2)"/>`;
    if(e.moodBefore&&!e.moodAfter)g+=`<circle cx="${x}" cy="${Y(e.moodBefore)}" r="3.2" fill="none" stroke="${MOODS[e.moodBefore].c}" stroke-width="1.4"/>`;
    if(e.moodAfter)g+=`<circle cx="${x}" cy="${Y(e.moodAfter)}" r="3.6" fill="${MOODS[e.moodAfter].c}"/>`}
  // lighter
  const both=pts.filter(e=>e.moodBefore&&e.moodAfter),up=both.filter(e=>BAND[e.moodAfter]>BAND[e.moodBefore]).length,down=both.filter(e=>BAND[e.moodAfter]<BAND[e.moodBefore]).length;
  const hardStarts=both.filter(e=>BAND[e.moodBefore]===0),hardLift=hardStarts.filter(e=>BAND[e.moodAfter]>0).length;
  const lift=both.length?`<div class="pcard plift"><div class="big">${up} of ${both.length}</div><p>times you checked in before and after, you left feeling lighter.${hardStarts.length>=2?` On the days you arrived low or frustrated, writing lifted you ${hardLift} of ${hardStarts.length} times.`:''}${down?` ${down===1?'Once':down+' times'} you left heavier, which happens too.`:''}</p></div>`:'';
  // week
  const byDay=DAYS.map(()=>[]);for(const e of pts){const d=(new Date(e.at).getDay()+6)%7;byDay[d].push(val(e))}
  const avg=a=>a.reduce((s,m)=>s+BAND[m],0)/a.length,rated=byDay.map((a,i)=>({i,n:a.length,v:a.length?avg(a):null})).filter(d=>d.n>=2);
  let wk='';if(rated.length>=3){const lo=rated.reduce((a,b)=>b.v<a.v?b:a),hi=rated.reduce((a,b)=>b.v>a.v?b:a);
    if(hi.v-lo.v>=.5)wk=`${fWeek.format(new Date(2024,0,lo.i+1))}s tend to be your lowest, and ${fWeek.format(new Date(2024,0,hi.i+1))}s your highest. `}
  const week=`<div class="pcard"><h3>Your week</h3><p class="pn">Where your check-ins land, day by day.</p><div class="pweek">${DAYS.map((d,i)=>`<div><div class="d">${d}</div><div class="col">${byDay[i].slice(-7).map(m=>`<i style="--c:${MOODS[m].c}" title="${MOODS[m].l}"></i>`).join('')}</div></div>`).join('')}</div><p class="pfoot">${wk}${pts.length<20?'It’s still early, so treat this as a hint rather than a verdict.':''}</p></div>`;
  // themes: what you were writing about on good and hard days
  const good=pts.filter(e=>BAND[val(e)]===2),hard=pts.filter(e=>BAND[val(e)]===0);
  const count=list=>{const c={};for(const e of list)for(const w of words(entryFullText(e)))c[w]=(c[w]||0)+1;return c};
  const cg=count(good),ch=count(hard);
  const top=(a,b,na,nb)=>Object.entries(a).filter(([w,n])=>n>=2&&n/Math.max(1,na)>(b[w]||0)/Math.max(1,nb)*1.3).sort((x,y)=>y[1]-x[1]).slice(0,5);
  const tg=top(cg,ch,good.length,hard.length),th=top(ch,cg,hard.length,good.length);
  const list=(rows,col)=>rows.length?rows.map(([w,n])=>`<div class="ptheme"><div class="r1"><span>${esc(w.charAt(0).toUpperCase()+w.slice(1))}</span><small>${n} ${n===1?'entry':'entries'}</small></div><div class="bar" style="--c:${col}"><i style="width:${Math.min(100,n/Math.max(...rows.map(r=>r[1]))*100)}%"></i></div></div>`).join(''):'<p class="pn">Not enough yet.</p>';
  const themes=`<div class="pcols"><div class="pcard"><h3>On your good days</h3><p class="pn">What you were writing about when you felt best.</p>${list(tg,BAND_C[2])}</div><div class="pcard"><h3>On your hard days</h3><p class="pn">What you were writing about when you felt lowest.</p>${list(th,BAND_C[0])}</div></div>`;
  // the specific words you picked
  const fc={};for(const e of pts)for(const w of [e.feelBefore,e.feelAfter])if(w)fc[w]=(fc[w]||0)+1;
  const fw=Object.entries(fc).sort((a,b)=>b[1]-a[1]).slice(0,10);
  const feels=fw.length?`<div class="pcard"><h3>In your words</h3><p class="pn">The feelings you’ve named most.</p><div class="pchips">${fw.map(([w,n])=>`<span><b>${esc(w)}</b> ×${n}</span>`).join('')}</div></div>`:'';
  const rng=`<div class="prange"><div class="seg" role="group" aria-label="Range">${[['month','Month'],['8w','8 weeks'],['all','All']].map(([k,l])=>`<button type="button" data-r="${k}" aria-pressed="${k===patRange}">${l}</button>`).join('')}</div></div>`;
  host.innerHTML=`<div class="pat">${rng}<div class="pcard"><h3>How you’ve been</h3><p class="pn">Each dot is a check-in. The lines show the general drift: how you’ve tended to arrive, and how you’ve tended to leave.</p><svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Your moods over time">${g}</svg><div class="plegend"><span><i class="dash"></i>Arriving</span><span><i></i>Leaving</span></div></div>${lift}${week}${themes}${feels}<p class="pfoot">Patterns come only from what’s saved on this device. They show what you were writing about, not what caused how you felt.</p></div>`;
  $$('.prange button',host).forEach(b=>b.addEventListener('click',()=>{patRange=b.dataset.r;renderPatterns()}))}

/* restore: merge a backup in without duplicating anything already here */
$('#restoreBtn').addEventListener('click',()=>$('#restoreFile').click());
$('#restoreFile').addEventListener('change',async ev=>{const f=ev.target.files&&ev.target.files[0];ev.target.value='';if(!f)return;
  let d=null;try{d=JSON.parse(await f.text())}catch(_){}
  if(!d||!Array.isArray(d.entries)){renderSettings();backupNote('That file isn’t a Hideout backup.');return}
  const have=new Set(state.entries.map(x=>x.id)),haveT=new Set(state.tasks.map(x=>x.id));let ne=0,nt=0,dup=0;
  for(const x of d.entries){if(!x||!x.id||typeof x.body!=='string'||typeof x.at!=='number')continue;if(have.has(x.id)){dup++;continue}state.entries.push(x);have.add(x.id);ne++}
  for(const t of (Array.isArray(d.tasks)?d.tasks:[])){if(!t||!t.id||typeof t.text!=='string'||haveT.has(t.id))continue;if(!Array.isArray(t.sources))t.sources=[];state.tasks.push(t);haveT.add(t.id);nt++}
  state.entries.sort((a,b)=>b.at-a.at);state.meta.savedTotal=Math.max(state.meta.savedTotal||0,state.entries.length);persist();updateCustDot();renderSettings();
  backupNote(ne||nt?`Restored ${ne} ${ne===1?'memory':'memories'} and ${nt} ${nt===1?'task':'tasks'}${dup?`. ${dup} ${dup===1?'was':'were'} already here`:''}.`:dup?'Everything in that backup is already here.':'That backup was empty.')});

/* demo check-ins: a couple of months of before-and-after moods, so Patterns has something to show */
function addDemoCheckins(){let sd=7;const r=()=>{sd=(sd*16807)%2147483647;return(sd-1)/2147483646},pick=a=>a[Math.floor(r()*a.length)];
  const now=Date.now(),DAY=864e5,down={happy:'calm',calm:'okay',okay:'low',low:'low',frustrated:'frustrated'};
  for(const e of state.entries){if(e.moodBefore||e.concern)continue;e.moodAfter=e.mood;e.moodBefore=r()<.6?down[e.mood]:e.mood;if(r()<.4)e.feelAfter=pick(FEELS[e.moodAfter])}
  const extra=[['happy','Long walk by the river after dinner. Sam came along and we talked the whole way.'],['calm','Slow morning. Coffee on the step and the river was loud from the rain.'],
    ['frustrated','Deadline moved up again at work. Spent the whole afternoon redoing slides.'],['low','Didn’t sleep well. Everything felt heavy and I skipped the gym.'],
    ['okay','Errands, laundry, a long call with the bank. Nothing much else.'],['happy','Cooked a big dinner with Sam and the kids. Loud, messy, really good.'],
    ['calm','Walked the river trail at sunset. Quiet. Needed that.'],['frustrated','Car wouldn’t start this morning, late for work, the meeting ran long.'],
    ['low','Missing my sister lately. Called her but it went to voicemail.'],['okay','Work was fine. Read a little before bed.'],['happy','Finished the chapter I’ve been stuck on for weeks.'],
    ['calm','Rain all day. Made soup and listened to records.'],['frustrated','Another deadline at work and the client changed everything again.'],
    ['low','Tired. Didn’t sleep and the week already feels too long.'],['happy','Walk with Sam by the water, then pizza. Easy evening.'],['okay','Busy day of meetings. Ate at my desk.']];
  for(let i=0;i<22;i++){const [mood,body]=extra[i%extra.length],at=now-(3+Math.floor(r()*53))*DAY-Math.floor(r()*8)*36e5;
    const a=r()<.12?down[mood]:mood,b=r()<.55?down[mood]:mood;const L=Reflector.analyze(body,{style:'curious',n:0,at,input:'write'});
    state.entries.push({id:uid(),at,input:'write',title:L.title,body,reflection:L.reflection,mood,moodBefore:b,moodAfter:a,feelAfter:r()<.45?pick(FEELS[a]):null,concern:false,archived:false,world:{time:pick(['morning','midday','golden','night']),weather:'clear'}});state.meta.savedTotal+=1}
  state.entries.sort((x,y)=>y.at-x.at)}
window.__talio&&Object.assign(window.__talio,{nudge:(k)=>{if(!k||k==='birds')LIFE.nextBirds=0;if(!k||k==='fish')LIFE.nextFish=0;if(k==='star')LIFE.nextStar=0;if(k==='sq'){squirrel=null;nextSq=0}},resurf:()=>showResurface(true),patterns:()=>{openPage('memories');setMemView('patterns')}});
'''
rep("window.__talio&&(window.__talio.fire=()=>Burn);", "window.__talio&&(window.__talio.fire=()=>Burn);\n" + glue)

open(dst, 'w').write(s)
print('bundle ok', len(s))
