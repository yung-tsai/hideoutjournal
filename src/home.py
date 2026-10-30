"""Home refinements (after the frames).
   - Idle fade on Home: after 10 s without a mouse move, key or tap, the logo, the menu icon and the volume icon fade out while
     drifting up a little, and the field fades to 60% (it stays visible); the scene grows a few % into the room they free.
     Anything brings it all back. Never while writing, while the field has focus, while the sidebar is open, or on a page.
     prefers-reduced-motion: fade only (no drift, no growth).
   - A bigger scene: the card fills the height between the header and the field (the caption is gone, so its room is too);
     it snaps to whole device pixels per art pixel when that costs almost nothing (6%), so it stays crisp without shrinking.
   - The closed writing card's shadow no longer peeks up from below the page.
   - Sidebar: Home, Journal, Patterns, Tasks, Settings, and a small wordmark next to the toggle (the recent-entries list is gone).
     It starts collapsed; once someone toggles it, their choice is kept. The big centred logo shows on Home only.
   - ?record (for screen recordings): no Dev item, no centred logo, the cursor hides after 1 s still, and the idle fade starts after 2 s.
   python3 home.py <in.html> <out.html>"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)) + '/'
src, dst = sys.argv[1], sys.argv[2]
s = open(src).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n: sys.exit(f'home.py: expected {n} got {c}: {a[:90]!r}')
    s = s.replace(a, b)

# ---------- a bigger card: less room held back above and below it ----------
rep("top=ph?70:84,bottom=ph?150:178", "top=ph?70:88,bottom=ph?150:136")
rep("const k=n>=1&&n/dpr>=fit*.8?n/dpr:Math.floor(fit*AW*dpr)/(AW*dpr);",
    "const k=n>=1&&n/dpr>=fit*.94?n/dpr:Math.floor(fit*AW*dpr)/(AW*dpr);")   # whole device pixels per art pixel when that costs ≤6%
rep("(H-top-bottom-h-2*pcF()*w-70)*.42", "(H-top-bottom-h-2*pcF()*w)*.42")

# ---------- sidebar: no recent list; a small wordmark by the toggle ----------
LOGO = open(HERE + '../assets/logo/hideout_wordmark_clean.svg').read()
MINI = ('<button type="button" class="sbmark" id="sbMark" aria-label="Hideout, home"><svg viewBox="0 0 1208 590" aria-hidden="true" shape-rendering="geometricPrecision">'
        + LOGO[LOGO.index('<path'):LOGO.rindex('</svg>')] + '</svg></button>')
rep('<nav class="sb" id="sb" aria-label="Sidebar"><div class="sbtop">', '<nav class="sb" id="sb" aria-label="Sidebar">' + MINI + '<div class="sbtop">')
rep('<div class="sblist" id="sbList"></div>', '<div class="sblist" id="sbList" hidden></div><div class="sbfill"></div>')
rep("sbSet(!sbNarrow()&&state.meta.sbOpen!==false,true);", "sbSet(!sbNarrow()&&state.meta.sbOpen===true,true);")   # collapsed until someone opens it

# ---------- behaviour ----------
rep("let meadowOn=false;", r"""/* ---------- Home: the UI rests when you're still; ?record for screen recordings ---------- */
const REC=/[?&]record\b/.test(location.search);if(REC)document.body.dataset.record='1';
$('#sbMark').addEventListener('click',()=>go(''));
(function(){const B=document.body,wait=REC?2000:10000;let t=0,c=0;
  const calm=()=>!B.dataset.sheet&&B.dataset.focus!=='journal'&&B.dataset.sb!=='open'&&!(document.activeElement&&document.activeElement.closest&&document.activeElement.closest('.dock,.journal,.sb'));
  const rest=()=>{if(calm())B.dataset.hidle='1';else arm()};
  function arm(){clearTimeout(t);t=setTimeout(rest,wait)}
  function wake(){if(B.dataset.hidle)delete B.dataset.hidle;arm();
    if(REC){delete B.dataset.nocur;clearTimeout(c);c=setTimeout(()=>{B.dataset.nocur='1'},1000)}}
  ['pointermove','pointerdown','keydown','wheel','touchstart'].forEach(k=>addEventListener(k,wake,{passive:true,capture:true}));
  addEventListener('hashchange',wake);
  new MutationObserver(()=>{if(B.dataset.hidle&&!calm())wake()}).observe(B,{attributes:true,attributeFilter:['data-sheet','data-focus','data-sb']});
  wake()})();
let meadowOn=false;""")

# ---------- styles ----------
rep('</style>', """
/* ---------- Home at rest ---------- */
.top .mnwrap,.top .wmark,.top .tools{transition:opacity .9s ease,transform 1s cubic-bezier(.2,.8,.2,1),translate .45s cubic-bezier(.2,.8,.2,1)}
body[data-hidle] .top .mnwrap,body[data-hidle] .top .wmark,body[data-hidle] .top .tools{opacity:0;transform:translateY(-10px)}   /* still tappable: a tap on a faded icon works straight away */
body[data-frame="postcard"][data-hidle] .dock{opacity:.6}
body[data-frame="postcard"] :is(#meadow,#waterfall,#desert,#stage,#scnav,.pcfx){scale:calc(var(--shk,1) * var(--idk,1));transition:translate .45s cubic-bezier(.2,.8,.2,1),scale 1.4s cubic-bezier(.2,.8,.2,1)}
body[data-frame="postcard"][data-hidle]{--idk:1.035}
body[data-hidle] .scdots{opacity:0!important}
@media (prefers-reduced-motion:reduce){body[data-hidle] .top .mnwrap,body[data-hidle] .top .wmark,body[data-hidle] .top .tools{transform:none}
  body[data-frame="postcard"][data-hidle]{--idk:1}}
/* the closed writing card waits below the page; keep its shadow from showing there */
body:not([data-journal="up"]) .jcard{box-shadow:none}
/* ---------- sidebar: a small wordmark by the toggle; the big logo on Home only ---------- */
.sb{padding-top:calc(76px + var(--sa-t,0px))}
.sbmark{position:absolute;top:calc(25px + var(--sa-t,0px));left:76px;height:28px;padding:0;border:0;background:none;cursor:pointer;line-height:0}
.sbmark svg{height:28px;width:auto;display:block}
.sbfill{flex:1}
body[data-sheet] .top .wmark{opacity:0;pointer-events:none}
@media (max-width:760px){.sbmark{left:68px;top:calc(19px + var(--sa-t,0px))}}
/* ---------- ?record ---------- */
body[data-record] #sb [data-act="dev"],body[data-record] .top .wmark,body[data-record] #devChip{display:none!important}
body[data-record][data-nocur],body[data-record][data-nocur] *{cursor:none!important}
</style>""")

open(dst, 'w').write(s)
print('home ok', len(s))
