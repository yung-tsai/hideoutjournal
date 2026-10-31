"""Honest titles, demo data kept apart, and a plainer entry page (after Home).
   - Titles: without Claude (which the live site can't reach yet), an entry is titled with its own first few words
     ("Walked to the bakery with Sam"), or the day and time of day when it's too short ("Saturday morning"). No more
     titles made from a mood word plus a topic ("A rough day at work"), which looked like the demo entries'.
   - Once, titles the old rules made up on unedited entries are redone the same way (the old ones kept in hideout-titles-before-v2).
   - Mood: the mood you picked at "How are you feeling?" wins over the guessed one, on Save and on Reflect.
   - Demo data lives in its own store (hideout-demo-v1), switched on from the Dev page ("Try demo data"); the app then
     shows only demo entries, with a "Demo data" chip, and your journal (talio-home-v1) isn't touched at all. "Back to my
     journal" switches back; "Clear demo data" deletes the demo store. Demo entries that were mixed into a real journal
     earlier are moved out once (a copy is kept under hideout-demo-moved-v1).
   - The Dev page lists check-ins that loading demo data may have invented on real entries, and can clear them (two taps).
   - Entry page: no "At camp" section and no "You wrote" / "You said" label; the question it answered, if any, sits above
     the text as a small muted italic line.
   python3 entries.py <in.html> <out.html>"""
import sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n: sys.exit(f'entries.py: expected {n} got {c}: {a[:90]!r}')
    s = s.replace(a, b)

# ---------- demo data in its own store ----------
rep("const STORE='talio-home-v1';",
    "const DEMO_MODE=(()=>{try{return localStorage.getItem('hideout-demo-mode')==='1'}catch(e){return false}})();\n"
    "const STORE=DEMO_MODE?'hideout-demo-v1':'talio-home-v1';   // demo data never shares a store with your journal")
rep("<button type=\"button\" id=\"devDemo\">Load demo memories</button>${demoCount()?'<button type=\"button\" id=\"devDemoOff\">Remove demo memories ('+demoCount()+')</button>':''}",
    "<button type=\"button\" id=\"devDemo\">${DEMO_MODE?'Back to my journal':'Try demo data'}</button><button type=\"button\" id=\"devDemoClear\">Clear demo data</button>")
rep("$('#devDemo').addEventListener('click',()=>{loadDemo();markDemo();renderDev();updateDock();if(page)openPage(page)});",
    "$('#devDemo').addEventListener('click',()=>demoSwitch(!DEMO_MODE));$('#devDemoClear').addEventListener('click',demoClear);")

# ---------- titles and mood ----------
rep("let title=topic&&topic[1]?`${ADJ[mood]} day ${where}`:`${ADJ[mood]} ${per}`;\n    if(turned&&(mood==='frustrated'||mood==='low'))title='A rough start, a better end';",
    "let title=plainTitle(text,when);")
rep("return{title:'A hard moment',mood:'low',concern:true", "return{title:plainTitle(text,when),mood:'low',concern:true")
rep("const m={at,input:session.kind,prompt:session.prompt||null,body:session.text,reflection:r.reflection,mood:r.mood,",
    "const m={at,input:session.kind,prompt:session.prompt||null,body:session.text,reflection:r.reflection,mood:session.moodBefore||r.mood,")
rep("title:r.title,body:session.text,reflection:r.reflection,mood:r.mood,", "title:r.title,body:session.text,reflection:r.reflection,mood:session.moodBefore||r.mood,")

# ---------- the entry page ----------
rep("<h4 class=\"dh\">${e.input==='talk'?'You said':'You wrote'}</h4>${e.prompt?`<p class=\"dq\">${esc(e.prompt)}</p>`:''}<p class=\"dbody\"></p>",
    "${e.prompt?`<p class=\"dq dprompt\">${esc(e.prompt)}</p>`:''}<p class=\"dbody\"></p>")
rep("${e.world?`<h4 class=\"dh\">At camp</h4><p class=\"dctx\">${esc(TIME_LABEL[e.world.time]||'')} by the river</p>`:''}", "")

# ---------- behaviour ----------
rep("let meadowOn=false;", r"""/* ---------- honest titles; demo data kept apart ---------- */
function plainTitle(text,when){when=when||new Date();const h=when.getHours(),per=h>=5&&h<12?'morning':h>=12&&h<17?'afternoon':h>=17&&h<22?'evening':'night';
  const first=String(text||'').trim().split(/[.!?;:\n—–]|,\s/)[0].replace(/^(?:so|um+|uh+|okay|ok|well|honestly|anyway|yeah)\b[,\s]*/i,'').trim();
  const w=first.split(/\s+/).filter(Boolean).slice(0,7);
  while(w.length>2&&/^(?:and|but|or|the|a|an|to|of|with|after|for|at|in|on|my|our|so|that|is|was|this|just|really|some)$/i.test(w[w.length-1]))w.pop();
  if(w.length<2)return when.toLocaleDateString(undefined,{weekday:'long'})+' '+per;
  const t=w.join(' ').replace(/[,\s]+$/,'');return t.charAt(0).toUpperCase()+t.slice(1)}
function demoSwitch(on){persist();try{if(on)localStorage.setItem('hideout-demo-mode','1');else localStorage.removeItem('hideout-demo-mode')}catch(_){}location.reload()}
function demoClear(){const b=$('#devDemoClear');if(b&&b.dataset.arm!=='1'){b.dataset.arm='1';b.textContent='Tap again to clear demo data';return}
  try{localStorage.removeItem('hideout-demo-v1');localStorage.removeItem('hideout-demo-moved-v1')}catch(_){}
  if(DEMO_MODE){try{localStorage.removeItem('hideout-demo-mode')}catch(_){}location.reload();return}
  if(b){b.dataset.arm='';b.textContent='Demo data cleared'}}
const DEMO_DOWN={happy:'calm',calm:'okay',okay:'low',low:'low',frustrated:'frustrated'};
function inventedCheckins(){return DEMO_MODE?[]:state.entries.filter(e=>e&&!e.demo&&e.moodAfter&&e.moodBefore&&e.moodAfter===e.mood&&(e.moodBefore===e.mood||e.moodBefore===DEMO_DOWN[e.mood]))}
{const _rd=renderDev;renderDev=function(){_rd();const host=$('#devP');if(!host||DEMO_MODE)return;const list=inventedCheckins();
  const d=document.createElement('div');d.className='devfix';
  d.innerHTML=`<h4>Check-ins to review</h4>`+(list.length?`<p>Loading demo data used to add made-up before/after moods to real entries. ${list.length===1?'This one looks':'These '+list.length+' look'} like that (the after mood matches the guessed one). Some could be real.</p><ul>${list.map(e=>`<li>${esc(fDay.format(new Date(e.at)))} · ${esc(e.title||'')} <span>before ${esc(e.moodBefore)}, after ${esc(e.moodAfter)}</span></li>`).join('')}</ul><div class="dseg"><button type="button" id="devFixCk">Clear these check-ins</button></div>`:'<p>Nothing to review.</p>');
  host.appendChild(d);const fb=$('#devFixCk');if(fb)fb.addEventListener('click',()=>{if(fb.dataset.arm!=='1'){fb.dataset.arm='1';fb.textContent='Tap again to clear';return}
    for(const e of inventedCheckins()){e.moodBefore=null;e.moodAfter=null;e.feelBefore=null;e.feelAfter=null}persist();renderDev()})}}
setTimeout(()=>{let changed=false;
  if(DEMO_MODE){if(!state.meta.demoMade){try{const real=JSON.parse(localStorage.getItem('talio-home-v1')||'null');if(real&&real.settings)state.settings={...state.settings,...real.settings}}catch(_){}
      state.meta.demoMade=true;loadDemo();changed=true}
    state.entries.forEach(e=>{if(!e.demo){e.demo=true;changed=true}});
    const c=document.createElement('button');c.type='button';c.className='demochip';c.innerHTML='Demo data<span>Back to my journal</span>';c.addEventListener('click',()=>demoSwitch(false));document.body.appendChild(c)}
  else{const out=state.entries.filter(e=>e&&e.demo);if(out.length){const gone=new Set(out.map(e=>e.id)),only=t=>Array.isArray(t.sources)&&t.sources.length&&t.sources.every(x=>gone.has(x.entryId));
      try{localStorage.setItem('hideout-demo-moved-v1',JSON.stringify({at:Date.now(),entries:out,tasks:state.tasks.filter(only)}))}catch(_){}
      state.entries=state.entries.filter(e=>!e.demo);state.tasks=state.tasks.filter(t=>!only(t));changed=true}}
  if(!DEMO_MODE&&!state.meta.titlesV2){   // once: titles the old rules made up (a mood word plus a topic) become the entry's own first words
    const OLD=/^(?:(?:A quiet|An ordinary|A heavy|A rough|A good) (?:day (?:at work|with family|with friends|outside)|morning|afternoon|evening|night)|A rough start, a better end|A hard moment)$/,was={};
    for(const e of state.entries)if(e&&!e.editedAt&&e.reflectedBy!=='claude'&&OLD.test(e.title||'')){was[e.id]=e.title;e.title=plainTitle(e.body,new Date(e.at))}
    if(Object.keys(was).length)try{localStorage.setItem('hideout-titles-before-v2',JSON.stringify(was))}catch(_){}
    state.meta.titlesV2=true;changed=true}
  if(changed){persist();updateDock();if(typeof renderSb==='function')renderSb(true);if(page)openPage(page);renderDev()}},0);
if(window.__talio)window.__talio.loadDemo=()=>demoSwitch(true);
let meadowOn=false;""")

# ---------- styles ----------
rep('</style>', """
/* ---------- the entry page; demo data ---------- */
#detailBody .dprompt{margin:18px 0 6px;font:italic 400 14.5px/1.45 var(--serif);color:var(--ink-3)}
#detailBody .dtitle+.dbody{margin-top:14px}
.demochip{position:fixed;left:50%;bottom:calc(10px + var(--sa-b,0px));transform:translateX(-50%);z-index:30;display:flex;align-items:center;gap:10px;
  padding:6px 8px 6px 12px;border:1px solid var(--line-2);border-radius:999px;background:#fff8e6;color:#7a5b16;font:600 11.5px/1 var(--ui);letter-spacing:.06em;text-transform:uppercase;cursor:pointer;box-shadow:var(--shadow-s)}
.demochip span{padding:5px 9px;border-radius:999px;background:#fff;color:var(--ink);font:500 12px/1 var(--ui);letter-spacing:0;text-transform:none}
body[data-record] .demochip{display:none}
#pg-dev .devfix ul{margin:6px 0 10px;padding:0 0 0 18px;font:400 13px/1.6 var(--ui);color:var(--ink-2)}
#pg-dev .devfix li span{color:var(--ink-3)}
</style>""")

open(dst, 'w').write(s)
print('entries ok', len(s))
