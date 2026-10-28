"""The fire: finish an entry with Reflect / Just save / Burn it, and the burn scene itself.
   python3 burn.py <in.html> <out.html>"""
import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__)) + '/'   # src/
A = HERE + '../assets/'   # art, sound and scene data
import sys, base64
src, dst = sys.argv[1], sys.argv[2]
s = open(src).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n: sys.exit(f'burn.py: expected {n} got {c}: {a[:80]!r}')
    s = s.replace(a, b)

SUPPORT = ('<p>If you’re thinking about ending your life or hurting yourself, you deserve support right now. In the US, call or text <b>988</b> to reach the Suicide &amp; Crisis Lifeline, any time.</p>'
           '<p>Outside the US, <b>findahelpline.com</b> lists free local lines. If you’re in immediate danger, call your local emergency number.</p>')

# ---------- markup ----------
rep('<div class="right"><button class="btn solid" type="button" id="jReflect" disabled>Reflect</button></div>',
    '<div class="right"><div class="split" id="jSplit"><button class="btn solid" type="button" id="jReflect" disabled>Reflect</button>'
    '<button class="btn solid more" type="button" id="jMoreBtn" aria-haspopup="menu" aria-expanded="false" aria-label="Other ways to finish" disabled>'
    '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 6l4 4 4-4"/></svg></button>'
    '<div class="smenu" id="jMenu" role="menu" hidden>'
    '<button type="button" role="menuitem" id="jJustSave">Just save<small>Kept, without a reflection</small></button>'
    '<button type="button" role="menuitem" id="jBurn">Burn it<small id="jBurnSub">Never saved, never read</small></button>'
    '</div></div></div>')
rep('<p class="fine" id="savedNote">Stay as long as you like. Anything more you add joins this entry.</p>',
    '<p class="fine" id="savedNote">Stay as long as you like. Anything more you add joins this entry.</p><div class="support" id="sSupport" hidden>' + SUPPORT + '</div>')
rep('<details id="devChip">',
    '<div class="fire" id="fire" hidden>'
    '<canvas id="fireCv" aria-label="A campfire at night by the river"></canvas><div class="fveil" id="fireVeil"></div>'
    '<p class="fhint" id="fireHint" role="status" aria-live="polite"></p>'
    '<div class="fbar" id="fireBar" hidden><button class="btn solid" type="button" id="fTake">Take out the page</button>'
    '<button class="btn" type="button" id="fSit">Just sit</button>'
    '<div class="fback"><button class="btn" type="button" id="fBack" aria-haspopup="menu" aria-expanded="false">Go back</button>'
    '<div class="smenu" id="fBackMenu" role="menu" hidden><button type="button" role="menuitem" id="fInside">Back inside<small>Your page goes back in your journal</small></button>'
    '<button type="button" role="menuitem" id="fCamp">Out to camp<small>Kept as a draft for next time</small></button></div></div></div>'
    '<div class="fbar" id="fireBar2" hidden><button class="btn" type="button" id="fPut">Put it away</button><button class="btn solid" type="button" id="fLower">Into the fire</button></div>'
    '<div class="fcare" id="fireCare" hidden><h2>Before you let this go</h2>' + SUPPORT +
    '<div class="row"><button class="btn" type="button" id="fCareBack">Back to writing</button><button class="btn solid" type="button" id="fCareGo">Go to the fire</button></div></div>'
    '</div>'
    '<div class="toast" id="letgoToast" role="status" aria-live="polite"><div class="tt"><small>Let go</small><b id="letgoT"></b></div></div>\n'
    '<details id="devChip">')
# a memory saved without a reflection doesn't show an empty "Reflection" heading
rep('<h4 class="dh">Reflection</h4><p class="drefl"></p>',"${e.reflection?'<h4 class=\"dh\">Reflection</h4><p class=\"drefl\"></p>':''}")
rep("$('.dbody',host).textContent=e.body;$('.drefl',host).textContent=e.reflection;",
    "$('.dbody',host).textContent=e.body;if(e.reflection)$('.drefl',host).textContent=e.reflection;")

# ---------- styles ----------
rep('</style>', '''
/* ---------- finishing an entry: Reflect, or one of the quieter ways ---------- */
.split{position:relative;display:inline-flex;align-items:stretch}
.split>#jReflect{border-top-right-radius:0;border-bottom-right-radius:0}
.split>.more{border-top-left-radius:0;border-bottom-left-radius:0;padding:0 12px;min-width:42px;border-left:1px solid rgba(36,25,14,.24);display:inline-flex;align-items:center;justify-content:center}
.split>.more svg{width:15px;height:15px}
.smenu{position:absolute;right:0;bottom:calc(100% + 8px);min-width:240px;z-index:6;background:var(--glass-strong);border:1px solid var(--line-2);border-radius:14px;padding:6px;
  box-shadow:0 14px 40px rgba(0,0,0,.45);-webkit-backdrop-filter:blur(16px);backdrop-filter:blur(16px)}
.smenu button{display:block;width:100%;text-align:left;background:none;border:0;border-radius:10px;padding:10px 12px;color:var(--ink);font:500 14.5px/1.25 var(--ui);cursor:pointer}
.smenu button small{display:block;margin-top:3px;color:var(--ink-3);font:400 12.5px/1.3 var(--ui)}
.smenu button:hover,.smenu button:focus-visible{background:var(--paper-3);outline:none}
#sSupport{margin-top:12px}
/* ---------- the fire ---------- */
.fire{position:fixed;inset:0;z-index:38;background:#05060a;transition:opacity .9s ease}
.fire[hidden]{display:none}
.fire canvas{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;image-rendering:pixelated;image-rendering:crisp-edges;touch-action:none}
.fire canvas.held{cursor:grabbing}
.fveil{position:absolute;inset:0;background:#040509;opacity:1;transition:opacity .9s ease;pointer-events:none}
.fbar{position:absolute;left:50%;bottom:calc(22px + var(--sa-b,0px));transform:translateX(-50%);display:flex;gap:6px;align-items:center;padding:6px;border-radius:999px;
  background:var(--frost);border:1px solid var(--frost-line);box-shadow:var(--shadow);-webkit-backdrop-filter:blur(12px);backdrop-filter:blur(12px);transition:opacity .5s ease}
.fbar[hidden]{display:none}
.fbar .btn{border-radius:999px;font-family:var(--ui);white-space:nowrap}
.fbar .btn:not(.solid){background:transparent;border-color:transparent}
.fbar .btn:not(.solid):hover{background:var(--paper-2)}
.fback{position:relative}
.fback .smenu{right:auto;left:50%;transform:translateX(-50%)}
.fhint{position:absolute;left:50%;top:calc(34px + var(--sa-t,0px));transform:translate(-50%,-6px);margin:0;width:max-content;max-width:min(86vw,520px);text-align:center;
  font:400 20px/1.35 var(--serif);color:var(--ink);text-shadow:0 1px 2px rgba(0,0,0,.85),0 0 18px rgba(0,0,0,.6);opacity:0;transition:opacity .7s ease,transform .7s ease;pointer-events:none}
.fhint[data-show="true"]{opacity:1;transform:translate(-50%,0)}
.fire[data-sit="1"] .fbar,.fire[data-sit="1"] .fhint{opacity:0;pointer-events:none}
.fcare{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:min(440px,calc(100vw - 32px));padding:22px;border-radius:18px;
  background:var(--glass-strong);border:1px solid var(--line-2);box-shadow:var(--shadow);-webkit-backdrop-filter:blur(16px);backdrop-filter:blur(16px)}
.fcare[hidden]{display:none}
.fcare h2{margin:0 0 10px;font:400 24px/1.2 var(--serif)}
.fcare p{margin:0 0 10px;color:var(--ink-2);font-size:14.5px;line-height:1.5}
.fcare .row{display:flex;gap:8px;justify-content:flex-end;margin-top:16px;flex-wrap:wrap}
.fcare .btn{border-radius:999px;font-family:var(--ui)}
@media (max-width:760px){.fbar{bottom:calc(14px + var(--sa-b,0px));gap:2px}.fbar .btn{padding:10px 12px;font-size:13.5px}.fhint{font-size:18px;top:calc(22px + var(--sa-t,0px))}}
</style>''')

# ---------- behaviour ----------
D=A+'burn2/'
enc=lambda f:'data:image/png;base64,' + base64.b64encode(open(D+f,'rb').read()).decode()
night,sunset,rise,day=enc('bnight_p.png'),enc('burnsun4_p.png'),enc('brise_p.png'),enc('bday_p.png')
# one painting per time of day; until day and sunrise exist, they borrow the sunset's soft evening
bg='{night:"'+night+'",golden:"'+sunset+'",morning:"'+rise+'",midday:"'+day+'"}'
engine = open(HERE+'burn.js').read()
glue = r'''
/* ---------- finishing an entry: Reflect, Just save, or Burn it ---------- */
const jMoreBtn=$('#jMoreBtn'),jMenu=$('#jMenu');
function closeFinish(){jMenu.hidden=true;jMoreBtn.setAttribute('aria-expanded','false')}
new MutationObserver(()=>{jMoreBtn.disabled=$('#jReflect').disabled;if(jMoreBtn.disabled)closeFinish()}).observe($('#jReflect'),{attributes:true,attributeFilter:['disabled']});
jMoreBtn.disabled=$('#jReflect').disabled;
jMoreBtn.addEventListener('click',e=>{e.stopPropagation();if(!jMenu.hidden){closeFinish();return}
  $('#jBurnSub').textContent=session&&(session.continued||session.result)?'Not saved':'Never saved, never read';   // honest if Claude already read it
  jMenu.hidden=false;jMoreBtn.setAttribute('aria-expanded','true');setTimeout(()=>{try{$('#jJustSave').focus()}catch(_){}},0)});
document.addEventListener('pointerdown',e=>{if(!jMenu.hidden&&!e.target.closest('#jSplit'))closeFinish()},true);
$('#jSplit').addEventListener('keydown',e=>{if(jMenu.hidden)return;
  if(e.key==='Escape'){e.stopPropagation();e.preventDefault();closeFinish();jMoreBtn.focus()}
  else if(e.key==='ArrowDown'||e.key==='ArrowUp'){e.preventDefault();const it=[...jMenu.querySelectorAll('button')],i=it.indexOf(document.activeElement);it[(i+(e.key==='ArrowDown'?1:it.length-1))%it.length].focus()}});

function justSave(){closeFinish();const text=jText.value.trim();if(!text||!session)return;if(document.activeElement)document.activeElement.blur();
  clearTimeout(stuckT);session.text=text;session.at=session.at||Date.now();
  const loc=Reflector.analyze(text,{style:'minimal',n:state.meta.savedTotal,at:session.at,input:session.kind,continued:true});   // rules on this device only, for a title and mood
  session.result={title:loc.title,reflection:'',mood:session.moodBefore||loc.mood,concern:!!loc.concern,source:'none',followUp:null,tasks:[]};session.tasks=[];
  const adding=!!session.entryId,e=saveEntry();session.entryId=e.id;
  const last=adding&&e.more&&e.more[e.more.length-1];if(last)last.reflectedBy='none';else e.reflectedBy='none';persist();Sound.chime(false);
  showSaved(adding?'Added to this entry':'Saved to Memories',loc.concern?'Kept, without a reflection.':'Kept quietly, without a reflection. Anything more you add joins this entry.');
  $('#sSupport').hidden=!loc.concern}
$('#jJustSave').addEventListener('click',justSave);
$('#rSave').addEventListener('click',()=>{$('#sSupport').hidden=true});

/* ---------- the fire: nothing is saved or sent; the words only exist as a draft until they burn ---------- */
function goToCamp(done){leaveJournal(false);const t0=performance.now();
  (function w(){if(tr&&mode==='exiting')tr.speed=60;if((mode==='out'&&!tr)||performance.now()-t0>7000){done();return}requestAnimationFrame(w)})()}
function letGoToast(n){const t=$('#letgoToast');$('#letgoT').textContent=n===1?'That’s the first thing you’ve let go of.':`That’s ${n} things you’ve let go of.`;
  t.dataset.show='true';clearTimeout(letGoToast.h);letGoToast.h=setTimeout(()=>{t.dataset.show='false'},5200)}
$('#jBurn').addEventListener('click',()=>{closeFinish();const text=jText.value.trim();if(!text||!session||Burn.active)return;
  if(document.activeElement)document.activeElement.blur();clearTimeout(stuckT);
  const fresh=!session.continued&&!session.entryId;if(fresh){state.meta.draft=text;persist()}
  const concern=!!Reflector.analyze(text,{style:'minimal',n:0,at:Date.now(),input:'write',continued:true}).concern;   // checked here, on this device
  body.dataset.journal='down';
  Burn.open({text,concern,time:ST.time,onExit:where=>{
    if(where==='inside'){body.dataset.journal='up';setJ('write');Burn.hide();setTimeout(()=>{try{jText.focus({preventScroll:true})}catch(_){}},400);return}
    if(where==='burned'){state.meta.letGo=(state.meta.letGo||0)+1;if(fresh)state.meta.draft='';jText.value='';if(session)session.text='';persist()}
    goToCamp(()=>{Burn.hide();if(where==='burned')setTimeout(()=>letGoToast(state.meta.letGo),reducedMotion?100:900)})}})});
window.__talio&&(window.__talio.fire=()=>Burn);
'''
ANCHOR="  jumpIn(kind){startJournal(kind||'write');tr&&(tr.t=tr.dur-.01)}};\n})();"
rep(ANCHOR, ANCHOR[:-len('\n})();')] + '\nconst BURN_BG=' + bg + ';\n' + engine + glue + '\n})();')

open(dst, 'w').write(s)
print('burn ok', len(s))
