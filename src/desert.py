"""The desert: a pixel-art sunset desert, the fourth choice in Settings > Scene (after the meadow, the camp and the waterfall).
   - body[data-scene] gains 'desert'. Shown like the meadow and the waterfall: a 16:9 postcard on the light page, its own caption,
     or full screen with the Postcard switch off; the burn opens in its card on wider screens.
   - The scene is src/desert.js (made by prototypes/desert/build.py; the sky's saturation uses the test page's starting values).
     It starts the first time it shows and only draws while showing.
   python3 desert.py <in.html> <out.html>"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)) + '/'
src, dst = sys.argv[1], sys.argv[2]
s = open(src).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n: sys.exit(f'desert.py: expected {n} got {c}: {a[:90]!r}')
    s = s.replace(a, b)

# ---------- the scene layer ----------
rep('<div id="meadow" aria-hidden="true">', '<div id="desert" aria-hidden="true"><canvas id="desertCv" width="952" height="536" role="img" aria-label="Pixel-art desert at sunset: saguaros, an ocotillo, a turning windmill, pink-lit mountains"></canvas><canvas class="pcEdge" aria-hidden="true"></canvas></div>\n<div id="meadow" aria-hidden="true">')

# ---------- Settings: the fourth scene ----------
rep('<button type="button" data-v="waterfall">The waterfall</button></div>', '<button type="button" data-v="waterfall">The waterfall</button><button type="button" data-v="desert">The desert</button></div>')
rep("return v==='camp'||v==='waterfall'?v:'meadow'}", "return v==='camp'||v==='waterfall'||v==='desert'?v:'meadow'}")
rep("if(body.dataset.scene==='waterfall')startWaterfall();", "if(body.dataset.scene==='waterfall')startWaterfall();if(body.dataset.scene==='desert')startDesert();")

# ---------- caption ----------
rep("function pcCaption(){if(document.body.dataset.scene==='waterfall'){",
    "const DESERT_CAP=['The desert, sunset','The last light on the peaks · the ocotillo moving in the warm air','WIND 4 KM/H · 24 °C · CLEAR'];\n"
    "function pcCaption(){if(document.body.dataset.scene==='desert'){const T=document.getElementById('s3capTitle');if(T){T.textContent=DESERT_CAP[0];document.getElementById('s3capSub').textContent=DESERT_CAP[1];document.getElementById('s3capData').textContent=DESERT_CAP[2]}return}\n"
    "  if(document.body.dataset.scene==='waterfall'){")
rep("let meadowOn=false;", """let desertOn=false;
function startDesert(){if(desertOn||!window.DesertScene)return;desertOn=true;
  window.__desert=DesertScene.start(document.getElementById('desertCv'),()=>document.body.dataset.scene==='desert'&&!document.hidden)}
let meadowOn=false;""")

# ---------- styles: the same as the meadow's ----------
rep('/* ---------- the meadow ---------- */', """/* ---------- the desert ---------- */
#desert{position:fixed;inset:0;z-index:0;display:none;overflow:hidden;background:#0f0c10}
#desert #desertCv{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;image-rendering:pixelated;image-rendering:crisp-edges}
#desert canvas.pcEdge{position:absolute;inset:0;width:100%;height:100%;pointer-events:none;z-index:2;display:none}
body[data-scene="desert"] #desert{display:block}
body[data-scene="desert"] #stage,body[data-scene="desert"] .vignette{display:none}
body[data-scene="desert"][data-frame="postcard"] #desert{inset:auto;left:var(--pc-left,50%);top:var(--pc-top,84px);width:var(--pc-w,952px);height:var(--pc-h,536px);background:transparent}
body[data-scene="desert"][data-frame="postcard"] #desert canvas.pcEdge{display:block}
body[data-scene="desert"][data-frame="postcard"] .s3cap{top:var(--pccap-top,80%)}
body[data-scene="desert"] #place{display:none}
body[data-scene="desert"] .sgroup:has(#custBtn),body[data-scene="desert"] p.sl:has(+#setWhere),body[data-scene="desert"] #setWhere,body[data-scene="desert"] #setWhere+.note{display:none}
@media (min-width:700px) and (min-height:560px){
body[data-scene="desert"][data-frame="postcard"] .fire{inset:auto;left:var(--pc-left,50%);top:var(--pc-top,84px);width:var(--pc-w,952px);height:var(--pc-h,536px)}
body[data-scene="desert"][data-frame="postcard"] .fire canvas.pcEdge{display:block}}
/* ---------- the meadow ---------- */""")

# ---------- the scene module, beside the meadow's ----------
mod = open(HERE + 'desert.js').read()
rep('<script>\n/* The meadow', '<script>\n' + mod + '\n</script>\n<script>\n/* The meadow')

open(dst, 'w').write(s)
print('waterfall ok', len(s))
