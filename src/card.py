"""The writing card, simplified: one question at a time, and one bar of icons.
   - It opens on "How are you feeling?" with the mood chips as its answer.
   - Picking a mood fades the heading into a question that fits that mood; the shuffle icon offers another.
   - The question you wrote under is saved with the entry (and with each added part), and shown in Memories.
   - Bottom bar: close and look-outside on the left; mic, more (Reflect / Burn) and Save on the right.
   python3 card.py <in.html> <out.html>"""
import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__)) + '/'   # src/
A = HERE + '../assets/'   # art, sound and scene data
import sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n: sys.exit(f'card.py: expected {n} got {c}: {a[:90]!r}')
    s = s.replace(a, b)
SV = lambda d, fill='none': f'<svg viewBox="0 0 24 24" fill="{fill}" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{d}</svg>'
SHUFFLE = SV('<path d="M20 11a8 8 0 0 0-14.3-4.9L4 8"/><path d="M4 4v4h4"/><path d="M4 13a8 8 0 0 0 14.3 4.9L20 16"/><path d="M20 20v-4h-4"/>')   # round arrows: another question
DOWN = SV('<path d="m6 9 6 6 6-6"/>')
EYE = SV('<path d="M2.5 12S6 5.5 12 5.5 21.5 12 21.5 12 18 18.5 12 18.5 2.5 12 2.5 12z"/><circle cx="12" cy="12" r="3"/>')
DOTS = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><circle cx="5.5" cy="12" r="1.7"/><circle cx="12" cy="12" r="1.7"/><circle cx="18.5" cy="12" r="1.7"/></svg>'
SPARK = SV('<path d="M12 3v4M12 17v4M3 12h4M17 12h4M6 6l2.5 2.5M15.5 15.5 18 18M18 6l-2.5 2.5M8.5 15.5 6 18"/>')
FLAME = SV('<path d="M12 21c-3.9 0-6.5-2.6-6.5-6.1 0-3.4 2.6-5.5 3.9-8.4.6 2 1.8 3.1 2.9 3.6.3-2.6 1.6-4.8 3.2-6.1-.3 2.6.8 4.4 2 6.1 1 1.4 1.5 2.9 1.5 4.6C19 18.3 16 21 12 21z"/>')

# ---------- questions ----------
rep("const PROMPTS={",
    "const ASK_FEEL='How are you feeling?';\n"
    "/* once a mood is picked, the heading becomes a question that fits it; shuffle offers the next one */\n"
    "const ASK={low:['What would make today feel good?','What’s weighing on you right now?','What do you need most today?','What’s one small thing that might help?'],\n"
    "  frustrated:['What would make today feel good?','What’s getting under your skin?','What would help you let this go?','What’s in your control here, and what isn’t?'],\n"
    "  okay:['What’s been on your mind today?','What’s one thing you want to remember about today?','What would make today a little better?'],\n"
    "  calm:['What’s helping you feel settled?','What’s been good about today?','What would you like to hold on to from today?'],\n"
    "  happy:['What made today good?','Who or what are you grateful for today?','What do you want to remember about today?']};\n"
    "const ASK_ANY=['What’s on your mind?','How’s the day going so far?','What’s been taking up space in your head?','What’s one thing you want to remember about today?'];\n"
    "const PROMPTS={")
# the field and the card both open on the same simple question
rep("$('#fieldQ').textContent=PROMPTS[ST.time];$('#jField').setAttribute('aria-label','Start writing: '+PROMPTS[ST.time]);",
    "$('#fieldQ').textContent=ASK_FEEL;$('#jField').setAttribute('aria-label','Start writing: '+ASK_FEEL);")
rep("if(kind==='write')prepWrite(state.meta.draft||'',PROMPTS[ST.time],false);else{$('#jTalkQ').textContent=PROMPTS[ST.time];setJ('talk')}",
    "if(kind==='write')prepWrite(state.meta.draft||'',ASK_FEEL,false);else{$('#jTalkQ').textContent=ASK_FEEL;setJ('talk')}")
rep("$('#jToTalk').addEventListener('click',()=>{session.kind='talk';$('#jTalkQ').textContent=PROMPTS[ST.time];startListening()});",
    "$('#jToTalk').addEventListener('click',()=>{session.kind='talk';$('#jTalkQ').textContent=$('#jWriteQ').textContent||ASK_FEEL;startListening()});")
# a fresh page starts on the feeling question; a follow-up ("Keep writing") keeps its question as the prompt
rep("function prepWrite(text,q,heard){",
    "function prepWrite(text,q,heard){if(session){const more=!!(session.continued||session.entryId);session.prompt=more&&q&&q!==ASK_FEEL?q:null;session.askMood=null;session.askIdx=0;session.anyIdx=-1;session.askFixed=more}")
rep("function drawBefore(){if(!session)return;", "function drawBefore(){if(!session)return;updateAsk();")
rep("function armStuck(){", r"""function setAsk(text){const el=$('#jWriteQ');if(!el||el.textContent===text)return;
  if(reducedMotion){el.textContent=text;return}
  el.classList.add('swap');clearTimeout(setAsk.t);setAsk.t=setTimeout(()=>{el.textContent=text;el.classList.remove('swap')},170)}
function updateAsk(){if(!session||session.askFixed)return;const m=session.moodBefore;
  if(m&&ASK[m]){if(session.askMood!==m){session.askMood=m;session.askIdx=0}session.prompt=ASK[m][session.askIdx%ASK[m].length];setAsk(session.prompt)}
  else if(session.anyIdx>=0){session.askMood=null;session.prompt=ASK_ANY[session.anyIdx%ASK_ANY.length];setAsk(session.prompt)}
  else{session.askMood=null;session.prompt=null;setAsk(ASK_FEEL)}}
function armStuck(){""")
# the question goes with what was written
rep("const e={id:uid(),at,input:session.kind,title:r.title,body:session.text,",
    "const e={id:uid(),at,input:session.kind,prompt:session.prompt||null,title:r.title,body:session.text,")
rep("if(base){const m={at,input:session.kind,body:session.text,",
    "if(base){const m={at,input:session.kind,prompt:session.prompt||null,body:session.text,")
# ...and Memories shows it above the words
rep("<h4 class=\"dh\">${e.input==='talk'?'You said':'You wrote'}</h4><p class=\"dbody\"></p>",
    "<h4 class=\"dh\">${e.input==='talk'?'You said':'You wrote'}</h4>${e.prompt?`<p class=\"dq\">${esc(e.prompt)}</p>`:''}<p class=\"dbody\"></p>")
rep("<h4 class=\"dh\">${m.input==='talk'?'You added, aloud':'You added'} · ${esc(fTime.format(new Date(m.at)))}</h4><p class=\"dbody\"></p>",
    "<h4 class=\"dh\">${m.input==='talk'?'You added, aloud':'You added'} · ${esc(fTime.format(new Date(m.at)))}</h4>${m.prompt?`<p class=\"dq\">${esc(m.prompt)}</p>`:''}<p class=\"dbody\"></p>")

# ---------- markup ----------
rep('<label class="jq" for="jText" id="jWriteQ">What’s on your mind?</label>',
    '<div class="jqrow"><label class="jq" for="jText" id="jWriteQ">How are you feeling?</label><button class="jib" type="button" id="jShuffle" aria-label="Another question" title="Another question">' + SHUFFLE + '</button></div>')
rep('<div class="jrow jfinish"><div class="right">',
    '<div class="jrow jfinish"><div class="right">')
rep('<button class="jmic" type="button" id="jToTalk"', '<button class="jib" type="button" id="jToTalk"')
rep('<button type="button" role="menuitem" id="jReflect" disabled>Reflect on it<small>',
    '<button type="button" role="menuitem" id="jReflect" disabled>' + SPARK + '<span>Reflect on it<small>')
rep('A few thoughtful lines back</small></button>', 'A few thoughtful lines back</small></span></button>')
rep('<button type="button" role="menuitem" id="jBurn">Burn it<small id="jBurnSub">Never saved, never read</small></button>',
    '<button type="button" role="menuitem" id="jBurn">' + FLAME + '<span>Burn it<small id="jBurnSub">Never saved, never read</small></span></button>')

# ---------- wiring ----------
rep("$$('[data-start]').forEach(b=>b.addEventListener('click',()=>startJournal(b.dataset.start)));",
    "$$('[data-start]').forEach(b=>b.addEventListener('click',()=>startJournal(b.dataset.start)));\n"
    "/* outside, tapping anywhere off the card folds it back into the field (the draft is kept); not mid-reflection or mid-recording */\n"
    "document.addEventListener('pointerdown',ev=>{if(body.dataset.focus!=='journal'||body.dataset.journal!=='up'||body.dataset.where!=='out'||body.dataset.peek)return;\n"
    "  if(ev.target.closest('#jcard,.toast,#burn,.burnui'))return;const st=jcard.dataset.state;if(st==='write'||st==='saved'){ev.preventDefault();$('#jLeave').click()}},true);\n"
    "$('#jShuffle').addEventListener('click',()=>{if(!session)return;if(session.askFixed){session.askFixed=false}\n"
    "  if(session.moodBefore&&ASK[session.moodBefore]){session.askIdx++}else{session.anyIdx++}updateAsk();try{jText.focus({preventScroll:true})}catch(_){}});")
rep("  $('#jLeave').textContent=inVan?'Step outside':'Close';",
    "  $('#jLeave').textContent=inVan?'Step outside':'Close';if(kind==='write'){try{jText.focus({preventScroll:true})}catch(e){}}")   # focus inside the tap itself, so phones raise the keyboard

rep("</style>", """
/* ---------- the writing card: one question, one bar of icons ---------- */
.jqrow{display:flex;align-items:flex-start;gap:8px}
.jqrow .jq{flex:1;min-width:0;transition:opacity .17s ease}
.jqrow .jq.swap{opacity:0}
#jMoodRow>.fine{display:none}
#jStuckRow{display:none!important}
body[data-where="out"] #jcard .jhead .jtools{display:none}
#jPeek{display:none!important}
.jib{flex:none;width:40px;height:40px;display:grid;place-items:center;border:0;border-radius:10px;background:none;color:var(--ink-2);cursor:pointer;transition:background .15s,color .15s}
.jib svg{width:20px;height:20px}
.jib:hover:not(:disabled){background:var(--paper-2);color:var(--ink)}
.jib:disabled{opacity:.35;cursor:default}
.jib[aria-expanded="true"]{background:var(--paper-2);color:var(--ink)}
.jib:focus-visible{outline:2px solid var(--olive);outline-offset:1px}
.jqrow .jib{width:30px;height:30px;margin:2px -6px 0 0;border-radius:8px;color:var(--ink-3)}
.jqrow .jib svg{width:16px;height:16px}
.jfinish{display:flex;align-items:center;gap:4px;margin-top:12px;padding-top:10px;border-top:1px solid var(--line)}
.jfinish .jleft{display:flex;gap:2px}
.jfinish .right{display:flex;align-items:center;gap:2px;margin-left:auto}
#jSplit{display:inline-flex;align-items:stretch;gap:0;position:relative;margin-left:6px}
#jSplit>#jSaveMain{border-top-right-radius:0;border-bottom-right-radius:0}
#jSplit>.btn:disabled{opacity:.45;cursor:default}
#jDictTip{display:none!important}   /* the mic sits right there now */
#jMenu button{display:flex;align-items:flex-start;gap:10px;text-align:left}
#jMenu button svg{width:18px;height:18px;flex:none;margin-top:1px;color:var(--ink-2)}
#jMenu button span{display:block}
.dq{margin:0 0 6px;font:italic 400 16px/1.4 var(--serif);color:var(--ink-3)}
</style>""")
rep("jText.placeholder='Start writing…'","jText.placeholder=''")
rep('<textarea id="jText" rows="4" placeholder="Start writing…"></textarea>','<textarea id="jText" rows="4" placeholder="" aria-label="Your entry"></textarea>')
open(dst, 'w').write(s)
print('card ok', len(s))
