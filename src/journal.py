"""Journal feature pass: fast capture + the before/after mood check.
   python3 journal.py <in.html> <out.html>"""
import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__)) + '/'   # src/
A = HERE + '../assets/'   # art, sound and scene data
import sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src).read()

def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n: sys.exit(f'journal.py: expected {n} got {c}: {a[:80]!r}')
    s = s.replace(a, b)

# ---------- fast capture: the card is up and ready before the scene finishes changing ----------
rep("""  startEnter(()=>{Sound.update();body.dataset.journal='up';if(!session)return;
    if(kind==='talk')startListening();else setTimeout(()=>{try{jText.focus({preventScroll:true})}catch(e){}},420)});""",
"""  body.dataset.journal='up';   // fast capture: don't make them wait on the scene
  if(kind==='write')setTimeout(()=>{try{jText.focus({preventScroll:true})}catch(e){}},reducedMotion?40:200);
  startEnter(()=>{Sound.update();if(!session)return;if(kind==='talk')startListening()});""")

# ---------- markup ----------
rep('<textarea id="jText" rows="4" placeholder="Start writing…"></textarea>',
    '<div class="moodrow" id="jMoodRow"><span class="fine">How are you?</span><div class="moods" id="jMoods" role="group" aria-label="How are you?"></div><div class="feels" id="jFeels" role="group" aria-label="More specifically" hidden></div></div>\n      <textarea id="jText" rows="4" placeholder="Start writing…"></textarea>')
rep('<div class="jrow"><button class="btn small" type="button" id="sMore">Keep going</button>',
    '<div class="moodrow" id="sMoodRow"><span class="fine" id="sMoodQ">And now?</span><div class="moods" id="sMoods" role="group" aria-label="And now?"></div><div class="feels" id="sFeels" role="group" aria-label="More specifically" hidden></div></div>\n      <div class="jrow"><button class="btn small" type="button" id="sMore">Keep going</button>')

# ---------- styles ----------
rep('</style>', '''
/* ---------- mood check-in ---------- */
.moodrow{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin:0 0 10px}
.moodrow .fine{margin:0}
.moods{display:flex;gap:6px;flex-wrap:wrap}
.moodbtn{display:inline-flex;align-items:center;gap:7px;border:1px solid var(--line);background:var(--paper-2);color:var(--ink-2);
  border-radius:999px;padding:6px 12px;font:500 13px/1 var(--ui);cursor:pointer;transition:background .18s,color .18s,border-color .18s}
.moodbtn i{width:8px;height:8px;border-radius:50%;background:var(--m);display:block;flex:none}
.moodbtn:hover{background:var(--paper-3);color:var(--ink)}
.moodbtn[aria-pressed="true"]{background:var(--paper-3);color:var(--ink);border-color:var(--m)}
.feels{flex-basis:100%;display:flex;gap:5px;flex-wrap:wrap;margin-top:-2px;animation:feelIn .35s ease}
.feels[hidden]{display:none}
.feelbtn{border:1px solid transparent;background:none;color:var(--ink-3);border-radius:999px;padding:5px 10px;font:500 12.5px/1 var(--ui);cursor:pointer}
.feelbtn:hover{color:var(--ink);background:var(--paper-2)}
.feelbtn[aria-pressed="true"]{color:var(--ink);background:var(--paper-3);border-color:var(--line-2)}
@keyframes feelIn{from{opacity:0;transform:translateY(-3px)}to{opacity:1;transform:none}}
@media (prefers-reduced-motion:reduce){.feels{animation:none}}
@media (max-width:760px){.moodbtn{padding:7px 7px;font-size:12px;gap:5px}.moodbtn i{width:7px;height:7px}.moods{gap:4px}}
@media (max-width:370px){.moodbtn i{display:none}.moodbtn{padding:7px 9px}}
</style>''')

# ---------- behaviour ----------
rep("function leaveJournal(saved){",
'''/* ---------- mood check-in: a quiet before and after, no AI involved ---------- */
const MOOD_ORDER=['low','frustrated','okay','calm','happy'],BAND={low:0,frustrated:0,okay:1,calm:2,happy:2};   // low → high; the chart groups them into three bands
const FEELS={low:['tired','sad','lonely','anxious','overwhelmed'],frustrated:['stressed','annoyed','angry','restless'],okay:['fine','busy','flat','meh'],
  calm:['rested','content','relieved','peaceful'],happy:['grateful','proud','excited','loved']};
function buildMoods(el,pick){el.innerHTML='';
  for(const k of MOOD_ORDER){const b=document.createElement('button');b.type='button';b.className='moodbtn';b.dataset.m=k;
    b.setAttribute('aria-pressed','false');b.style.setProperty('--m',MOODS[k].c);b.innerHTML='<i></i>';
    b.appendChild(document.createTextNode(MOODS[k].l));b.addEventListener('click',()=>pick(k));el.appendChild(b)}}
function markMood(el,k){for(const b of el.children)b.setAttribute('aria-pressed',String(b.dataset.m===k))}
function buildFeels(el,mood,cur,pick){el.innerHTML='';if(!mood){el.hidden=true;return}el.hidden=false;   // optional: a more specific word, never required
  for(const w of FEELS[mood]){const b=document.createElement('button');b.type='button';b.className='feelbtn';b.textContent=w;
    b.setAttribute('aria-pressed',String(w===cur));b.addEventListener('click',()=>pick(w));el.appendChild(b)}}
function savedEntry(){return session&&session.entryId?state.entries.find(x=>x.id===session.entryId):null}
function drawBefore(){if(!session)return;markMood($('#jMoods'),session.moodBefore||null);
  buildFeels($('#jFeels'),session.moodBefore,session.feelBefore,w=>{session.feelBefore=session.feelBefore===w?null:w;drawBefore()})}
function afterLine(e){const b=e.moodBefore,a=e.moodAfter;return!a?'And now?':b&&BAND[a]>BAND[b]?'Lighter than when you arrived.':b&&a===b?'Steady. Thanks for checking in.':'Noted. Thanks for checking in.'}
function drawAfter(){const e=savedEntry();if(!e)return;markMood($('#sMoods'),e.moodAfter||null);$('#sMoodQ').textContent=afterLine(e);
  buildFeels($('#sFeels'),e.moodAfter,e.feelAfter,w=>{e.feelAfter=e.feelAfter===w?null:w;persist();drawAfter()})}
function initMoods(){
  buildMoods($('#jMoods'),k=>{if(!session)return;if(session.moodBefore===k){session.moodBefore=null;session.feelBefore=null}else{session.moodBefore=k;session.feelBefore=null}drawBefore()});
  buildMoods($('#sMoods'),k=>{const e=savedEntry();if(!e)return;if(e.moodAfter===k){e.moodAfter=null;e.feelAfter=null}else{e.moodAfter=k;e.feelAfter=null}persist();drawAfter()})}
function leaveJournal(saved){''')

# the before row: only on a fresh entry, never when adding to one
rep("function prepWrite(text,q,heard){",
    "function prepWrite(text,q,heard){$('#jMoodRow').hidden=!!(session&&(session.continued||session.entryId));drawBefore();")

# the after row, set up each time the saved card shows
rep("function showSaved(t,note){$('#savedT').textContent=t;$('#savedNote').textContent=note;",
'''function showSaved(t,note){$('#savedT').textContent=t;$('#savedNote').textContent=note;
  {const e=savedEntry();$('#sMoodRow').hidden=!e;if(e)drawAfter()}''')

# remember how they arrived
rep("const e={id:uid(),at,input:session.kind,title:r.title,body:session.text,reflection:r.reflection,mood:r.mood,",
    "const e={id:uid(),at,input:session.kind,title:r.title,body:session.text,reflection:r.reflection,mood:r.mood,moodBefore:session.moodBefore||null,feelBefore:session.feelBefore||null,moodAfter:null,feelAfter:null,")

rep("applyMotion();buildRV();size();applyWorld();updateDock();", "initMoods();applyMotion();buildRV();size();applyWorld();updateDock();")

open(dst, 'w').write(s)
print('journal ok', len(s))
