"""Post-process the assembled app: rename to Hideout and apply a UI theme.
   python3 theme.py <in.html> <out.html> <lantern|adaptive|none>"""
import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__)) + '/'   # src/
A = HERE + '../assets/'   # art, sound and scene data
import sys, re
src, dst, theme = sys.argv[1], sys.argv[2], sys.argv[3]
s = open(src).read()

def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n: sys.exit(f'expected {n} got {c}: {a[:80]!r}')
    s = s.replace(a, b)

# ---------- name: Talio -> Hideout (storage keys and test hooks stay) ----------
rep('<title>Talio</title>', '<title>Hideout Journal</title>')
rep('<div class="brand"><h1>Talio</h1>', '<div class="brand"><h1>Hideout</h1>')
rep('Talio mostly listens', 'Hideout mostly listens')
rep('Talio sometimes asks', 'Hideout sometimes asks')
rep('Talio regularly offers', 'Hideout regularly offers')
rep('Talio is reading this', 'Hideout is reading this')
rep('Talio catches it', 'Hideout catches it')
rep('Fix anything before Talio reflects.', 'Fix anything before Hideout reflects.')
rep('You are Talio, the calm, warm voice inside a cozy journaling app', 'You are the calm, warm voice of Hideout, a cozy journaling app')
rep('How Talio sounds:', 'How you sound:')
rep('Talio’s reflections and tasks stay', 'Reflections and tasks stay')
rep('<h4 class="dh">Talio</h4>', '<h4 class="dh">Reflection</h4>')
s = s.replace('/* Talio river camp:', '/* Hideout river camp:').replace('   Talio river camp —', '   Hideout river camp —').replace('   Talio app layer:', '   Hideout app layer:')

# ---------- one "Reflect" button: opens Write by default; Settings can make it open Talk ----------
import re as _re
_m=_re.search(r'    <button class="start" type="button" data-start="talk">.*?</button>\n    <button class="start" type="button" data-start="write">.*?</button>\n',s,_re.S)
if not _m: sys.exit('dock buttons not found')
s=s[:_m.start()]+'    <button class="start" type="button" data-start="reflect" data-primary="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 20h4L19 9l-4-4L4 16z"/><path d="m13.5 6.5 4 4"/></svg>Reflect</button>\n'+s[_m.end():]
rep('<p class="sl" style="margin-top:16px">Default input</p>','<p class="sl" style="margin-top:16px">Reflect opens with</p>')
rep('<div class="seg" id="setInput" role="group" aria-label="Default input"><button type="button" data-v="talk">Talk</button><button type="button" data-v="write">Write</button><button type="button" data-v="last">Remember last choice</button></div>',
    '<div class="seg" id="setInput" role="group" aria-label="Reflect opens with"><button type="button" data-v="write">Write</button><button type="button" data-v="talk">Talk</button></div>')
rep("$$('#setInput button').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.v===state.settings.defaultInput)));",
    "$$('#setInput button').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.v===resolvedInput())));")
rep("function resolvedInput(){const d=state.settings.defaultInput;return d==='last'?state.meta.lastInput||'talk':d}",
    "function resolvedInput(){return state.settings.defaultInput==='talk'?'talk':'write'}   // Reflect opens Write unless Settings says Talk")
rep("function updateDock(){const p=resolvedInput(),row=$('.dock-row');$$('[data-start]').forEach(b=>b.dataset.primary=String(b.dataset.start===p));\n  row.prepend($(`[data-start=\"${p}\"]`))}",
    "function updateDock(){}")
rep("function startJournal(kind){","function startJournal(kind){if(kind==='reflect'||!kind)kind=resolvedInput();")
rep("defaultInput:'talk'","defaultInput:'write'")
rep("applyMotion();buildRV();size();applyWorld();updateDock();",
    "if(!state.meta.reflectV1){state.settings.defaultInput='write';state.meta.reflectV1=true;persist()}   // one-time: Reflect now opens Write\napplyMotion();buildRV();size();applyWorld();updateDock();")

# time of day on <body>, for the adaptive tint
rep("function applyWorld(){resolveWorld();applyState();updatePlace();Sound.update()}",
    "function applyWorld(){resolveWorld();document.body.dataset.tod=ST.time;applyState();updatePlace();Sound.update()}")

if theme != 'none':
    # fonts: pixel only for the wordmark; a warm serif for reading moments; Figtree for controls
    rep('family=Pixelify+Sans:wght@400;500;600&family=Figtree:wght@400;500;600&display=swap',
        'family=Pixelify+Sans:wght@600&family=Newsreader:opsz,wght@6..72,400;6..72,500&family=Figtree:wght@400;500;600&display=swap')
    css = '''
/* ---------- theme: readable type + glass that sits on every time of day ---------- */
:root{
  --serif:"Newsreader","Iowan Old Style",Georgia,serif;--pixel:var(--ui);
  --glass:rgba(15,18,24,.6);--glass-strong:rgba(15,18,24,.86);--frost:rgba(15,18,24,.5);--frost-hi:rgba(30,35,46,.7);
  --frost-line:rgba(232,236,242,.14);--paper:#141820;--paper-2:rgba(226,232,242,.07);--paper-3:rgba(226,232,242,.14);--field:rgba(0,0,0,.26);
  --ink:#eef0f2;--ink-2:#c5cad2;--ink-3:#8f97a3;--line:rgba(232,236,242,.12);--line-2:rgba(232,236,242,.22);
  --olive:#dcae6c;--olive-ink:#24190e;--accent:#d99a58;--danger:#e8907a;
}
.brand h1{font:600 32px/1 "Pixelify Sans",ui-monospace,monospace;letter-spacing:.01em}
.brand p{font-family:var(--ui)}
.tab{font:500 14.5px/1 var(--ui);letter-spacing:0}
.start{font:600 15px/1 var(--ui);letter-spacing:0}
.btn,.cust,.peekpill{font-family:var(--ui);letter-spacing:0}
.btn{font-weight:600;font-size:14px}
.soon b{font:600 14.5px/1.2 var(--ui)}
.dock-q{font:400 22px/1.25 var(--serif);letter-spacing:0;text-shadow:0 1px 2px rgba(6,8,12,.75),0 0 12px rgba(6,8,12,.55),0 0 28px rgba(6,8,12,.35)}
.phead h2{font:400 30px/1.1 var(--serif)}
.jq{font:400 24px/1.25 var(--serif)}
.rtitle{font:500 24px/1.2 var(--serif)}
.thinking,.saved,.follow p,.dtitle,.empty strong{font-family:var(--serif)}
.mem h3{font:500 18px/1.3 var(--serif)}
.sheet{-webkit-backdrop-filter:blur(18px) saturate(1.15);backdrop-filter:blur(18px) saturate(1.15)}
@media (max-width:760px){.dock-q{font-size:20px}.jq{font-size:21px}}
'''
    if theme == 'adaptive':
        css += '''
/* adaptive: the glass takes the scene's own shadow color */
body[data-tod="morning"]{--glass:rgba(36,28,44,.58);--glass-strong:rgba(32,25,40,.88);--frost:rgba(36,28,44,.48);--paper:#201a28}
body[data-tod="midday"]{--glass:rgba(12,30,32,.56);--glass-strong:rgba(11,27,29,.88);--frost:rgba(12,30,32,.46);--paper:#0f2224}
body[data-tod="golden"]{--glass:rgba(36,24,34,.6);--glass-strong:rgba(32,21,30,.88);--frost:rgba(36,24,34,.5);--paper:#22161f}
body[data-tod="night"]{--glass:rgba(14,18,40,.6);--glass-strong:rgba(12,15,34,.88);--frost:rgba(14,18,40,.5);--paper:#111530}
'''
    rep('</style>', css + '</style>')

open(dst, 'w').write(s)
print('ok', theme, len(s))
