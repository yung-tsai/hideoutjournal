"""The bottom of the screen is one thing: a writing field. Memories and Tasks move to the top left.
   Tapping the field opens the same journal card in the van (fast capture), with the cursor waiting.
   python3 field.py <in.html> <out.html>"""
import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__)) + '/'   # src/
A = HERE + '../assets/'   # art, sound and scene data
import sys, re
src, dst = sys.argv[1], sys.argv[2]
s = open(src).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n: sys.exit(f'field.py: expected {n} got {c}: {a[:90]!r}')
    s = s.replace(a, b)

MEM_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="5" y="3.5" width="14" height="17" rx="2"/><path d="M9 8h6M9 12h6M9 16h3"/></svg>'
TASK_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="4" y="5" width="4" height="4" rx="1"/><path d="M11 7h9"/><rect x="4" y="14" width="4" height="4" rx="1"/><path d="M11 16h9"/></svg>'
MIC_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="9" y="3.5" width="6" height="11" rx="3"/><path d="M5.5 11.5a6.5 6.5 0 0 0 13 0M12 18v2.5"/></svg>'

# ---------- the bar becomes a field ----------
i = s.index('<div class="dock" id="dock">'); i = s.index('  <div class="dock-row">', i)
j = s.index('  </div>\n</div>', i) + len('  </div>\n')
s = s[:i] + ('  <div class="dock-row field">\n'
             '    <button class="jfield" type="button" data-start="write" id="jField" aria-label="Start writing: How did today go?"><span class="caret" aria-hidden="true"></span><span class="ph" id="fieldQ">How did today go?</span></button>\n'
             '    <button class="jmic" type="button" data-start="talk" aria-label="Talk instead" title="Talk instead">' + MIC_SVG + '</button>\n'
             '  </div>\n') + s[j:]
# the prompt now lives in the field itself
rep("  $('#dockQ').textContent=PROMPTS[ST.time];",
    "  $('#dockQ').textContent=PROMPTS[ST.time];$('#fieldQ').textContent=PROMPTS[ST.time];$('#jField').setAttribute('aria-label','Start writing: '+PROMPTS[ST.time]);")

# ---------- Memories and Tasks, top left ----------
rep('<header class="top">',
    '<header class="top">\n  <div class="tnav" role="navigation" aria-label="Sections">'
    '<button class="tab tnb" type="button" data-tab="memories" aria-label="Memories">' + MEM_SVG + '<span>Memories</span></button>'
    '<button class="tab tnb" type="button" data-tab="tasks" aria-label="Tasks">' + TASK_SVG + '<span>Tasks</span></button></div>')
rep("t.closest('.dock')&&page===t.dataset.tab?null:t.dataset.tab", "t.closest('.dock,.tnav')&&page===t.dataset.tab?null:t.dataset.tab")   # tap again to close

# ---------- just start typing (keyboard) ----------
rep("$$('[data-start]').forEach(b=>b.addEventListener('click',()=>startJournal(b.dataset.start)));",
    "$$('[data-start]').forEach(b=>b.addEventListener('click',()=>startJournal(b.dataset.start)));\n"
    "/* on a keyboard, typing a letter outside starts an entry with that letter */\n"
    "addEventListener('keydown',ev=>{if(ev.defaultPrevented||ev.metaKey||ev.ctrlKey||ev.altKey||ev.key.length!==1||!/\\S/.test(ev.key))return;\n"
    "  const tg=ev.target;if(tg&&(tg.closest('input,textarea,select,[contenteditable]')))return;\n"
    "  if(mode!=='out'||session||page||body.dataset.focus)return;\n"
    "  ev.preventDefault();startJournal('write');if(session&&session.kind==='write'){jText.value+=ev.key;jText.dispatchEvent(new Event('input'));try{jText.focus({preventScroll:true});jText.setSelectionRange(jText.value.length,jText.value.length)}catch(_){}}});")

rep("</style>", """
/* ---------- the writing field at the bottom; sections at the top ---------- */
.dock-q{display:none}
p.sl:has(+ #setInput),#setInput{display:none}   /* the field writes and the mic talks, so this choice is gone */
.dock-row.field{gap:6px;padding:6px;width:min(560px,calc(100vw - 28px - var(--sa-l,0px) - var(--sa-r,0px)))}
.jfield{flex:1;min-width:0;display:flex;align-items:center;gap:10px;min-height:50px;padding:0 18px;border:0;border-radius:calc(var(--r) - 2px);
  background:rgba(255,255,255,.07);color:var(--ink-2);font:400 18px/1.3 var(--serif);text-align:left;cursor:text;transition:background .2s,color .2s}
.jfield:hover{background:rgba(255,255,255,.11);color:var(--ink)}
.jfield:focus-visible{outline:2px solid var(--olive);outline-offset:2px}
.jfield .ph{flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.jfield .caret{flex:none;width:2px;height:21px;border-radius:1px;background:var(--accent);animation:fieldBlink 1.15s steps(1) infinite}
@keyframes fieldBlink{50%{opacity:0}}
body[data-motion="reduced"] .jfield .caret{animation:none}
@media (prefers-reduced-motion:reduce){.jfield .caret{animation:none}}
.jmic{flex:none;width:50px;height:50px;display:grid;place-items:center;border:0;border-radius:calc(var(--r) - 2px);background:none;color:var(--ink-2);cursor:pointer;transition:background .2s,color .2s}
.jmic svg{width:21px;height:21px}
.jmic:hover{background:var(--paper-2);color:var(--ink)}
.top{justify-content:space-between}
.tnav{display:flex;gap:8px}
.tnb{display:inline-flex;align-items:center;gap:8px;height:40px;padding:0 14px 0 12px;border-radius:var(--r);border:1px solid var(--frost-line);background:var(--frost);
  box-shadow:var(--shadow-s);color:var(--ink);font:500 14px/1 var(--ui);cursor:pointer;-webkit-backdrop-filter:blur(12px);backdrop-filter:blur(12px)}
.tnb svg{width:18px;height:18px}
.tnb:hover{background:var(--paper-2)}
.tnb[aria-current="page"]{background:var(--paper-3)}
@media (max-width:760px){.tnb{width:40px;padding:0;justify-content:center}.tnb span{display:none}.jfield{font-size:17px;padding:0 16px}}
</style>""")
open(dst, 'w').write(s)
print('field ok', len(s))
