"""Turn the standalone stream prototype's scene script into a module the Hideout app can host."""
import re
S='/tmp/claude-0/-home-claude/b4eb5617-a3f5-5f2a-9e5d-a181bc4d3cf2/scratchpad/shore/'
s=open(S+'hideout-stream.html').read()
i=s.index('<script type="module">');j=s.index('</script>',i)
js=s[i+len('<script type="module">'):j]
def r(a,b,n=1):
    global js
    assert js.count(a)==n,(js.count(a),a[:90]); js=js.replace(a,b)
def cut(a,b,new):
    global js
    i=js.index(a); k=js.index(b,i); js=js[:i]+new+js[k:]
r("const stage=$('#stage');","const stage=$('#scene3d');")
r("const l=$('#loading');l.textContent='This scene needs more graphics power than this device has right now. Try reloading.';l.classList.remove('done')",
  "const l=$('#s3msg');l.textContent='This scene needs more graphics power than this device has right now. Try reloading.';l.hidden=false")
cut("function setTime(k){tKey=k;target=asState(PRESETS[k]);","/* ---------------- frame toggle",
"""function setTime(k){tKey=k;target=asState(PRESETS[k]);const c=PRESETS[k].cap,T=$('#s3capTitle');if(T){T.textContent=c[0];$('#s3capSub').textContent=c[1];$('#s3capData').textContent=c[2]}}

""")
cut("/* ---------------- frame toggle","/* ---------------- size ---------------- */",
"""/* ---------------- the app decides: which scene, and whether it is framed as a postcard ---------------- */
let framed=document.body.dataset.frame!=='full';
const audio=null;   // sound comes from the app (the river and birds)
new MutationObserver(()=>{const f=document.body.dataset.frame!=='full';if(f!==framed){framed=f;finish.uniforms.uFrame.value=framed?1:0}resize()}).observe(document.body,{attributes:true,attributeFilter:['data-frame','data-scene']});

""")
r("function resize(){const W=innerWidth,Hh=innerHeight,root=document.documentElement.style;let w,h;\n  if(framed){const portrait=W<Hh*.85;const a=portrait?4/5:4/3;const top=66,bottomRoom=170;",
  "function resize(){const W=innerWidth,Hh=innerHeight,root=document.documentElement.style;let w,h;\n  if(framed){const portrait=W<Hh*.85;const a=portrait?4/5:4/3;const top=PHONE?70:84,bottomRoom=PHONE?150:178;")
js=js.replace("'--st-top'","'--s3-top'").replace("'--st-w'","'--s3-w'").replace("'--st-h'","'--s3-h'").replace("'--cap-top'","'--s3cap-top'")
r("function loop(){const dt=Math.min(clock.getDelta(),.1);",
  "function loop(){if(document.body.dataset.scene!=='stream'||document.hidden){clock.getDelta();requestAnimationFrame(loop);return}   // only draw while the stream is showing\n  const dt=Math.min(clock.getDelta(),.1);")
r("document.body.dataset.frame='postcard';resize();applyState();\nrequestAnimationFrame(()=>{loop();setTimeout(()=>$('#loading').classList.add('done'),300)});\nwindow.__stream=",
  "finish.uniforms.uFrame.value=framed?1:0;resize();applyState();\nrequestAnimationFrame(loop);\nwindow.__scene3d=")
assert '#loading' not in js and "'.seg button'" not in js and '#bSound' not in js and '#field' not in js, 'leftover UI hooks'
open('/home/claude/pixel/stream3d.js','w').write("/* The stream: Hideout's 3D scene (three.js). Built from the standalone prototype by make_s3.py; the app owns all UI. */\n"+js)
print('module',len(js))
