"""The river camp as a postcard: the same light page as the stream, with the pixel art printed on it as a deckled card.
   - The card keeps the art's own 16:9 shape (952x536), centred between the header and the journal field.
   - Pixel-crisp: a whole number of device pixels per art pixel wherever that costs little room, otherwise the exact fit,
     always drawn nearest-neighbour (never blurred).
   - The camp fits itself to the card instead of the window, so the pan, the zoom into the van and the van's inside all
     happen within it. On wider screens the burn scene opens in the card too (on phones the card is too small for it, so it stays full screen). The deckled edge is painted by a small canvas over each.
   - A caption under the card follows the camp's time of day. With the Postcard switch off, the camp is full screen as before.
   - On the postcard page the header and the journal field stay put (the full-screen look still lets them rest away when idle).
   python3 postcard.py <in.html> <out.html>"""
import sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n: sys.exit(f'postcard.py: expected {n} got {c}: {a[:90]!r}')
    s = s.replace(a, b)

# ---------- an edge canvas inside the camp and inside the fire ----------
rep('<div id="stage">', '<div id="stage"><canvas class="pcEdge" aria-hidden="true"></canvas>')
rep('<div class="fire" id="fire" hidden><canvas id="fireCv"', '<div class="fire" id="fire" hidden><canvas class="pcEdge" aria-hidden="true"></canvas><canvas id="fireCv"')

# ---------- on the postcard page the interface is part of the page: it never rests away ----------
rep("function goIdle(force){if(!force&&busy())", "function goIdle(force){if(!force&&document.body.dataset.frame==='postcard')return;if(!force&&busy())")

# ---------- the camp fits the card, not the window ----------
rep("function size(){", r"""/* ---------- the camp as a postcard ---------- */
function pcOn(){return document.body.dataset.scene==='camp'&&document.body.dataset.frame==='postcard'}
function pcH12(x,y){let a=(x*.1031)%1,b=(y*.1031)%1,c=(x*.1031)%1;const d=a*(b+33.33)+b*(c+33.33)+c*(a+33.33);a+=d;b+=d;c+=d;return(((a+b)*c)%1+1)%1}
function pcVn(x,y){const ix=Math.floor(x),iy=Math.floor(y),fx=x-ix,fy=y-iy,ux=fx*fx*(3-2*fx),uy=fy*fy*(3-2*fy);
  const a=pcH12(ix,iy),b=pcH12(ix+1,iy),c=pcH12(ix,iy+1),d=pcH12(ix+1,iy+1);return a+(b-a)*ux+(c-a)*uy+(a-b-c+d)*ux*uy}
function pcEdges(w,h,dpr){   // the deckled edge, the same recipe as the stream's: page-coloured flecks thinning into the picture
  const f=Math.min(1,Math.max(.4,w/1000)),u=dpr*f,W=Math.round(w*dpr),H=Math.round(h*dpr),m=9*u,band=24*u,reach=Math.ceil(m+band*1.5+19*u);   // the edge scales with the card
  const col=getComputedStyle(document.body).backgroundColor.match(/\d+/g).map(Number);
  document.querySelectorAll('.pcEdge').forEach(cv=>{if(cv.width===W&&cv.height===H&&cv.dataset.col===String(col))return;cv.width=W;cv.height=H;cv.dataset.col=String(col);
    const g=cv.getContext('2d'),im=g.createImageData(W,H),D=im.data;
    for(let y=0;y<H;y++){const ty=Math.min(y,H-1-y);for(let x=0;x<W;x++){const t=Math.min(Math.min(x,W-1-x),ty);if(t>reach){x=W-1-reach-1;if(x<0)break;continue}
      const n=pcVn(x/(30*u),y/(30*u))*14*u+pcVn(x/(7*u),y/(7*u))*5*u,k=Math.min(1,Math.max(0,(t-n+band*.5-m)/band)),sm=k*k*(3-2*k);
      if(pcH12(Math.floor(x/(2*u)),Math.floor(y/(2*u)))>sm){const i=(y*W+x)*4;D[i]=col[0];D[i+1]=col[1];D[i+2]=col[2];D[i+3]=255}}}
    g.putImageData(im,0,0)})}
function pcLayout(){if(!pcOn())return;const R=document.documentElement.style,W=innerWidth,H=innerHeight,ph=Math.min(W,H)<700,top=ph?70:84,bottom=ph?150:178,dpr=devicePixelRatio||1;
  const AW=952,AH=536,fit=Math.min(Math.max(200,W-32)/AW,Math.max(120,H-top-bottom)/AH),n=Math.floor(fit*dpr);
  const k=n>=1&&n/dpr>=fit*.8?n/dpr:Math.floor(fit*AW*dpr)/(AW*dpr);   // whole device pixels per art pixel where it costs little room
  const w=Math.round(AW*k*dpr)/dpr,h=Math.round(AH*k*dpr)/dpr,left=Math.round((W-w)/2*dpr)/dpr;
  const y=Math.round((top+Math.max(0,(H-top-bottom-h-70)*.42))*dpr)/dpr;   // a short card sits a little above the middle of the free space, its caption under it
  R.setProperty('--pc-top',y+'px');R.setProperty('--pc-left',left+'px');R.setProperty('--pc-w',w+'px');R.setProperty('--pc-h',h+'px');R.setProperty('--pccap-top',(y+h+14)+'px');
  pcEdges(w,h,dpr)}
function size(){pcLayout();""")
rep("const W=innerWidth,H=innerHeight,s=Math.max(W/w,H/h)*P.z;", "const W=stageEl.clientWidth||innerWidth,H=stageEl.clientHeight||innerHeight,s=Math.max(W/w,H/h)*P.z;")
rep("const W=innerWidth,H=innerHeight,s0=Math.max(W/NW,H/NH),visW=W/s0", "const W=stageEl.clientWidth||innerWidth,H=stageEl.clientHeight||innerHeight,s0=Math.max(W/NW,H/NH),visW=W/s0")
rep("free=W-viewK.panel,freeH=H-viewK.bottom;", "free=W-(pcOn()?0:viewK.panel),freeH=H-(pcOn()?0:viewK.bottom);")
rep("sy:viewK.bottom?Math.max(90,freeH*.55):H/2", "sy:viewK.bottom&&!pcOn()?Math.max(90,freeH*.55):H/2")
rep("sx:innerWidth/2,sy:innerHeight/2,z:1}}", "sx:(stageEl.clientWidth||innerWidth)/2,sy:(stageEl.clientHeight||innerHeight)/2,z:1}}")
rep("place(cv,NW,NH,P.ext,pc.e,viewK.panel*.72,viewK.bottom);", "place(cv,NW,NH,P.ext,pc.e,pcOn()?0:viewK.panel*.72,pcOn()?0:viewK.bottom);")
rep("IN.port=innerHeight>innerWidth*1.05", "IN.port=!pcOn()&&innerHeight>innerWidth*1.05", 2)   # the card is always landscape
# the fire fits its layer, which is the card in postcard mode
rep("function sizeView(){const a=innerWidth/Math.max(1,innerHeight);",
    "function sizeView(){const a=(layer.clientWidth||innerWidth)/Math.max(1,layer.clientHeight||innerHeight);")

# ---------- the caption follows the camp's time of day; switching scenes re-lays the page ----------
rep("ST.weather='clear'}   // weather is paused for now", "ST.weather='clear';pcCaption()}   // weather is paused for now")
rep("function resolveWorld(){", r"""const PC_CAP={morning:['The river camp, morning','First light on the water · the van still cold','WIND 4 KM/H · 9 °C · CLEAR'],
  midday:['The river camp, midday','Sun high over the pines · the river running bright','WIND 8 KM/H · 19 °C · CLEAR'],
  golden:['The river camp, golden hour','The sun low behind the peaks · smoke from the fire','WIND 3 KM/H · 15 °C · CLEAR'],
  night:['The river camp, after dark','Stars over the ridge · the fire burning low','WIND 2 KM/H · 7 °C · CLEAR']};
function pcCaption(){if(document.body.dataset.scene!=='camp')return;const c=PC_CAP[ST.time]||PC_CAP.golden,T=document.getElementById('s3capTitle');if(!T)return;
  T.textContent=c[0];document.getElementById('s3capSub').textContent=c[1];document.getElementById('s3capData').textContent=c[2]}
function resolveWorld(){""")
rep("body.dataset.frame=state.settings.frame!==false?'postcard':'full';syncSceneUI()}",
    "body.dataset.frame=state.settings.frame!==false?'postcard':'full';syncSceneUI();if(body.dataset.frame==='postcard'&&body.dataset.idle)delete body.dataset.idle;\n"
    "  if(on){if(window.__scene3d)window.__scene3d.setTime('golden')}else{pcCaption();if(typeof size==='function')size()}}   // the caption and the card follow the scene")

# ---------- styles ----------
rep('</style>', """
/* ---------- the river camp as a postcard ---------- */
body[data-scene="camp"][data-frame="postcard"] #stage{inset:auto;left:var(--pc-left,50%);top:var(--pc-top,84px);width:var(--pc-w,952px);height:var(--pc-h,536px);background:var(--ground)}
body[data-scene="camp"][data-frame="postcard"] .vignette{display:none}
body[data-frame="postcard"] #place{display:none}
body[data-scene="camp"][data-frame="postcard"] .s3cap{top:var(--pccap-top,80%)}
@media (min-width:700px) and (min-height:560px){
body[data-scene="camp"][data-frame="postcard"] .fire{inset:auto;left:var(--pc-left,50%);top:var(--pc-top,84px);width:var(--pc-w,952px);height:var(--pc-h,536px)}
body[data-scene="camp"][data-frame="postcard"] .fire canvas.pcEdge{display:block}}
#stage canvas.pcEdge,.fire canvas.pcEdge{position:absolute;inset:0;left:0;top:0;width:100%;height:100%;pointer-events:none;z-index:6;display:none;image-rendering:auto}
body[data-scene="camp"][data-frame="postcard"] #stage canvas.pcEdge{display:block}
</style>""")

open(dst, 'w').write(s)
print('postcard ok', len(s))
