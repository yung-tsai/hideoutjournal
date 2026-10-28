"""Never lose everything to one click: clearing asks twice, and whatever was cleared is kept so it can be brought back.
   python3 safety.py <in.html> <out.html>"""
import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__)) + '/'   # src/
A = HERE + '../assets/'   # art, sound and scene data
import sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n: sys.exit(f'safety.py: expected {n} got {c}: {a[:90]!r}')
    s = s.replace(a, b)

# a rescue copy, kept just before anything wipes the journal
rep("function persist(){",
    "const RESCUE=STORE+'-before-clear';\n"
    "function keepRescue(){try{if(state.entries.length||state.tasks.length)localStorage.setItem(RESCUE,JSON.stringify({...state,clearedAt:Date.now()}))}catch(_){}}\n"
    "function rescueInfo(){try{const r=JSON.parse(localStorage.getItem(RESCUE)||'null');return r&&Array.isArray(r.entries)?r:null}catch(_){return null}}\n"
    "function bringBack(){const r=rescueInfo();if(!r)return;delete r.clearedAt;try{localStorage.setItem(STORE,JSON.stringify(r));localStorage.removeItem(RESCUE)}catch(_){}location.reload()}\n"
    "function persist(){")

# dev panel: clearing needs a second tap, and keeps a rescue copy
rep("<button type=\"button\" id=\"devClear\">Clear all data</button>",
    "<button type=\"button\" id=\"devClear\">Clear all data</button>${rescueInfo()?'<button type=\"button\" id=\"devBack\">Bring back cleared data</button>':''}")
rep("$('#devClear').addEventListener('click',()=>{const dev=state.dev;",
    "$('#devBack')&&$('#devBack').addEventListener('click',bringBack);\n"
    "  $('#devClear').addEventListener('click',()=>{const b=$('#devClear');\n"
    "    if(b.dataset.arm!=='1'){b.dataset.arm='1';b.textContent='Tap again to clear everything';setTimeout(()=>{if(b.isConnected){b.dataset.arm='';b.textContent='Clear all data'}},4000);return}\n"
    "    keepRescue();const dev=state.dev;")

# Settings erase already confirms; it keeps a rescue copy too, and Settings offers to bring it back
rep("$('#eraseYes').addEventListener('click',()=>{const keep=",
    "$('#eraseYes').addEventListener('click',()=>{keepRescue();const keep=")
rep('<button class="btn small danger" type="button" id="eraseBtn">',
    '<button class="btn small" type="button" id="bringBackBtn" hidden>Bring back what was erased</button><button class="btn small danger" type="button" id="eraseBtn">')
rep("function renderSettings(){",
    "function renderSettings(){{const r=rescueInfo(),bb=$('#bringBackBtn');if(bb){bb.hidden=!r;if(r)bb.textContent=`Bring back what was erased (${r.entries.length} ${r.entries.length===1?'memory':'memories'})`}}")
rep("$('#restoreBtn').addEventListener('click',()=>$('#restoreFile').click());",
    "$('#restoreBtn').addEventListener('click',()=>$('#restoreFile').click());\n$('#bringBackBtn').addEventListener('click',bringBack);")
open(dst, 'w').write(s)
print('safety ok', len(s))
