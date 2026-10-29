import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__)) + '/'   # src/
A = HERE + '../assets/'   # art, sound and scene data
import sys, re
SRC = A+'talio-home-v6-3d.html'
ART = A+'ghc_src/golden-hour-camp.html'
OUT = HERE+'../build/fragment.html'
old = open(SRC).read()
art = open(ART).read()

def cut(s, a, b):
    i = s.index(a); j = s.index(b, i)
    return s[i:j]

def rep(s, a, b, count=1):
    n = s.count(a)
    if n != count: sys.exit(f'expected {count} got {n}: {a[:90]!r}')
    return s.replace(a, b)

# ---------------- CSS ----------------
css = cut(old, '<style>\n', '</style>')[len('<style>\n'):]
css = re.sub(r':root\{\n.*?\n\}\n', '', css, count=1, flags=re.S)
css = rep(css, '/* The world brings its own light; the interface keeps one warm paper palette in both themes on purpose. */\n@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--ground:#1a1f22}}\n:root[data-theme="dark"]{--ground:#1a1f22}\n', '')
css = rep(css, '/* Talio Home: the low-res 3D pond retreat fills the screen; the product UI sits on top at native resolution.\n   Panels and sheets use warm paper; controls over the scene use frosted paper chips so they read in every time of day. */\n', '')
TOKENS = '''/* Talio river camp: the pixel landscape is the page; the interface floats on it as dark, warm glass that rests away when idle.
   One deliberate dark look in every theme, taken from the scene's dusk palette. Pixel type for names and controls, plain type for reading. */
:root{
  --ground:#0f0c10;--paper:#231b1f;--paper-2:rgba(255,232,204,.07);--paper-3:rgba(255,232,204,.16);
  --glass:rgba(30,23,27,.72);--glass-strong:rgba(28,21,25,.9);--field:rgba(8,5,8,.32);
  --ink:#f4e7d3;--ink-2:#d2bea5;--ink-3:#9e8a78;--line:rgba(244,231,211,.12);--line-2:rgba(244,231,211,.22);
  --olive:#f0c27a;--olive-ink:#2a1a12;--accent:#f39b55;--danger:#ef8a72;
  --frost:rgba(30,23,27,.6);--frost-line:rgba(255,232,204,.14);--frost-hi:rgba(48,37,42,.78);
  --shadow:0 18px 50px rgba(6,3,6,.45);--shadow-s:0 6px 20px rgba(6,3,6,.35);
  --pixel:"Pixelify Sans","Silkscreen",ui-monospace,monospace;--serif:var(--pixel);--ui:"Figtree",system-ui,-apple-system,sans-serif;--write:"Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif;
  --r:10px;--panel-w:min(410px,calc(100vw - 32px));
  --sa-t:env(safe-area-inset-top,0px);--sa-b:env(safe-area-inset-bottom,0px);--sa-l:env(safe-area-inset-left,0px);--sa-r:env(safe-area-inset-right,0px);
  --kb:0px;color-scheme:dark;
}
'''
css = TOKENS + css
css = rep(css, '#view{position:fixed;display:block;image-rendering:pixelated;z-index:0}\n#nogl{position:fixed;inset:0;display:grid;place-items:center;padding:24px;text-align:center;color:#eee}\n', '')
css = css.replace('background:#fff;', 'background:var(--field);').replace('background:#fff}', 'background:var(--field)}')
css = rep(css, '.switch::after{content:"";position:absolute;top:3px;left:3px;width:22px;height:22px;border-radius:50%;background:var(--field);', '.switch::after{content:"";position:absolute;top:3px;left:3px;width:22px;height:22px;border-radius:50%;background:var(--ink);')
css = rep(css, '.icon:hover{background:#fbf9f4}', '.icon:hover{background:var(--frost-hi)}')
css = rep(css, 'background:#efe8da;', 'background:var(--paper-2);')
css = css.replace('rgba(42,41,36,.06)', 'rgba(255,232,204,.08)').replace('rgba(42,41,36,.04)', 'rgba(255,232,204,.05)')
css = rep(css, 'background:color-mix(in srgb,var(--paper) 97%,transparent);border:1px solid rgba(255,255,255,.6);border-radius:22px;',
          'background:var(--glass);border:1px solid var(--frost-line);border-radius:14px;-webkit-backdrop-filter:blur(16px) saturate(1.1);backdrop-filter:blur(16px) saturate(1.1);')
css = rep(css, 'background:color-mix(in srgb,var(--paper) 96%,transparent);color:var(--ink);border-radius:22px;',
          'background:var(--glass);color:var(--ink);border-radius:14px;border:1px solid var(--frost-line);-webkit-backdrop-filter:blur(16px) saturate(1.1);backdrop-filter:blur(16px) saturate(1.1);')
css = rep(css, 'border-radius:18px;background:var(--paper);box-shadow:var(--shadow);max-width:calc(100vw - 32px)}',
          'border-radius:12px;background:var(--glass-strong);border:1px solid var(--frost-line);box-shadow:var(--shadow);max-width:calc(100vw - 32px);-webkit-backdrop-filter:blur(14px);backdrop-filter:blur(14px)}')
css = rep(css, 'padding:8px 10px calc(8px + var(--sa-b));background:var(--paper);border-top:1px solid var(--line);',
          'padding:8px 10px calc(8px + var(--sa-b));background:var(--glass);border-top:1px solid var(--frost-line);-webkit-backdrop-filter:blur(16px);backdrop-filter:blur(16px);')
css = rep(css, 'border-radius:22px 22px 0 0;border:0;transform:translateY(110%);background:var(--paper)}',
          'border-radius:14px 14px 0 0;border:0;border-top:1px solid var(--frost-line);transform:translateY(110%);background:var(--glass-strong)}')
css = rep(css, '.jcard{border-radius:20px;', '.jcard{border-radius:14px;')
css = rep(css, '.dock{bottom:calc(82px + var(--sa-b));width:calc(100% - 28px);transform:translateX(-50%)}',
          '.dock{bottom:calc(82px + var(--sa-b));width:calc(100% - 28px);transform:translateX(-50%) translateY(var(--dock-y,0px))}')
# corners: pixel UI prefers small, crisp radii; switches and dots stay round
css = css.replace('border-radius:999px', 'border-radius:var(--r)')
css = rep(css, '.switch{flex:none;width:46px;height:28px;border-radius:var(--r);', '.switch{flex:none;width:46px;height:28px;border-radius:999px;')
css = css.replace('border-radius:14px;margin-bottom:8px', 'border-radius:var(--r);margin-bottom:8px')
# pixel type for names, headings and controls
css = rep(css, '.brand h1{margin:0;font:400 32px/1 var(--serif);', '.brand h1{margin:0;font:600 34px/1 var(--pixel);')
css = rep(css, '.tab{display:flex;align-items:center;gap:8px;border:0;background:none;padding:9px 16px;border-radius:var(--r);font:500 15px/1 var(--ui);',
          '.tab{display:flex;align-items:center;gap:8px;border:0;background:none;padding:9px 16px;border-radius:var(--r);font:500 15.5px/1 var(--pixel);letter-spacing:.02em;')
css = rep(css, 'font:600 15px/1 var(--ui);cursor:pointer;background:transparent;color:var(--ink);transition:background .2s}',
          'font:500 16px/1 var(--pixel);letter-spacing:.02em;cursor:pointer;background:transparent;color:var(--ink);transition:background .2s}')
css = rep(css, '.btn{border:1px solid var(--line-2);background:var(--field);border-radius:var(--r);padding:10px 16px;font:600 14px/1 var(--ui);',
          '.btn{border:1px solid var(--line-2);background:var(--field);border-radius:var(--r);padding:10px 16px;font:500 15px/1 var(--pixel);letter-spacing:.02em;')
css = rep(css, '.cust{position:relative;display:flex;align-items:center;gap:8px;border:0;border-radius:var(--r);padding:12px 16px;background:none;cursor:pointer;font:500 14px/1 var(--ui);',
          '.cust{position:relative;display:flex;align-items:center;gap:8px;border:0;border-radius:var(--r);padding:12px 16px;background:none;cursor:pointer;font:500 15px/1 var(--pixel);letter-spacing:.02em;')
css = rep(css, '.dock-q{margin:0;font:400 19px/1.25 var(--serif);', '.dock-q{margin:0;font:500 19px/1.25 var(--pixel);letter-spacing:.01em;')
css = rep(css, '.btn:hover{background:var(--paper-2)}', '.btn:hover{background:var(--paper-3)}')
extra = open(HERE+'extra.css').read()
css = rep(css, '/* ---------- portrait / small screens ---------- */', extra + '\n/* ---------- portrait / small screens ---------- */')

# ---------------- HTML ----------------
html = cut(old, '</style>\n', '<script src="https://cdn.jsdelivr.net/npm/three')[len('</style>\n'):]
html = rep(html, '''<canvas id="view" role="img" aria-label="A small pixelated 3D pond retreat seen from above: a vintage camper van beside a pond with a dock, reeds, rocks and autumn trees."></canvas>
<div id="nogl" hidden>Talio needs WebGL, which isn’t available in this browser.</div>''',
'''<div id="stage"><canvas id="view" width="720" height="405" role="img" aria-label="Pixel-art sunset over snowy mountains, framed by tall pines, with a river and small waterfalls and a camper van with a campfire in a clearing"></canvas><div id="stagefx" aria-hidden="true"><canvas id="glowfx"></canvas><div id="artvig"></div></div><canvas id="inside" width="720" height="405" aria-hidden="true"></canvas></div>
<div class="vignette" aria-hidden="true"></div>''')
html = rep(html, '<p id="place">Pond retreat</p>', '<p id="place">River camp</p>')
html = rep(html, '<span class="lbl">Customize RV</span>', '<span class="lbl">Your van</span>')
html = rep(html, 'reset your RV?', 'reset your van?')
html = rep(html, '<h2 id="custH">Your RV</h2><p class="sub">Journaling opens new options. Nothing ever expires.</p>', '<h2 id="custH">Your van</h2><p class="sub">New looks open up as you journal. Nothing ever expires.</p>')
html = rep(html, 'aria-label="Close RV customization"', 'aria-label="Close Your van"')
html = rep(html, '<small>New RV option unlocked</small>', '<small>New van option unlocked</small>')
html = rep(html, '<span>Water, wind and rain, made live in your browser.</span>', '<span>River and wind, made live in your browser.</span>')
html = rep(html, '<span>Holds the camera still and swaps the walk-in for a quick fade.</span>', '<span>Stills the scene and swaps the move into the van for a quick fade.</span>')

# ---------------- scene ----------------
sets = cut(art, 'const SETS = ', 'const ORDER')
scene = open(HERE+'scene2d.js').read()
_sets=sets.strip();assert _sets.startswith('const SETS = ') and _sets.endswith(';')
import json as _js
_S=_js.loads(_sets[len('const SETS = '):-1])
for _k in ('sunset','day','night','sunrise'):_S[_k]=_js.load(open(A+f'newscene/{_k}_set.json'))
# the nearest ferns on their own layer, with the painting behind them filled in (see scene2d drawFerns)
_F=_js.load(open(A+'up/ferns.json'))
for _k in ('sunset','day','night','sunrise'):_S[_k]['base']=_F['sets'][_k]['base'];_S[_k]['ferns']=_F['sets'][_k]['ferns'];_S[_k]['fernGroups']=_F['groups']
# the squirrel: one sprite atlas, and where it lives in each camp scene
import base64 as _sb
_sq='data:image/png;base64,'+_sb.b64encode(open(A+'sq/atlas_opt.png','rb').read()).decode()
for _k in ('sunset','day','night','sunrise'):_S[_k]['squirrel']=[898,319,.5,776,816,887]   # home, ground, scale, nearest/farthest stop, trunk edge
scene = rep(scene, '/*@@SETS@@*/', 'const SETS = '+_js.dumps(_S)+';')
scene = rep(scene, '/*@@SQIMG@@*/', _sq)
scene = rep(scene, '/*@@VANASSETS@@*/null', open(A+'up/vanassets.json').read())
import json as _j
sky = open(A+'clouds/skyassets.json').read()
scene = rep(scene, '/*@@SKY@@*/', 'const SKY=' + sky + ';')
ins = open(A+'inlay/inassets.json').read()
_I=_js.loads(ins)
import base64 as _b64,io as _io
from PIL import Image as _Img
_buf=_io.BytesIO();_Img.open(A+'newscene/insun_final.png').save(_buf,'PNG',optimize=True)
_I['sets']['sunset']={'full':'data:image/png;base64,'+_b64.b64encode(_buf.getvalue()).decode()}
_m=_js.load(open(A+'newscene/insun_meta.json'))
_I['meta']={'sunset':{'w':952,'h':536,'bulbs':_m['bulbs'],'lamp':[round(_m['lamp'][0]),round(_m['lamp'][1])],'water':_m['water'],'steam':[163,410],'birdY':[60,150],'lit':True}}
for _n,_k,_lit in (('inday','day',False),('innight','night',True),('inrise','sunrise',False)):
    _buf=_io.BytesIO();_Img.open(A+f'newscene/{_n}_m0.png').save(_buf,'PNG',optimize=True)
    _I['sets'][_k]={'full':'data:image/png;base64,'+_b64.b64encode(_buf.getvalue()).decode()}
    _I['meta'][_k]={**_I['meta']['sunset'],'water':_js.load(open(A+f'newscene/{_n}_water.json'))['water'],'lit':_lit}
ins=_js.dumps(_I)
scene = rep(scene, '/*@@INSIDE@@*/', 'const INS=' + ins + ';')

# ---------------- app ----------------
app = cut(old, '/* ==========================================================================\n   Talio app layer', '})();\n</script>')
app = rep(app, "dev:{angle:30,time:'auto',weather:'auto',sim:null,ai:'claude',voice:'live'}", "dev:{time:'auto',weather:'clear',sim:null,ai:'claude',voice:'live'}")
app = rep(app, "function resolveWorld(){ST.time=state.dev.time==='auto'?clockTime():state.dev.time;ST.weather=state.dev.weather==='auto'?worldWeather():state.dev.weather}",
          "function resolveWorld(){const t=state.dev.time;ST.time=t==='auto'||!TIME_LABEL[t]?clockTime():t;ST.weather='clear'}   // weather is paused for now")
app = rep(app, "$('#place').textContent='Pond retreat · '+", "$('#place').textContent='River camp · '+")
app = rep(app, "a little RV parked by a pond, away from the noise", "a little camper van parked by a river in the woods, away from the noise")
app = rep(app, "Talk or write from the RV, and each entry", "Talk or write from the van, and each entry")
app = rep(app, '''${e.world?`<h4 class="dh">At the retreat</h4><p class="dctx">${esc(TIME_LABEL[e.world.time]||'')} · ${esc(e.world.weather==='clear'?'Clear skies':WX_LABEL[e.world.weather]||'')}, from the window seat</p>`:''}''',
          '''${e.world?`<h4 class="dh">At camp</h4><p class="dctx">${esc(TIME_LABEL[e.world.time]||'')} by the river</p>`:''}''')
# RV catalog: the van is part of the painting for now; keep the structure, empty the options
i = app.index('/* ---------- RV catalog'); j = app.index('/* ---------- app UI state ---------- */')
app = app[:i] + '''/* ---------- van options: the van is part of the painting for now, so the catalog is empty.
   Slots come back when the van becomes its own layer (paint, roof, awning, wheels). ---------- */
const RV_CATALOG={exterior:[],interior:[]};
const optKey=(layer,slot,id)=>layer+'.'+slot+'.'+id;
function journalCount(){return state.dev.sim==null?state.meta.savedTotal:state.dev.sim}
function isUnlocked(o){return journalCount()>=o.at}
function allOptions(){const out=[];for(const layer of Object.keys(RV_CATALOG))for(const s of RV_CATALOG[layer])for(const o of s.options)out.push({layer,slot:s.key,slotLabel:s.label,...o});return out}
function buildRV(){}
function newUnlocks(){return allOptions().filter(o=>o.at>0&&isUnlocked(o)&&!state.rv.seen.includes(optKey(o.layer,o.slot,o.id)))}
function updateCustDot(){$('#custDot').hidden=!newUnlocks().length}

''' + app[j:]
app = rep(app, '''  viewK.focusT=name==='customize'?1:0;
  const n=narrow();viewK.shiftT=name&&!n?(sheet.offsetWidth+18)/2:0;viewK.shiftYT=name==='customize'&&n?sheet.offsetHeight*.42:0;
  $('#dock').style.setProperty('--dock-shift',viewK.shiftT+'px');''',
'''  const n=narrow();viewK.focusT=name==='customize'?1:0;viewK.pfT=(name&&!n)||name==='customize'?1:0;
  viewK.panelT=name&&!n?sheet.offsetWidth+36:0;viewK.bottomT=name==='customize'&&n?sheet.offsetHeight:0;
  $('#dock').style.setProperty('--dock-shift',viewK.panelT/2+'px');wakeUI();''')
i = app.index('/* ---------- Customize RV ---------- */'); j = app.index('/* ---------- unlock note')
app = app[:i] + '''/* ---------- Your van (placeholder until van options return) ---------- */
function renderCustomize(){
  const n=journalCount();
  $('#custBody').innerHTML=`<div class="progress"><b>${n} ${n===1?'memory':'memories'} saved.</b> New paint, racks and gear for the van are on the way. Everything you save now will count toward them.</div>
    <div class="soon">${['Paint','Roof','Awning','Wheels'].map(s=>`<div><b>${s}</b><small>Coming soon</small></div>`).join('')}</div>`}
''' + app[j:]
# dev panel
app = rep(app, "$('#devP').innerHTML=seg('angle',[[30,'30°'],[40,'40°']],'Exterior camera')+seg('time',[['auto','Auto'],['morning','Morning'],['midday','Midday'],['golden','Golden'],['night','Night']],'Time')+\n    seg('weather',[['auto','Auto'],['clear','Clear'],['rain','Rain'],['windy','Windy']],'Weather')+",
          "$('#devP').innerHTML=seg('time',[['auto','Auto'],['morning','Sunrise'],['midday','Day'],['golden','Sunset'],['night','Night']],'Time of day')+`<p>Auto follows your clock: sunrise 5–10am, day until 4:30pm, sunset until about 7:45pm, then night.</p>`+\n    `<div><h4>Weather</h4></div><p>Paused for now. Clear skies until rain and wind art arrive.</p>`+")
app = rep(app, '<button type="button" id="devToast">Replay unlock note</button>', '')
app = rep(app, "  $('#devToast').addEventListener('click',()=>{state.rv.announced=[];announceUnlocks()});\n", '')
app = rep(app, "    if(k==='angle')v=+v;if(k==='sim')v=v==='null'?null:+v;state.dev[k]=v;persist();\n    if(k==='angle')VIEW.angle=v;if(k==='time'||k==='weather')applyWorld();",
          "    if(k==='sim')v=v==='null'?null:+v;state.dev[k]=v;persist();\n    if(k==='time')applyWorld();")
# boot
app = rep(app, "VIEW.angle=state.dev.angle===40?40:30;\n", '')
app = rep(app, "U.time.value=20;requestAnimationFrame(frame);", "requestAnimationFrame(frame);")
app = rep(app, "dev(o){Object.assign(state.dev,o);renderDev&&0;VIEW.angle=state.dev.angle;persist();applyWorld();updateCustDot();renderDev()},loadDemo,tune(t){VIEW.tune=t},",
          "dev(o){Object.assign(state.dev,o);persist();applyWorld();updateCustDot();renderDev()},loadDemo,life:()=>JSON.stringify({b:LIFE.birds,nb:LIFE.nextBirds,l:LIFE.leaves.length,f:LIFE.fish,t:(performance.now()-T0)/1000,mode:sceneMode}),idle:()=>!!body.dataset.idle,goIdle:()=>goIdle(true),")
# resting interface: fades after a few still seconds; any movement or touch brings it back
app = rep(app, "/* ---------- developer controls", '''/* ---------- resting interface ---------- */
const IDLE_MS=4500;let idleT=0;
function busy(){const a=document.activeElement;return!!(page||body.dataset.focus==='journal'||mode!=='out'||$('#devChip').open||$('#resurf').dataset.show==='true'||$('#toast').dataset.show==='true'||
  (a&&a!==body&&a.closest&&a.closest('.top,.dock,.bottomnav,#devChip')&&a.matches(':focus-visible')))}
function goIdle(force){if(!force&&busy()){idleT=setTimeout(goIdle,IDLE_MS);return}body.dataset.idle='true'}
function wakeUI(){if(body.dataset.idle)delete body.dataset.idle;clearTimeout(idleT);idleT=setTimeout(goIdle,IDLE_MS)}
['pointermove','pointerdown','keydown','wheel','touchstart'].forEach(e=>addEventListener(e,wakeUI,{passive:true,capture:true}));
wakeUI();

/* ---------- developer controls''')

# look outside: hide the journal card for a moment
html = rep(html, '<div class="jhead"><span id="jEyebrow">Monday · Evening</span><button class="linkbtn" type="button" id="jLeave">Step outside</button></div>',
  '<div class="jhead"><span id="jEyebrow">Monday · Evening</span><div class="jtools"><button class="jeye" type="button" id="jPeek" aria-label="Hide the journal and look outside" title="Look outside"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M2.5 12S6 5.5 12 5.5 21.5 12 21.5 12 18 18.5 12 18.5 2.5 12 2.5 12z"/><circle cx="12" cy="12" r="3"/></svg></button><button class="linkbtn" type="button" id="jLeave">Step outside</button></div></div>')
html = rep(html, '<div class="toast resurf" id="resurf"', '<button class="peekpill" type="button" id="jBack">Back to writing</button>\n<div class="toast resurf" id="resurf"')
css = rep(css, '/* ---------- portrait / small screens ---------- */', """/* look outside: the card slides away, a small pill brings it back */
.jtools{display:flex;align-items:center;gap:10px}
.jeye{width:30px;height:30px;border:0;border-radius:8px;background:none;color:var(--ink-2);display:grid;place-items:center;cursor:pointer;padding:0}
.jeye:hover{background:var(--paper-2);color:var(--ink)}
.jeye svg{width:17px;height:17px}
.peekpill{position:fixed;left:50%;bottom:calc(22px + var(--sa-b));z-index:26;transform:translate(-50%,16px);opacity:0;pointer-events:none;
  padding:11px 18px;border-radius:var(--r);border:1px solid var(--frost-line);background:var(--glass);color:var(--ink);font:500 15px/1 var(--pixel);letter-spacing:.02em;
  cursor:pointer;-webkit-backdrop-filter:blur(14px);backdrop-filter:blur(14px);box-shadow:var(--shadow-s);transition:opacity .6s ease,transform .6s ease}
body[data-peek] .journal{transform:translateY(115%)}
body[data-peek] .peekpill{opacity:1;transform:translate(-50%,0);pointer-events:auto}
body[data-peek][data-idle] .peekpill{opacity:0;pointer-events:none}
/* ---------- portrait / small screens ---------- */""")
app = rep(app, "  if(body.dataset.focus==='journal'){const st=jcard.dataset.state;", "  if(body.dataset.peek){unpeek();return}\n  if(body.dataset.focus==='journal'){const st=jcard.dataset.state;")
app = rep(app, "  body.dataset.journal='down';const after=", "  delete body.dataset.peek;body.dataset.journal='down';const after=")
app = rep(app, "function busy(){const a=document.activeElement;return!!(", "function busy(){if(body.dataset.peek)return false;const a=document.activeElement;return!!(")
app = rep(app, "/* ---------- resting interface ---------- */", """/* ---------- look outside (journal card hidden for a while) ---------- */
function peek(){if(body.dataset.focus!=='journal'||body.dataset.journal!=='up')return;if(document.activeElement)document.activeElement.blur();body.dataset.peek='true';wakeUI();setTimeout(()=>{try{$('#jBack').focus({preventScroll:true})}catch(e){}},400)}
function unpeek(){if(!body.dataset.peek)return;delete body.dataset.peek;wakeUI();setTimeout(()=>{const st=jcard.dataset.state;try{(st==='write'?jText:$('#jPeek')).focus({preventScroll:true})}catch(e){}},500)}
$('#jPeek').addEventListener('click',peek);$('#jBack').addEventListener('click',unpeek);

/* ---------- resting interface ---------- */""")
out = '''<title>Talio</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Pixelify+Sans:wght@400;500;600&family=Figtree:wght@400;500;600&display=swap">
<style>
''' + css + '</style>\n' + html + '<script>\n(()=>{\n\'use strict\';\n' + scene + '\n' + app + '})();\n</script>\n'
open(OUT, 'w').write(out)
import subprocess
subprocess.run(['python3',HERE+'theme.py',OUT,OUT,'adaptive'],check=True)
subprocess.run(['python3',HERE+'journal.py',OUT,OUT],check=True)
subprocess.run(['python3',HERE+'burn.py',OUT,OUT],check=True)
subprocess.run(['python3',HERE+'bundle.py',OUT,OUT],check=True)
subprocess.run(['python3',HERE+'sound.py',OUT,OUT],check=True)
subprocess.run(['python3',HERE+'van.py',OUT,OUT],check=True)
subprocess.run(['python3',HERE+'safety.py',OUT,OUT],check=True)
subprocess.run(['python3',HERE+'patterns.py',OUT,OUT],check=True)
subprocess.run(['python3',HERE+'field.py',OUT,OUT],check=True)
subprocess.run(['python3',HERE+'write.py',OUT,OUT],check=True)
subprocess.run(['python3',HERE+'card.py',OUT,OUT],check=True)
subprocess.run(['python3',HERE+'voice.py',OUT,OUT],check=True)
subprocess.run(['python3',HERE+'tasks.py',OUT,OUT],check=True)
subprocess.run(['python3',HERE+'stream3d.py',OUT,OUT],check=True)
subprocess.run(['python3',HERE+'postcard.py',OUT,OUT],check=True)
subprocess.run(['python3',HERE+'meadow.py',OUT,OUT],check=True)
subprocess.run(['python3',HERE+'waterfall.py',OUT,OUT],check=True)
subprocess.run(['python3',HERE+'desert.py',OUT,OUT],check=True)
print('ok', len(out))
