"""UI refresh (light, calm, minimal): forest green for actions and selected states, calm neutrals for everything else; red only in the logo.
   - Header: a menu icon on the left, the red "Hideout" wordmark alone in the centre (assets/logo/hideout_wordmark_clean.svg, inlined),
     the volume icon on the right.
   - Menu icon: it opens the sidebar (nav.py). A small green dot sits on it (and on Tasks in the sidebar) when new tasks have been
     caught; it clears once Tasks is opened (state.meta.tasksSeenN).
   - Journal: Entries / Patterns as underlined tabs, the search field on top, entry cards with a thumbnail (the scene, a placeholder
     for now), date and time, title, a short preview and a muted mood chip.
   - Settings: Reflection style, a Scene picker with thumbnails, and a Sound section.
   python3 refresh.py <in.html> <out.html>"""
import os, sys, io, json, base64
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)) + '/'
ROOT = HERE + '../'
src, dst = sys.argv[1], sys.argv[2]
s = open(src).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n: sys.exit(f'refresh.py: expected {n} got {c}: {a[:90]!r}')
    s = s.replace(a, b)

# ---------- scene thumbnails (16:9), from each scene's own picture ----------
def thumb(im):
    im = im.convert('RGB'); w, h = im.size; t = h * 16 // 9
    if t < w: im = im.crop(((w - t) // 2, 0, (w - t) // 2 + t, h))
    im = im.resize((320, 180), Image.LANCZOS); b = io.BytesIO(); im.save(b, 'JPEG', quality=82)
    return 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode()
camp = json.load(open(ROOT + 'assets/newscene/sunset_set.json'))['base']
THUMBS = {'meadow': thumb(Image.open(ROOT + 'assets/meadow/master.png')),
          'camp': thumb(Image.open(io.BytesIO(base64.b64decode(camp.split(',', 1)[1])))),
          'waterfall': thumb(Image.open(ROOT + 'prototypes/waterfall/master.png')),
          'desert': thumb(Image.open(ROOT + 'prototypes/desert/master.png'))}

# ---------- header: menu icon, wordmark, volume ----------
LOGO = open(ROOT + 'assets/logo/hideout_wordmark_clean.svg').read()
WORDMARK = ('<svg class="wordmark" viewBox="0 0 1208 590" role="img" aria-label="Hideout" shape-rendering="geometricPrecision">'
            + LOGO[LOGO.index('<path'):LOGO.rindex('</svg>')] + '</svg>')   # the hand-lettered wordmark, inlined so it stays sharp at any size
MENU = ('<div class="mnwrap"><button class="icon mnbtn" type="button" id="menuBtn" aria-expanded="false" aria-controls="sheet" aria-label="Menu">'
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><path d="M4.5 7h15M4.5 12h15M4.5 17h15"/></svg>'
        '<i class="mndot" id="menuDot" hidden aria-hidden="true"></i></button></div>')   # it opens the sidebar (nav.py)
rep('<header class="top">\n', '<header class="top">\n' + MENU + '<div class="wmark">' + WORDMARK + '</div>\n')

# ---------- Journal: search on top, entry cards with a thumbnail ----------
rep('<input id="memSearch" type="search" placeholder="Search your memories…" aria-label="Search memories" autocomplete="off">',
    '<input id="memSearch" type="search" placeholder="Search your journal" aria-label="Search your journal" autocomplete="off">')
rep('html+=`<li><button class="mem" type="button" data-id="${esc(e.id)}"><div class="mtop"><span>${esc(dayLabel(e.at))} · ${esc(fTime.format(new Date(e.at)))}</span>${moodHTML(e)}</div>',
    'html+=`<li><button class="mem" type="button" data-id="${esc(e.id)}"><img class="mthumb" src="${entryThumb(e)}" alt="" loading="lazy"><div class="mtop"><span>${esc(dayLabel(e.at))} · ${esc(fTime.format(new Date(e.at)))}</span>${moodHTML(e)}</div>')

# ---------- Settings: Sound gets its own heading ----------
rep('<section class="sgroup"><h3>Retreat</h3>', '<section class="sgroup"><h3>Sound</h3>')

# ---------- behaviour ----------
rep("let meadowOn=false;", r"""/* ---------- UI refresh: the new-tasks dot, scene thumbnails ---------- */
const SCENE_THUMB=""" + json.dumps(THUMBS) + r""";
function entryThumb(e){return SCENE_THUMB[e.scene]||SCENE_THUMB[document.body.dataset.scene]||SCENE_THUMB.meadow}   // the scene, as a placeholder
(function(){
  // scene thumbnails in Settings
  $$('#setScene button').forEach(b=>{const v=b.dataset.v;if(!SCENE_THUMB[v]||b.querySelector('img'))return;b.insertAdjacentHTML('afterbegin',`<img src="${SCENE_THUMB[v]}" alt="">`)});
  // search above the tabs in the Journal
  const pg=$('#pg-memories .phead'),tr=$('#pg-memories .tools-row');if(pg&&tr)pg.after(tr);})();
if(state.meta.tasksSeenN==null){state.meta.tasksSeenN=state.tasks.length;persist()}
function updateMenuDot(){const n=state.tasks.length>(state.meta.tasksSeenN||0);$('#menuDot').hidden=!n;$('#menuDotT').hidden=!n}
{const _persist=persist;persist=function(){_persist();updateMenuDot()}}
updateMenuDot();
let meadowOn=false;""")
rep("  if(name==='tasks')renderTasks();", "  if(name==='tasks'){renderTasks();state.meta.tasksSeenN=state.tasks.length;persist()}")
rep('function addTasks(texts,entry){', 'function addTasks(texts,entry){if(entry&&!entry.scene)entry.scene=document.body.dataset.scene;')

# ---------- styles ----------
rep('</style>', """
/* ---------- UI refresh: tokens ---------- */
body[data-frame="postcard"]{background:#f7f6f2;
  --ground:#f7f6f2;--paper:#ffffff;--paper-2:#f1f0eb;--paper-3:#e8e7e1;--glass:#ffffff;--glass-strong:#ffffff;--field:#f3f2ee;
  --ink:#1e2622;--ink-2:#5b6560;--ink-3:#8c948f;--line:rgba(30,38,34,.10);--line-2:rgba(30,38,34,.18);
  --olive:#2f5d3e;--olive-ink:#ffffff;--accent:#2f5d3e;--danger:#1e2622;--green:#2f5d3e;--green-2:#e7efe9;
  --frost:#ffffff;--frost-line:rgba(30,38,34,.10);--frost-hi:#f1f0eb;
  --shadow:0 16px 44px rgba(30,38,34,.10);--shadow-s:0 3px 12px rgba(30,38,34,.06)}
:root{--logo:#c0392b}
/* ---------- header: menu left, wordmark centre, volume right ---------- */
.top .brand,.top .tnav{display:none!important}
.top{display:grid;grid-template-columns:1fr auto 1fr;align-items:center}
.mnwrap{grid-column:1;justify-self:start;position:relative}
.wmark{grid-column:2;justify-self:center;line-height:0}
.wordmark{height:46px;width:auto;display:block}
.top .tools{grid-column:3;justify-self:end}
.mnbtn{position:relative}
.mndot{position:absolute;top:7px;right:7px;width:8px;height:8px;border-radius:50%;background:var(--green,#2f5d3e);box-shadow:0 0 0 2px var(--paper,#fff)}
.mndot.in{position:static;display:inline-block;width:6px;height:6px;margin-left:6px;vertical-align:2px;box-shadow:none}
body[data-frame="postcard"] .icon{background:var(--paper);border:1px solid var(--line);color:var(--ink)}
@media (max-width:760px){.wordmark{height:38px}}
/* ---------- actions and selected states in forest green ---------- */
body[data-frame="postcard"] .seg button[aria-pressed="true"],body[data-frame="postcard"] .btn.solid{background:var(--green);color:#fff;border-color:var(--green)}
body[data-frame="postcard"] .switch[aria-checked="true"]{background:var(--green)}
body[data-frame="postcard"] .radio input:checked+span::before,body[data-frame="postcard"] input[type=radio]{accent-color:var(--green)}
body[data-frame="postcard"] #jText,body[data-frame="postcard"] input,body[data-frame="postcard"] textarea{caret-color:var(--green)}
body[data-frame="postcard"] .mood{background:var(--paper-2);color:var(--ink-2);border:0}
body[data-frame="postcard"] .mood i{background:var(--m);opacity:.55}
/* ---------- the Journal ---------- */
#pg-memories .tools-row{display:flex;flex-direction:column;gap:12px;margin:2px 0 4px}
#pg-memories .search{width:100%}
#pg-memories .chips{display:none}
.memseg{display:flex;gap:22px;background:none!important;border:0!important;padding:0!important;box-shadow:none!important;margin-top:14px;border-bottom:1px solid var(--line)!important;border-radius:0!important}
.memseg button{height:auto!important;padding:0 0 9px!important;border-radius:0!important;background:none!important;color:var(--ink-3)!important;font:500 15px/1.2 var(--ui)!important;border-bottom:2px solid transparent!important;margin-bottom:-1px}
.memseg button[aria-pressed="true"]{color:var(--ink)!important;border-bottom-color:var(--green)!important}
#pg-memories .phead{display:block}
#pg-memories .phead>div{display:flex;flex-direction:column}
#pg-memories .phead .close{position:absolute;top:16px;right:16px}
.feed{border-left:0;padding-left:0}
.feed li::before{display:none}
.feed li+li{margin-top:10px}
.mem{display:grid!important;grid-template-columns:92px 1fr;grid-template-areas:"img top" "img h" "img p" "img meta";column-gap:14px;padding:10px!important;border:1px solid var(--line)!important;border-radius:14px!important;background:var(--paper)!important}
.mem:hover{border-color:var(--line-2)!important}
.mthumb{grid-area:img;width:92px;height:72px;object-fit:cover;border-radius:10px;image-rendering:pixelated;align-self:start}
.mem .mtop{grid-area:top;align-items:center}
.mem h3{grid-area:h;margin:3px 0 2px!important;font:600 15.5px/1.3 var(--ui)!important}
.mem .prev{grid-area:p;font-size:13.5px!important;-webkit-line-clamp:2}
.mem .mmeta{grid-area:meta}
.month{font:600 11.5px/1 var(--ui);letter-spacing:.12em;text-transform:uppercase;color:var(--ink-3);margin:20px 0 10px}
/* ---------- Settings ---------- */
body[data-frame="postcard"] .radio{background:var(--paper);border-color:var(--line)}
body[data-frame="postcard"] .radio:has(input:checked){background:var(--green-2);border-color:var(--green)}
body[data-frame="postcard"] .radio input{appearance:none;-webkit-appearance:none;flex:none;width:18px;height:18px;margin:2px 0 0;border-radius:50%;border:1.5px solid var(--ink-3);background:var(--paper)}
body[data-frame="postcard"] .radio input:checked{border-color:var(--green);background:radial-gradient(circle,var(--green) 0 4.5px,transparent 5px)}
.sgroup h3{font:600 11.5px/1 var(--ui);letter-spacing:.12em;text-transform:uppercase;color:var(--ink-3)}
#setScene{display:grid!important;grid-template-columns:repeat(2,1fr);gap:10px;background:none!important;border:0!important;padding:0!important;box-shadow:none!important}
#setScene button{display:flex;flex-direction:column;align-items:stretch;gap:7px;height:auto!important;padding:6px 6px 9px!important;border-radius:12px!important;border:1px solid var(--line)!important;background:var(--paper)!important;color:var(--ink-2)!important;font:500 13.5px/1.2 var(--ui)!important;text-align:center}
#setScene button img{width:100%;aspect-ratio:16/9;object-fit:cover;border-radius:8px;image-rendering:pixelated;display:block}
#setScene button[aria-pressed="true"]{border:2px solid var(--green)!important;color:var(--ink)!important;padding:5px 5px 8px!important}
</style>""")

open(dst, 'w').write(s)
print('refresh ok', len(s))
