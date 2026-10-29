"""The waterfall: a pixel-art morning waterfall into a forest pool, the fourth choice in Settings > Scene (after the meadow, the camp and the stream).
   - body[data-scene] gains 'waterfall'. It's shown like the meadow: a 16:9 postcard on the light page (postcard.py's layout, deckled
     edge, its own caption), or full screen with the Postcard switch off; the burn opens in its card on wider screens.
   - The scene is src/waterfall.js (made by prototypes/waterfall/build.py). It starts the first time it shows and only draws while showing.
   python3 waterfall.py <in.html> <out.html>"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)) + '/'
src, dst = sys.argv[1], sys.argv[2]
s = open(src).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n: sys.exit(f'waterfall.py: expected {n} got {c}: {a[:90]!r}')
    s = s.replace(a, b)

# ---------- the scene layer ----------
rep('<div id="meadow" aria-hidden="true">', '<div id="waterfall" aria-hidden="true"><canvas id="waterfallCv" width="952" height="536" role="img" aria-label="Pixel-art waterfall falling into a forest pool in the morning, ferns swaying in front"></canvas><canvas class="pcEdge" aria-hidden="true"></canvas></div>\n<div id="meadow" aria-hidden="true">')

# ---------- Settings: a fourth scene ----------
rep('<button type="button" data-v="stream">The stream</button></div>', '<button type="button" data-v="stream">The stream</button><button type="button" data-v="waterfall">The waterfall</button></div>')
rep("return v==='camp'||v==='stream'?v:'meadow'}", "return v==='camp'||v==='stream'||v==='waterfall'?v:'meadow'}")
rep("if(body.dataset.scene==='meadow')startMeadow();", "if(body.dataset.scene==='meadow')startMeadow();if(body.dataset.scene==='waterfall')startWaterfall();")

# ---------- caption ----------
rep("function pcCaption(){if(document.body.dataset.scene==='meadow'){",
    "const WATERFALL_CAP=['The waterfall, morning','Spray rising off the pool · the ferns moving in the cool air','WIND 3 KM/H · 11 °C · CLEAR'];\n"
    "function pcCaption(){if(document.body.dataset.scene==='waterfall'){const T=document.getElementById('s3capTitle');if(T){T.textContent=WATERFALL_CAP[0];document.getElementById('s3capSub').textContent=WATERFALL_CAP[1];document.getElementById('s3capData').textContent=WATERFALL_CAP[2]}return}\n"
    "  if(document.body.dataset.scene==='meadow'){")
rep("let meadowOn=false;", """let waterfallOn=false;
function startWaterfall(){if(waterfallOn||!window.WaterfallScene)return;waterfallOn=true;
  window.__waterfall=WaterfallScene.start(document.getElementById('waterfallCv'),()=>document.body.dataset.scene==='waterfall'&&!document.hidden)}
let meadowOn=false;""")

# ---------- styles: the same as the meadow's ----------
rep('/* ---------- the meadow ---------- */', """/* ---------- the waterfall ---------- */
#waterfall{position:fixed;inset:0;z-index:0;display:none;overflow:hidden;background:#0f0c10}
#waterfall #waterfallCv{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;image-rendering:pixelated;image-rendering:crisp-edges}
#waterfall canvas.pcEdge{position:absolute;inset:0;width:100%;height:100%;pointer-events:none;z-index:2;display:none}
body[data-scene="waterfall"] #waterfall{display:block}
body[data-scene="waterfall"] #stage,body[data-scene="waterfall"] .vignette{display:none}
body[data-scene="waterfall"][data-frame="postcard"] #waterfall{inset:auto;left:var(--pc-left,50%);top:var(--pc-top,84px);width:var(--pc-w,952px);height:var(--pc-h,536px);background:transparent}
body[data-scene="waterfall"][data-frame="postcard"] #waterfall canvas.pcEdge{display:block}
body[data-scene="waterfall"][data-frame="postcard"] .s3cap{top:var(--pccap-top,80%)}
body[data-scene="waterfall"] #place{display:none}
body[data-scene="waterfall"] .sgroup:has(#custBtn),body[data-scene="waterfall"] p.sl:has(+#setWhere),body[data-scene="waterfall"] #setWhere,body[data-scene="waterfall"] #setWhere+.note{display:none}
@media (min-width:700px) and (min-height:560px){
body[data-scene="waterfall"][data-frame="postcard"] .fire{inset:auto;left:var(--pc-left,50%);top:var(--pc-top,84px);width:var(--pc-w,952px);height:var(--pc-h,536px)}
body[data-scene="waterfall"][data-frame="postcard"] .fire canvas.pcEdge{display:block}}
/* ---------- the meadow ---------- */""")

# ---------- the scene module, beside the meadow's ----------
mod = open(HERE + 'waterfall.js').read()
rep('<script>\n/* The meadow', '<script>\n' + mod + '\n</script>\n<script>\n/* The meadow')

open(dst, 'w').write(s)
print('waterfall ok', len(s))
