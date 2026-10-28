"""Real ambience: a river loop always, birds by day. Each loops by crossfading two copies, so it never seams.
   python3 sound.py <in.html> <out.html>"""
import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__)) + '/'   # src/
A = HERE + '../assets/'   # art, sound and scene data
import sys, base64
src, dst = sys.argv[1], sys.argv[2]
s = open(src).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n: sys.exit(f'sound.py: expected {n} got {c}: {a[:80]!r}')
    s = s.replace(a, b)
D = A+'snd/'
enc = lambda f: base64.b64encode(open(D + f, 'rb').read()).decode()

rep("const Sound=(()=>{let ctx=null,master,muff,water,wind,rain,windF,on=false;",
    "const SND={water:'" + enc('water_loop.mp3') + "',birds:'" + enc('birds_loop.mp3') + "'};\n"
    "const Sound=(()=>{let ctx=null,master,muff,water,wind,rain,windF,on=false,river=null,birds=null;")
# the loop player
rep("  function set(g,v,tc=.8){g&&g.gain.setTargetAtTime(v,ctx.currentTime,tc)}",
r"""  function set(g,v,tc=.8){g&&g.gain.setTargetAtTime(v,ctx.currentTime,tc)}
  function decode(b64){const bin=atob(b64),u=new Uint8Array(bin.length);for(let i=0;i<bin.length;i++)u[i]=bin.charCodeAt(i);
    return new Promise((res,rej)=>{try{const p=ctx.decodeAudioData(u.buffer,res,rej);if(p&&p.then)p.then(res,rej)}catch(e){rej(e)}})}
  const XF=4,CIN=new Float32Array(64).map((_,i)=>Math.sin(i/63*Math.PI/2)),COUT=new Float32Array(64).map((_,i)=>Math.cos(i/63*Math.PI/2));
  function looper(b64,level,rate=1){   // two copies overlap with an equal-power crossfade, so the loop has no seam
    const out=gain(level);out.connect(muff);let buf=null,next=0,timer=0;
    function voice(t){const s=ctx.createBufferSource(),g=gain(0),src=buf.duration-.5,L=src/rate;s.buffer=buf;s.playbackRate.value=rate;s.connect(g);g.connect(out);
      g.gain.setValueCurveAtTime(CIN,t,XF);g.gain.setValueCurveAtTime(COUT,t+L-XF,XF);s.start(t,.25,src);s.stop(t+L+.05);return t+L-XF}
    function pump(){if(!buf)return;while(next<ctx.currentTime+12)next=voice(Math.max(next,ctx.currentTime+.05))}
    decode(b64).then(b=>{buf=b;next=ctx.currentTime+.05;pump();timer=setInterval(pump,4000)},()=>{});
    return out}""")
# create the loops with the rest of the sound, and quiet the old synthesized water
rep("    rain=gain(0);chain(noise('white'),filt('highpass',1400),filt('lowpass',7000),rain,muff)}",
    "    rain=gain(0);chain(noise('white'),filt('highpass',1400),filt('lowpass',7000),rain,muff);\n"
    "    river=looper(SND.water,0,.82);   // slowed a little: a calmer, bigger river\n"
    "    birds=looper(SND.birds,0)}")
rep("    set(water,inside?.02:.05);",
    "    set(water,0);const BIRDS={morning:.85,midday:.6,golden:.45,night:0}[ST.time]??.5;   // birds by day, quiet at night\n"
    "    const S=state.settings,lv=k=>Math.max(0,Math.min(100,S[k]??100))/100;\n"
    "    set(master,lv('volume'),.3);set(river,(inside?.35:.8)*lv('volWater'),.6);set(birds,(inside?.35:1)*BIRDS*.68*(ST.weather==='rain'?.3:1)*lv('volBirds'),.8);")
# ---------- levels ----------
rep("if(v){init();if(!ctx)return;ctx.resume&&ctx.resume();set(master,1,.4);update()}",
    "if(v){init();if(!ctx)return;ctx.resume&&ctx.resume();set(master,Math.max(0,Math.min(100,state.settings.volume??80))/100,.4);update()}")
rep("settings:{reflectionStyle:'curious',defaultInput:'write',sound:false,reducedMotion:osReduced},",
    "settings:{reflectionStyle:'curious',defaultInput:'write',sound:false,reducedMotion:osReduced,volume:80,volWater:100,volBirds:100},")
rep('<div class="toggle-row"><div><b>Sound</b><span>River and wind, made live in your browser.</span></div>',
    '<div class="toggle-row"><div><b>Sound</b><span>The river, birds by day, and the weather.</span></div>')
import re
m = re.search(r'<div class="toggle-row"><div><b>Sound</b>.*?</button></div>', s, re.S)
if not m: sys.exit('sound row not found')
SL = lambda i, l: '<label class="vol"><span>' + l + '</span><input type="range" id="' + i + '" min="0" max="100" step="1"><output for="' + i + '"></output></label>'
s = s[:m.end()] + '<div class="vols" id="vols">' + SL('volMaster','Volume') + SL('volWater','Water') + SL('volBirds','Birds') + '</div>' + s[m.end():]
rep('</style>', '''
.vols{display:flex;flex-direction:column;gap:10px;margin:2px 0 14px;padding:12px 14px;border-radius:12px;background:var(--paper-2)}
.vols[data-off="true"]{opacity:.5}
.vol{display:grid;grid-template-columns:62px 1fr 38px;align-items:center;gap:10px;font-size:13.5px;color:var(--ink-2)}
.vol output{font-variant-numeric:tabular-nums;text-align:right;color:var(--ink-3);font-size:12.5px}
.vol input{width:100%;accent-color:var(--olive);height:24px;cursor:pointer}
</style>''')
rep("function renderSettings(){", "function renderSettings(){renderVols();")

# ---------- the speaker button opens a volume slider instead of just toggling ----------
rep('<button class="icon" id="soundBtn"', '<div class="sndwrap"><button class="icon" id="soundBtn"')
m2 = re.search(r'<div class="sndwrap"><button class="icon" id="soundBtn".*?</button>', s, re.S)
if not m2: sys.exit('sound button not found')
s = s[:m2.end()] + ('<div class="sndpop" id="sndPop" hidden>'
  '<button class="sndmute" type="button" id="sndMute" aria-pressed="false">Sound off</button>'
  '<input type="range" id="volQuick" min="0" max="100" step="1" aria-label="Volume" orient="vertical">'
  '<output for="volQuick" id="volQuickOut"></output></div></div>') + s[m2.end():]
rep('</style>', '''
.sndwrap{position:relative}
.sndpop{position:absolute;top:calc(100% + 8px);right:0;z-index:30;width:max-content;display:flex;flex-direction:column;align-items:center;gap:8px;
  padding:14px 10px 10px;border-radius:16px;background:var(--glass-strong);border:1px solid var(--line-2);box-shadow:0 14px 40px rgba(0,0,0,.45);
  -webkit-backdrop-filter:blur(16px);backdrop-filter:blur(16px);animation:popIn .22s ease}
.sndpop[hidden]{display:none}
.sndpop input[type=range]{writing-mode:vertical-lr;direction:rtl;width:22px;height:118px;margin:0;accent-color:var(--olive);cursor:pointer}
.sndpop output{font:500 12px/1 var(--ui);color:var(--ink-3);font-variant-numeric:tabular-nums}
.sndmute{border:0;background:none;color:var(--ink-3);font:500 11.5px/1 var(--ui);cursor:pointer;padding:2px 6px;border-radius:999px;white-space:nowrap}
.sndmute:hover{background:var(--paper-2);color:var(--ink)}
.sndmute[aria-pressed="true"]{color:var(--olive)}
@keyframes popIn{from{opacity:0;transform:translateY(-6px)}to{opacity:1;transform:none}}
@media (prefers-reduced-motion:reduce){.sndpop{animation:none}}
@media (max-width:760px){.sndpop{right:calc(-6px - var(--sa-r,0px))}}
</style>''')
glue = r'''
/* ---------- sound levels: 0-100, saved with the other settings ---------- */
const VOLS=[['volMaster','volume',80],['volWater','volWater',100],['volBirds','volBirds',100]];
function renderVols(){for(const [id,k,d] of VOLS){const el=$('#'+id),v=state.settings[k]??d;el.value=v;el.nextElementSibling.textContent=v+'%'}
  $('#vols').dataset.off=String(!state.settings.sound)}
for(const [id,k,d] of VOLS){const el=$('#'+id);
  el.addEventListener('input',()=>{state.settings[k]=+el.value;el.nextElementSibling.textContent=el.value+'%';Sound.update()});
  el.addEventListener('change',()=>{persist();if(!state.settings.sound){state.settings.sound=true;persist();applySound();renderVols()}})}
'''
rep("window.__talio&&(window.__talio.fire=()=>Burn);", "window.__talio&&(window.__talio.fire=()=>Burn);\n" + glue)

# the chime on switching sound on is one sound too many
rep("function toggleSound(){state.settings.sound=!state.settings.sound;persist();applySound();if(state.settings.sound)setTimeout(()=>Sound.chime(true),80)}",
    "function toggleSound(){state.settings.sound=!state.settings.sound;persist();applySound();renderVols();syncQuick()}")
# the synthesized wind only belongs to weather, not to a clear day
rep("set(wind,ST.weather==='windy'?.05:ST.weather==='rain'?.022:.01);",
    "set(wind,(ST.weather==='windy'?.05:ST.weather==='rain'?.022:0)*lv('volume'));")
# the quick slider in the top-right popover
rep("window.__talio&&(window.__talio.fire=()=>Burn);", "window.__talio&&(window.__talio.fire=()=>Burn);\n" + r'''
/* ---------- the speaker button: tap for a volume slider, not a blunt toggle ---------- */
const sndPop=$('#sndPop'),volQuick=$('#volQuick'),sndMute=$('#sndMute');
function syncQuick(){const on=!!state.settings.sound,v=state.settings.volume??80;
  volQuick.value=on?v:0;$('#volQuickOut').textContent=(on?v:0)+'%';
  sndMute.textContent=on?'Sound off':'Sound on';sndMute.setAttribute('aria-pressed',String(!on));
  $('#soundBtn').setAttribute('aria-pressed',String(on))}
function openSnd(o){sndPop.hidden=!o;$('#soundBtn').setAttribute('aria-expanded',String(!!o));if(o){syncQuick();setTimeout(()=>{try{volQuick.focus()}catch(_){}},0)}}
$('#soundBtn').setAttribute('aria-haspopup','true');$('#soundBtn').setAttribute('aria-expanded','false');
$('#soundBtn').addEventListener('click',e=>{e.stopPropagation();openSnd(sndPop.hidden)});
document.addEventListener('pointerdown',e=>{if(!sndPop.hidden&&!e.target.closest('.sndwrap'))openSnd(false)},true);
addEventListener('keydown',e=>{if(e.key==='Escape'&&!sndPop.hidden){e.stopPropagation();openSnd(false);$('#soundBtn').focus()}},true);
volQuick.addEventListener('input',()=>{const v=+volQuick.value;$('#volQuickOut').textContent=v+'%';
  if(v>0){state.settings.volume=v;if(!state.settings.sound){state.settings.sound=true;applySound()}}else if(state.settings.sound){state.settings.sound=false;applySound()}
  Sound.update();renderVols();syncQuick();$('#volQuickOut').textContent=v+'%';volQuick.value=v});
volQuick.addEventListener('change',()=>persist());
sndMute.addEventListener('click',()=>{toggleSound()});
''')

open(dst, 'w').write(s)
print('sound ok', len(s))
