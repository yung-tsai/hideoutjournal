"""The stream: a 3D scene (three.js), offered beside the river camp in Settings (the camp is the default again).
   - Settings > Scene: The stream / River camp, and a Postcard frame switch (on by default) for either scene.
   - Over the postcard the interface turns light, on a white page; full screen keeps the dark glass. (The camp's postcard is laid out by postcard.py.)
   - Memories is called Journal. The sound button is a plain on/off volume icon. The logo sits at the top.
   - Writing in the van and the van's looks belong to the river camp, so they hide while the stream is showing.
   python3 stream3d.py <in.html> <out.html>"""
import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__)) + '/'   # src/
A = HERE + '../assets/'   # art, sound and scene data
import sys, base64, os
src, dst = sys.argv[1], sys.argv[2]
s = open(src).read()
HERE = os.path.dirname(os.path.abspath(__file__)) + '/'
LOGO = A+'logo/hideout_logo.png'
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n: sys.exit(f'stream3d.py: expected {n} got {c}: {a[:90]!r}')
    s = s.replace(a, b)

# ---------- the scene layer, under everything ----------
rep("  if(!A||(renderPaused&&!tr))return;", "  if(!A||(renderPaused&&!tr)||(body.dataset.scene==='stream'&&!tr&&mode==='out'))return;   // the camp sleeps while the stream is showing")
rep('<div id="stage">', '<div id="scene3d" aria-hidden="true"></div>\n'
    '<div class="s3cap" id="s3cap" aria-hidden="true"><b id="s3capTitle"></b><span id="s3capSub"></span><code id="s3capData"></code></div>\n'
    '<p class="s3msg" id="s3msg" role="status" hidden></p>\n<div id="stage">')

# ---------- logo ----------
logo = 'data:image/png;base64,' + base64.b64encode(open(LOGO, 'rb').read()).decode()
rep('<div class="brand"><h1>Hideout</h1>', '<div class="brand"><h1 class="logo"><img src="' + logo + '" alt="Hideout Journal" width="585" height="321"></h1>')

# ---------- header: logo left, one menu in the middle (Journal, Tasks, Settings), volume far right ----------
import re as _re
_m = _re.search(r'  <div class="brand">.*?</div>\n', s, _re.S)
if not _m: sys.exit('stream3d.py: brand not found')
brand = _m.group(0); s = s[:_m.start()] + s[_m.end():]
rep('<header class="top">\n', '<header class="top">\n' + brand)
_g = _re.search(r'    <button class="icon" id="gearBtn" type="button" aria-label="Settings">(<svg.*?</svg>)</button>\n', s, _re.S)
if not _g: sys.exit('stream3d.py: gear not found')
gear_svg = _g.group(1); s = s[:_g.start()] + s[_g.end():]
rep('<span>Tasks</span></button></div>', '<span>Tasks</span></button><button class="tnb" type="button" id="gearBtn" aria-label="Settings">' + gear_svg + '<span>Settings</span></button></div>')

# ---------- Memories becomes Journal ----------
rep('data-tab="memories" aria-label="Memories"', 'data-tab="memories" aria-label="Journal"')
rep('<span>Memories</span>', '<span>Journal</span>')
rep('</svg>Memories</button>', '</svg>Journal</button>', 3)
rep('<h2 id="memH">Memories</h2>', '<h2 id="memH">Journal</h2>')
rep('aria-label="Close Memories"', 'aria-label="Close Journal"', 2)
rep('Saved to Memories', 'Saved to Journal', 3)

# ---------- Settings: scene and postcard ----------
rep('      <section class="sgroup"><h3>Retreat</h3>',
    '      <section class="sgroup"><h3>Scene</h3>\n'
    '        <p class="sl">Where your hideout is</p><div class="seg" id="setScene" role="group" aria-label="Scene"><button type="button" data-v="stream">The stream</button><button type="button" data-v="camp">River camp</button></div>\n'
    '        <div class="toggle-row" id="frameRow" style="margin-top:14px"><div><b>Postcard frame</b><span>Shows your scene as a framed print on a light page.</span></div><button class="switch" type="button" role="switch" id="setFrame" aria-label="Postcard frame"></button></div>\n'
    '      </section>\n'
    '      <section class="sgroup"><h3>Retreat</h3>')
rep("function renderSettings(){", "function renderSettings(){syncSceneUI();")
rep("const inVan=state.settings.writeWhere==='van';", "const inVan=state.settings.writeWhere==='van'&&document.body.dataset.scene!=='stream';")
rep("requestAnimationFrame(frame);\n(function waitReady(){",
    r"""/* ---------- the stream or the river camp ---------- */
function sceneOn(){return (state.settings.scene||'camp')==='stream'}
function syncSceneUI(){const v=state.settings.scene||'camp';$$('#setScene button').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.v===v)));
  $('#setFrame').setAttribute('aria-checked',String(state.settings.frame!==false))}
function applyScene(){const on=sceneOn();body.dataset.scene=on?'stream':'camp';body.dataset.frame=state.settings.frame!==false?'postcard':'full';syncSceneUI()}
$$('#setScene button').forEach(b=>b.addEventListener('click',()=>{state.settings.scene=b.dataset.v;persist();applyScene()}));
$('#setFrame').addEventListener('click',()=>{state.settings.frame=state.settings.frame===false;persist();applyScene()});
/* the volume icon is a plain on/off switch; the levels live in Settings */
$('#soundBtn').addEventListener('click',e=>{e.stopImmediatePropagation();e.preventDefault();$('#sndPop').hidden=true;toggleSound()},true);
applyScene();
requestAnimationFrame(frame);
(function waitReady(){""")

# ---------- styles ----------
rep('</style>', """
/* ---------- the stream ---------- */
#scene3d{position:fixed;inset:0;z-index:0;display:none}
#scene3d canvas{display:block;width:100%;height:100%}
body[data-scene="stream"] #scene3d{display:block}
body[data-scene="stream"] #stage,body[data-scene="stream"] .vignette{display:none}
body[data-scene="stream"][data-frame="postcard"] #scene3d{inset:auto;left:50%;top:var(--s3-top,84px);width:var(--s3-w,80vw);height:var(--s3-h,60vh);transform:translateX(-50%)}
.s3cap{display:none;position:fixed;left:0;right:0;top:var(--s3cap-top,80%);z-index:1;text-align:center;pointer-events:none;padding:0 16px}
body[data-frame="postcard"] .s3cap{display:block}
.s3cap b{display:block;font:500 15px/1.3 var(--ui);color:var(--ink)}
.s3cap span{display:block;font:400 13.5px/1.45 var(--ui);color:var(--ink-2)}
.s3cap code{display:block;margin-top:3px;font:400 11.5px/1.4 ui-monospace,SFMono-Regular,Menlo,monospace;color:var(--ink-3);letter-spacing:.05em}
.s3msg{position:fixed;left:50%;top:45%;transform:translateX(-50%);z-index:2;max-width:320px;text-align:center;font:400 16px/1.4 var(--serif);color:var(--ink-2)}
.top{grid-template-columns:1fr auto 1fr}
.top .brand{display:block;justify-self:start;text-align:left;grid-column:1}
.top .tnav{grid-column:2;justify-self:center;gap:6px}
.top .tools{grid-column:3;justify-self:end}
.brand h1.logo{margin:0;line-height:0;font-size:0}
.brand h1.logo img{height:52px;width:auto;display:block;margin:0}
body[data-scene="stream"] #place{display:none}
body[data-scene="stream"] .sgroup:has(#custBtn),body[data-scene="stream"] p.sl:has(+#setWhere),body[data-scene="stream"] #setWhere,body[data-scene="stream"] #setWhere+.note{display:none}
/* over the postcard: a light interface on a white page */
body[data-frame="postcard"]{background:#fbfaf7;
  --ground:#fbfaf7;--paper:#ffffff;--paper-2:rgba(31,42,51,.05);--paper-3:rgba(31,42,51,.1);
  --glass:rgba(255,255,255,.94);--glass-strong:#ffffff;--field:rgba(31,42,51,.04);
  --ink:#1f2a33;--ink-2:#55616b;--ink-3:#8a949c;--line:rgba(31,42,51,.1);--line-2:rgba(31,42,51,.18);
  --olive:#3f8a3a;--olive-ink:#ffffff;--accent:#c4552f;--danger:#b8432e;
  --frost:#ffffff;--frost-line:rgba(31,42,51,.12);--frost-hi:#f1f2ee;
  --shadow:0 18px 50px rgba(31,42,51,.12);--shadow-s:0 4px 16px rgba(31,42,51,.07)}
body[data-frame="postcard"] .jfield{background:#fff;border:1px solid var(--line);color:var(--ink-2)}
body[data-frame="postcard"] .jfield:hover{background:#fff;color:var(--ink)}
body[data-frame="postcard"] .tnb,body[data-frame="postcard"] .icon{-webkit-backdrop-filter:none;backdrop-filter:none}
@media (max-width:760px){.brand h1.logo img{height:40px}}
body[data-frame="postcard"] .switch::after{background:#fff}
body[data-frame="postcard"] .switch:not([aria-checked="true"]){background:#d9ddd6}
</style>""")

# ---------- three.js and the scene module ----------
mod = open(HERE + 'stream3d.js').read()
s = s.rstrip()
s += ('\n<script type="importmap">{"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",'
      '"three/addons/":"https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"}}</script>\n'
      '<script type="module">\n' + mod + '\n</script>\n')
open(dst, 'w').write(s)
print('stream3d ok', len(s))
