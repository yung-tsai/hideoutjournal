"""Write where you are: tapping the field opens the journal card right there in the scene (or in the van, by setting).
   One card everywhere: mic on the right, Save as the main button, and Reflect on it / Burn it under the arrow.
   python3 write.py <in.html> <out.html>"""
import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__)) + '/'   # src/
A = HERE + '../assets/'   # art, sound and scene data
import sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n: sys.exit(f'write.py: expected {n} got {c}: {a[:90]!r}')
    s = s.replace(a, b)
MIC_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="9" y="3.5" width="6" height="11" rx="3"/><path d="M5.5 11.5a6.5 6.5 0 0 0 13 0M12 18v2.5"/></svg>'

# ---------- the setting: where you write ----------
rep("settings:{reflectionStyle:'curious',defaultInput:'write',sound:false,reducedMotion:osReduced,volume:80,volWater:100,volBirds:100},",
    "settings:{reflectionStyle:'curious',defaultInput:'write',sound:false,reducedMotion:osReduced,volume:80,volWater:100,volBirds:100,writeWhere:'out'},")
i = s.index('<div class="seg" id="setInput"'); j = s.index('</div>', i) + len('</div>')
s = s[:j] + ('\n        <p class="sl" style="margin-top:16px">Where you write</p>'
             '<div class="seg" id="setWhere" role="group" aria-label="Where you write"><button type="button" data-v="out">Outside</button><button type="button" data-v="van">In the van</button></div>'
             '<p class="note" style="margin-top:8px">Outside, the page opens right where you are. In the van, you step inside first.</p>') + s[j:]
rep("function renderSettings(){",
    "function renderSettings(){$$('#setWhere button').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.v===(state.settings.writeWhere||'out'))));")
rep("$$('[data-start]').forEach(b=>b.addEventListener('click',()=>startJournal(b.dataset.start)));",
    "$$('[data-start]').forEach(b=>b.addEventListener('click',()=>startJournal(b.dataset.start)));\n"
    "$$('#setWhere button').forEach(b=>b.addEventListener('click',()=>{state.settings.writeWhere=b.dataset.v;persist();renderSettings()}));")

# ---------- write outside: no walk into the van ----------
rep("  startEnter(()=>{Sound.update();if(!session)return;if(kind==='talk')startListening()});\n  Sound.update();\n}",
    "  const inVan=state.settings.writeWhere==='van';body.dataset.where=inVan?'van':'out';\n"
    "  $('#jLeave').textContent=inVan?'Step outside':'Close';$('#sOut').textContent=inVan?'Head outside':'Done';\n"
    "  const go=()=>{Sound.update();if(!session)return;if(kind==='talk')startListening()};\n"
    "  if(inVan)startEnter(go);else go();   // outside: the page just opens where you are\n"
    "  Sound.update();\n}")

# ---------- one finish row: mic, Save, and the arrow for Reflect / Burn ----------
rep('<div class="jrow"><button class="linkbtn" type="button" id="jToTalk">Talk instead</button><div class="right"><div class="split" id="jSplit"><button class="btn solid" type="button" id="jReflect" disabled>Reflect</button>',
    '<div class="jrow jfinish"><div class="right"><button class="jmic" type="button" id="jToTalk" aria-label="Talk instead" title="Talk instead">' + MIC_SVG + '</button><div class="split" id="jSplit"><button class="btn solid" type="button" id="jSaveMain" disabled>Save</button>')
rep('<button type="button" role="menuitem" id="jJustSave">Just save<small>Kept, without a reflection</small></button>',
    '<button type="button" role="menuitem" id="jReflect" disabled>Reflect on it<small>A few thoughtful lines back</small></button>')
rep("$('#jJustSave').addEventListener('click',justSave);",
    "$('#jSaveMain').addEventListener('click',justSave);\n"
    "{const sm=$('#jSaveMain'),rf=$('#jReflect');new MutationObserver(()=>{sm.disabled=rf.disabled}).observe(rf,{attributes:true,attributeFilter:['disabled']});sm.disabled=rf.disabled}")
rep("setTimeout(()=>{try{$('#jJustSave').focus()}catch(_){}},0)});", "setTimeout(()=>{try{$('#jReflect').focus()}catch(_){}},0)});")
rep("$('#jReflect').addEventListener('click',runReflect);", "$('#jReflect').addEventListener('click',()=>{closeFinish();runReflect()});")
rep("Here’s what I heard. Fix anything before Hideout reflects.", "Here’s what I heard. Fix anything before you save.")
rep("/* ---------- finishing an entry: Reflect, Just save, or Burn it ---------- */",
    "/* ---------- finishing an entry: Save, or under the arrow, Reflect on it or Burn it ---------- */")

rep("</style>", """
/* ---------- one card for writing, outside or in the van ---------- */
.jfinish .right{display:flex;align-items:center;gap:6px;margin-left:auto}
.jfinish .jmic{width:44px;height:44px}
.jfinish .jmic[hidden]{display:none}
</style>""")
open(dst, 'w').write(s)
print('write ok', len(s))
