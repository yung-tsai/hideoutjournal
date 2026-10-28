"""Your van: two-tone paint and gear that open up with days journaled (not entry count).
   python3 van.py <in.html> <out.html>"""
import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__)) + '/'   # src/
A = HERE + '../assets/'   # art, sound and scene data
import sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n: sys.exit(f'van.py: expected {n} got {c}: {a[:90]!r}')
    s = s.replace(a, b)

# ---------- state ----------
rep("  meta:{lastInput:'talk',savedTotal:0,draft:'',demoIdx:0},\n  dev:{",
    "  meta:{lastInput:'talk',savedTotal:0,draft:'',demoIdx:0},\n"
    "  van:{paint:'silver',custom:'#5f8a8b',roof:'none',firstRoof:null,tire:false,ladder:false,seen:-1,viewed:0},\n  dev:{")
rep("    meta:{...d.meta,...s.meta},dev:{...d.dev,...s.dev}}}catch(e){storageOK=false;return d}}",
    "    meta:{...d.meta,...s.meta},van:{...d.van,...(s.van||{})},dev:{...d.dev,...s.dev}}}catch(e){storageOK=false;return d}}")
# backups carry the van too
rep("entries:state.entries,tasks:state.tasks,rv:state.rv,settings:state.settings}",
    "entries:state.entries,tasks:state.tasks,rv:state.rv,van:state.van,settings:state.settings}")
rep("  state.entries.sort((a,b)=>b.at-a.at);state.meta.savedTotal=Math.max(state.meta.savedTotal||0,state.entries.length);persist();updateCustDot();renderSettings();",
    "  if(d.van&&typeof d.van==='object')state.van={...state.van,...d.van,seen:state.van.seen,viewed:state.van.viewed};\n"
    "  state.entries.sort((a,b)=>b.at-a.at);state.meta.savedTotal=Math.max(state.meta.savedTotal||0,state.entries.length);\n"
    "  state.van.seen=Math.max(state.van.seen,vanTop());persist();applyVan();updateCustDot();renderSettings();   // restored days open things quietly, no toast")

# ---------- the old placeholder bits ----------
rep("function updateCustDot(){$('#custDot').hidden=!newUnlocks().length}",
    "function updateCustDot(){$('#custDot').hidden=!(vanTop()>(state.van.viewed||0))}")
i = s.index("/* ---------- Your van (placeholder until van options return) ---------- */")
j = s.index("$('#toastSee').addEventListener('click',", i)
s = s[:i] + "/*@@VANUI@@*/\n" + s[j:]
rep("<small>New van option unlocked</small>", "<small>Your van</small>")
# dev: simulate days journaled
rep("seg('sim',[['null','Real ('+state.meta.savedTotal+')'],...[0,1,2,3,4,5,6,7,8].map(n=>[n,String(n)])],'Journal count for unlocks')",
    "seg('sim',[['null','Real ('+realDays()+')'],...[0,1,3,5,7,14,21,30].map(n=>[n,String(n)])],'Days journaled, for van unlocks')")
rep("if(k==='sim'){updateCustDot();if(page==='customize')renderCustomize()}",
    "if(k==='sim'){applyVan();announceUnlocks();updateCustDot();if(page==='customize')renderCustomize()}")

ui = r"""/* ==========================================================================
   Your van. Things open up with days journaled, not entries: five entries in
   one sitting still count as one day, and a gap never takes anything away.
   ========================================================================== */
const VAN_COLOURS=[['silver',null,'Silver',0],['sage','#7d9a6e','Sage',1],['sky','#6f93b8','Sky',1],['brick','#a8503c','Brick',1],
  ['mustard','#d9a23a','Mustard',5],['cream','#e2d4a8','Cream',5],['charcoal','#3a4048','Charcoal',5]];
const VAN_STEPS=[
  {d:1,key:'paint',line:'First entry down. Your van’s earned a fresh coat of paint.',btn:'Pick a colour',next:'a fresh coat of paint'},
  {d:3,key:'tire',line:'Three days in and not tired yet. Here’s a spare.',btn:'Take a look',next:'a spare tire, for the days you’re running a little flat',equip:{tire:true}},
  {d:5,key:'paint2',line:'Five days in. A few more colours in the paint shed.',btn:'Take a look',next:'three more colours'},
  {d:7,key:'ladder',line:'One week in. You’re climbing the ladder.',btn:'Take a look',next:'a ladder',equip:{ladder:true}},
  {d:14,key:'roof',line:'Two weeks. Time to raise the roof: canoe or roof box?',btn:'Choose',next:'something for the roof'},
  {d:21,key:'roof2',line:'Three weeks. There’s room up top for the other one too.',btn:'Take a look',next:'a second choice for the roof'},
  {d:30,key:'wheel',line:'A month at the Hideout. Paint it any colour you like.',btn:'Pick a colour',next:'any colour you like'}];
const ROOFS={canoe:'Canoe',roofbox:'Roof box'};
const dayKey=t=>{const d=new Date(t);return d.getFullYear()*10000+(d.getMonth()+1)*100+d.getDate()};
function realDays(){const k=new Set();for(const e of state.entries){if(!e||typeof e.at!=='number')continue;k.add(dayKey(e.at));for(const m of (e.more||[]))if(m&&m.at)k.add(dayKey(m.at))}return k.size}
const VAN_TEST_ALL=true;   // TESTING ONLY: everything open while Kyoto88 checks the art. Set to false before anyone else uses the app.
function daysJournaled(){return state.dev.sim!=null?state.dev.sim:VAN_TEST_ALL?Math.max(30,realDays()):realDays()}
const vanEarned=()=>{const n=daysJournaled();return VAN_STEPS.filter(x=>n>=x.d)};
const vanTop=()=>vanEarned().reduce((m,x)=>Math.max(m,x.d),0);
const vanHas=key=>vanEarned().some(x=>x.key===key);
function roofChoices(){const n=daysJournaled(),v=state.van;if(n<14)return[];if(n>=21||!v.firstRoof)return['canoe','roofbox'];return[v.firstRoof]}
function paintHex(){const v=state.van,n=daysJournaled();
  if(v.paint==='custom')return n>=30?v.custom:null;
  const c=VAN_COLOURS.find(c=>c[0]===v.paint);return c&&n>=c[3]?c[1]:null}
function applyVan(){const v=state.van;
  Van.set({paint:paintHex(),roof:roofChoices().includes(v.roof)?v.roof:'none',tire:!!v.tire&&vanHas('tire'),ladder:!!v.ladder&&vanHas('ladder')})}
// a first look for anyone who already has entries: what they've earned is simply there, with a dot on Your van, no toast
if(state.van.seen<0){state.van.seen=vanTop();persist()}

/* how a colour will really look on the van: the paint is softened to suit the scene */
const swatchCss=hex=>{const r=Van.ramp(hex)[4];return `rgb(${r.map(v=>Math.round(v*255)).join(',')})`};
function renderCustomize(){
  const v=state.van,n=daysJournaled(),next=VAN_STEPS.find(x=>n<x.d);
  v.viewed=Math.max(v.viewed||0,vanTop());persist();updateCustDot();
  let h=`<div class="vnext"><b>${n} ${n===1?'day':'days'} of journaling.</b> ${next?`Next, after ${next.d===1?'your first entry':next.d+' days'}: ${next.next}.`:'You’ve opened everything for now. More is on the way.'}</div>`;
  if(vanHas('paint')){
    const sw=VAN_COLOURS.filter(c=>n>=c[3]).map(([k,hex,name])=>`<button type="button" class="vsw${k==='silver'?' silver':''}" data-paint="${k}" aria-pressed="${v.paint===k}" ${hex?`style="--c:${swatchCss(hex)}"`:''}><i aria-hidden="true"></i><span>${name}</span></button>`).join('');
    const own=n>=30?`<label class="vsw own" aria-pressed="${v.paint==='custom'}"><i aria-hidden="true" style="--c:${swatchCss(v.custom)}"><input type="color" id="vanOwn" value="${v.custom}" aria-label="Your own colour"></i><span>Your own</span></label>`:'';
    h+=`<section class="vsec"><h3>Paint</h3><div class="swatches">${sw}${own}</div><p class="vfine">The lower half takes the colour; the top stays white.${n>=30?' Bright picks are softened to suit the scene.':''}</p></section>`}
  const roofs=roofChoices();
  if(roofs.length){const choosing=n<21&&!v.firstRoof;
    h+=`<section class="vsec"><h3>Roof</h3>${choosing?'<p class="vfine" style="margin:-2px 0 10px">Pick one now. The other opens at 21 days.</p>':''}<div class="seg" role="group" aria-label="Roof">${(choosing?[]:['none']).concat(roofs).map(k=>`<button type="button" data-roof="${k}" aria-pressed="${v.roof===k}">${k==='none'?'Nothing':ROOFS[k]}</button>`).join('')}</div></section>`}
  const gear=[['tire','Spare tire','On the back door.'],['ladder','Ladder','Up the back corner to the roof.']].filter(g=>vanHas(g[0]));
  if(gear.length)h+=`<section class="vsec"><h3>Gear</h3>${gear.map(([k,name,sub])=>`<div class="toggle-row"><div><b>${name}</b><span>${sub}</span></div><button class="switch" type="button" role="switch" data-gear="${k}" aria-checked="${!!v[k]}" aria-label="${name}"></button></div>`).join('')}</section>`;
  $('#custBody').innerHTML=h;
  $$('#custBody [data-paint]').forEach(b=>b.addEventListener('click',()=>{v.paint=b.dataset.paint;persist();applyVan();renderCustomize()}));
  const own=$('#vanOwn');if(own){
    own.addEventListener('input',()=>{v.paint='custom';v.custom=own.value;own.parentElement.style.setProperty('--c',swatchCss(own.value));
      $$('#custBody .vsw').forEach(x=>x.setAttribute('aria-pressed',String(x.classList.contains('own'))));applyVan()});
    own.addEventListener('change',()=>persist())}
  $$('#custBody [data-roof]').forEach(b=>b.addEventListener('click',()=>{const k=b.dataset.roof;v.roof=k;if(k!=='none'&&!v.firstRoof)v.firstRoof=k;persist();applyVan();renderCustomize()}));
  $$('#custBody [data-gear]').forEach(b=>b.addEventListener('click',()=>{const k=b.dataset.gear;v[k]=!v[k];persist();applyVan();b.setAttribute('aria-checked',String(!!v[k]))}));
}
/* ---------- the unlock note: one quiet line after saving ---------- */
let toastTimer=0;
function announceUnlocks(){const earned=vanEarned(),fresh=earned.filter(x=>x.d>state.van.seen);
  if(!fresh.length){state.van.seen=Math.min(state.van.seen,vanTop());return}   // (lowering the dev counter rewinds quietly)
  state.van.seen=vanTop();for(const x of fresh)if(x.equip)Object.assign(state.van,x.equip);
  persist();applyVan();updateCustDot();if(page==='customize')renderCustomize();
  const x=fresh[fresh.length-1];$('#toastName').textContent=x.line;$('#toastSee').textContent=x.btn;
  const t=$('#toast');t.dataset.show='true';Sound.chime(true);clearTimeout(toastTimer);toastTimer=setTimeout(()=>{t.dataset.show='false'},12000)}
applyVan();updateCustDot();
"""
rep("/*@@VANUI@@*/\n", ui)
# the note's line can be a full sentence now
rep(".toast .tt b{font:600 15px/1.3 var(--ui)}", ".toast .tt b{font:600 15px/1.35 var(--ui);white-space:normal;max-width:min(420px,62vw)}")
rep("</style>", """
/* ---------- Your van ---------- */
.vnext{padding:12px 14px;border-radius:12px;background:var(--paper-2);color:var(--ink-2);font-size:14px;line-height:1.5;margin:2px 0 18px}
.vnext b{color:var(--ink);font-weight:600}
.vsec{margin:0 0 20px}
.vsec h3{font:600 11.5px/1 var(--ui);letter-spacing:.14em;text-transform:uppercase;color:var(--ink-3);margin:0 0 12px}
.vfine{font-size:12.5px;color:var(--ink-3);margin:10px 0 0;line-height:1.45}
.swatches{display:flex;flex-wrap:wrap;gap:12px 10px}
.vsw{display:flex;flex-direction:column;align-items:center;gap:6px;width:58px;border:0;background:none;padding:0;cursor:pointer;color:var(--ink-2);font:500 12px/1.2 var(--ui)}
.vsw i{position:relative;display:block;width:42px;height:42px;border-radius:50%;
  background:linear-gradient(to bottom,#ece7da 0 44%,rgba(0,0,0,.18) 44% 48%,var(--c,#9aa3ad) 48% 100%);box-shadow:inset 0 0 0 1px rgba(0,0,0,.28)}
.vsw.silver i{background:linear-gradient(160deg,#b9c0c8,#7f8893);}
.vsw[aria-pressed="true"] i{outline:2px solid var(--ink);outline-offset:3px}
.vsw[aria-pressed="true"]{color:var(--ink)}
.vsw:focus-visible{outline:none}.vsw:focus-visible i{outline:2px solid var(--olive);outline-offset:3px}
.vsw.own i{overflow:hidden}
.vsw.own input{position:absolute;inset:-8px;width:calc(100% + 16px);height:calc(100% + 16px);opacity:0;cursor:pointer;border:0;padding:0}
.vsw.own i::after{content:"+";position:absolute;right:-2px;bottom:-2px;width:16px;height:16px;border-radius:50%;background:var(--ink);color:var(--paper);font:600 12px/16px var(--ui);text-align:center}
.vsec .toggle-row{padding:10px 0}
</style>""")
rep("state.dev=keep.dev;persist();buildRV();updateCustDot();renderSettings()});","state.dev=keep.dev;persist();buildRV();applyVan();updateCustDot();renderSettings()});")
rep("state.dev=dev;persist();buildRV();updateCustDot();updateDock();","state.dev=dev;persist();buildRV();applyVan();updateCustDot();updateDock();")
rep("dev(o){Object.assign(state.dev,o);persist();applyWorld();updateCustDot();","dev(o){Object.assign(state.dev,o);persist();applyWorld();if('sim' in o){applyVan();announceUnlocks()}updateCustDot();")
open(dst, 'w').write(s)
print('van ok', len(s))
