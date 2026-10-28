"""Save catches tasks too, on this device with no AI. The saved screen lists what went to Tasks, each with an
   undo, so nothing lands there by surprise. (Reflect still shows its own task list before saving.)
   python3 tasks.py <in.html> <out.html>"""
import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__)) + '/'   # src/
A = HERE + '../assets/'   # art, sound and scene data
import sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n: sys.exit(f'tasks.py: expected {n} got {c}: {a[:90]!r}')
    s = s.replace(a, b)

rep("session.result={title:loc.title,reflection:'',mood:session.moodBefore||loc.mood,concern:!!loc.concern,source:'none',followUp:null,tasks:[]};session.tasks=[];",
    "session.result={title:loc.title,reflection:'',mood:session.moodBefore||loc.mood,concern:!!loc.concern,source:'none',followUp:null,tasks:loc.tasks||[]};"
    "session.tasks=(loc.tasks||[]).map(text=>({text,removed:false}));   // the same on-device finder Reflect uses")
# the end of justSave: list what was caught
i = s.index("function justSave(){"); j = s.index("$('#sSupport').hidden=!loc.concern}", i)
s = s[:j] + "$('#sSupport').hidden=!loc.concern;showCaught(e.id,session.at)}" + s[j+len("$('#sSupport').hidden=!loc.concern}"):]
rep("function showSaved(t,note){", "function showSaved(t,note){$('#sCaught').hidden=true;")
rep('<p class="fine" id="savedNote">', '<div class="scaught" id="sCaught" hidden><p class="fine">Added to Tasks</p><ul id="sCaughtList"></ul></div><p class="fine" id="savedNote">')
rep("function justSave(){", r"""function showCaught(entryId,at){const box=$('#sCaught'),ul=$('#sCaughtList');
  const mine=state.tasks.filter(t=>!t.done&&(t.sources||[]).some(x=>x.entryId===entryId&&x.at===at));
  if(!mine.length){box.hidden=true;return}
  ul.innerHTML=mine.map(t=>`<li><span>${esc(t.text)}</span><button type="button" class="jib" data-tid="${t.id}" aria-label="Remove “${esc(t.text)}” from Tasks" title="Remove">`+
    '<svg viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" aria-hidden="true"><path d="M3.5 3.5l7 7M10.5 3.5l-7 7"/></svg></button></li>').join('');
  box.hidden=false;
  $$('#sCaughtList [data-tid]').forEach(b=>b.addEventListener('click',()=>{const t=state.tasks.find(x=>x.id===b.dataset.tid);if(!t)return;
    t.sources=(t.sources||[]).filter(x=>!(x.entryId===entryId&&x.at===at));if(!t.sources.length)state.tasks=state.tasks.filter(x=>x!==t);   // only undo what this entry added
    persist();b.closest('li').remove();if(!ul.children.length)box.hidden=true}))}
function justSave(){""")
rep("</style>", """
.scaught{margin:10px 0 2px;padding:10px 12px;border-radius:12px;background:var(--paper-2)}
.scaught .fine{margin:0 0 4px}
.scaught ul{list-style:none;margin:0;padding:0}
.scaught li{display:flex;align-items:center;gap:8px;padding:2px 0;font-size:14.5px;color:var(--ink)}
.scaught li span{flex:1;min-width:0}
.scaught li .jib{width:30px;height:30px}
.scaught li .jib svg{width:13px;height:13px}
</style>""")
# spoken text has no full stops: end each task at the next clause instead of the next sentence
rep(r"const TASK=/\b(?:need to|needs to|have to|has to|got to|gotta|should|must|remember to|don'?t forget to|i'?ll|i will|going to|todo:?)\s+([^.!?;\n]+)/gi;",
    r"const TASK=/\b(?:need to|needs to|have to|has to|got to|gotta|should|must|remember to|don'?t forget to|i'?ll|i will|going to|todo:?)\s+((?:(?!\b(?:but|because|since|so|which|if|though|when|and then|i'?m|i'?ve|i have|i had|you|there'?s|let'?s|yeah|anyway|okay)\b)[^.!?;\n])+)/gi;")
rep("if(!t||VAGUE.test(t)||t.split(/\\s+/).length<2)continue;",
    "if(!t||VAGUE.test(t)||t.split(/\\s+/).length<2)continue;\n        if(/^(?:it'?s|that'?s|there'?s|this|it|we|they|he|she|you|i'?m|my)\\b/i.test(t))continue;   // 'and it's about to be a minute' is not a task")
# trim spoken filler and words left dangling when the recording ends mid-phrase
rep("t=t.replace(WHEN,'').replace(/\\s{2,}/g,' ').replace(/[\\s,]+$/,'').replace(/^i\\s+/i,'').trim();",
    "t=t.replace(WHEN,'').replace(/\\s+(?:as we call it|or whatever|and whatever|and stuff|and everything|you know|or something|i guess|i think)\\b.*$/i,'').replace(/\\s{2,}/g,' ').replace(/[\\s,]+$/,'').replace(/^i\\s+/i,'').trim();\n"
    "        while(/\\s(?:for|to|with|at|on|of|and|or|the|a|an|my|our|from|in)$/i.test(t))t=t.replace(/\\s+\\S+$/,'');")
open(dst, 'w').write(s)
print('tasks ok', len(s))
