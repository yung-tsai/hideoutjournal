"""The meadow: a pixel-art golden-hour meadow becomes Hideout's default scene; the river camp is the second choice, the stream the third.
   - Settings > Scene: The meadow / River camp / The stream. body[data-scene] is meadow|camp|stream.
   - The meadow is shown like the camp: a 16:9 postcard on the light page (postcard.py's layout, deckled edge, caption),
     or full screen with the Postcard switch off. The burn scene opens in the card on wider screens, as with the camp.
   - The scene itself is src/meadow.js (made by tools/meadow/build_page.py). It starts the first time the meadow shows
     and only draws while it's showing; the camp sleeps while the meadow shows, as it does for the stream.
   - Writing in the van and the van's looks belong to the camp, so they hide here too.
   python3 meadow.py <in.html> <out.html>"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)) + '/'
src, dst = sys.argv[1], sys.argv[2]
s = open(src).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n: sys.exit(f'meadow.py: expected {n} got {c}: {a[:90]!r}')
    s = s.replace(a, b)

# ---------- the scene layer ----------
rep('<div id="stage">', '<div id="meadow" aria-hidden="true"><canvas id="meadowCv" width="952" height="536" role="img" aria-label="Pixel-art meadow at golden hour: snowy mountains, a waterfall, a pine in front, grass swaying"></canvas><canvas class="pcEdge" aria-hidden="true"></canvas></div>\n<div id="stage">')

# ---------- Settings: three scenes, the meadow first and the default ----------
rep('<button type="button" data-v="stream">The stream</button><button type="button" data-v="camp">River camp</button></div>',
    '<button type="button" data-v="meadow">The meadow</button><button type="button" data-v="camp">River camp</button><button type="button" data-v="stream">The stream</button></div>')
rep("function sceneOn(){return (state.settings.scene||'camp')==='stream'}",
    "function sceneName(){const v=state.settings.scene;return v==='camp'||v==='stream'?v:'meadow'}\nfunction sceneOn(){return sceneName()==='stream'}")
rep("const v=state.settings.scene||'camp';", "const v=sceneName();")
rep("body.dataset.scene=on?'stream':'camp';", "body.dataset.scene=sceneName();if(body.dataset.scene==='meadow')startMeadow();")

# ---------- the camp sleeps while the meadow shows; the van is the camp's ----------
rep("(body.dataset.scene==='stream'&&!tr&&mode==='out')", "(body.dataset.scene!=='camp'&&!tr&&mode==='out')")
rep("const inVan=state.settings.writeWhere==='van'&&document.body.dataset.scene!=='stream';", "const inVan=state.settings.writeWhere==='van'&&document.body.dataset.scene==='camp';")

# ---------- the postcard layout and caption are shared with the camp ----------
if "const c=PRESETS[k].cap,T=$('#s3capTitle');if(T){" in s: rep("const c=PRESETS[k].cap,T=$('#s3capTitle');if(T){", "const c=PRESETS[k].cap,T=$('#s3capTitle');if(T&&document.body.dataset.scene==='stream'){")   # the stream writes its caption only while it shows
rep("function pcOn(){return document.body.dataset.scene==='camp'&&document.body.dataset.frame==='postcard'}",
    "function pcOn(){return document.body.dataset.scene!=='stream'&&document.body.dataset.frame==='postcard'}")
rep("function pcCaption(){if(document.body.dataset.scene!=='camp')return;",
    "const MEADOW_CAP=['The meadow, golden hour','The last light on the peaks · the grass moving in the wind','WIND 6 KM/H W · 16 °C · CLOUD 25%'];\n"
    "function pcCaption(){if(document.body.dataset.scene==='meadow'){const T=document.getElementById('s3capTitle');if(T){T.textContent=MEADOW_CAP[0];document.getElementById('s3capSub').textContent=MEADOW_CAP[1];document.getElementById('s3capData').textContent=MEADOW_CAP[2]}return}\n"
    "  if(document.body.dataset.scene!=='camp')return;")
rep("function resolveWorld(){", """let meadowOn=false;
function startMeadow(){if(meadowOn||!window.MeadowScene)return;meadowOn=true;
  window.__meadow=MeadowScene.start(document.getElementById('meadowCv'),()=>document.body.dataset.scene==='meadow'&&!document.hidden)}
function resolveWorld(){""")

# ---------- styles ----------
rep('</style>', """
/* ---------- the meadow ---------- */
#meadow{position:fixed;inset:0;z-index:0;display:none;overflow:hidden;background:#0f0c10}
#meadow #meadowCv{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;image-rendering:pixelated;image-rendering:crisp-edges}
#meadow canvas.pcEdge{position:absolute;inset:0;width:100%;height:100%;pointer-events:none;z-index:2;display:none}
body[data-scene="meadow"] #meadow{display:block}
body[data-scene="meadow"] #stage,body[data-scene="meadow"] .vignette{display:none}
body[data-scene="meadow"][data-frame="postcard"] #meadow{inset:auto;left:var(--pc-left,50%);top:var(--pc-top,84px);width:var(--pc-w,952px);height:var(--pc-h,536px);background:transparent}
body[data-scene="meadow"][data-frame="postcard"] #meadow canvas.pcEdge{display:block}
body[data-scene="meadow"][data-frame="postcard"] .s3cap{top:var(--pccap-top,80%)}
body[data-scene="meadow"] #place{display:none}
body[data-scene="meadow"] .sgroup:has(#custBtn),body[data-scene="meadow"] p.sl:has(+#setWhere),body[data-scene="meadow"] #setWhere,body[data-scene="meadow"] #setWhere+.note{display:none}
@media (min-width:700px) and (min-height:560px){
body[data-scene="meadow"][data-frame="postcard"] .fire{inset:auto;left:var(--pc-left,50%);top:var(--pc-top,84px);width:var(--pc-w,952px);height:var(--pc-h,536px)}
body[data-scene="meadow"][data-frame="postcard"] .fire canvas.pcEdge{display:block}}
</style>""")

# ---------- the scene module, before the app script so the app can start it ----------
mod = open(HERE + 'meadow.js').read()
rep('<script>\n(()=>{', '<script>\n' + mod + '\n</script>\n<script>\n(()=>{')

open(dst, 'w').write(s)
print('meadow ok', len(s))
