"""Live voice that keeps going: browsers end a speech session after about a minute (Chrome) or a long
   run of words. When that happens, start a fresh session a moment later, retry if the browser refuses,
   and if it still won't restart, say so ("Paused. Tap to keep listening") instead of pretending to listen.
   Finished phrases get a capital and a full stop, since browser voice adds almost no punctuation.
   python3 voice.py <in.html> <out.html>"""
import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__)) + '/'   # src/
A = HERE + '../assets/'   # art, sound and scene data
import sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n: sys.exit(f'voice.py: expected {n} got {c}: {a[:90]!r}')
    s = s.replace(a, b)

i = s.index("const LiveTranscriber={available:!!SR,"); j = s.index("function micPolicyBlocked(){", i)
s = s[:i] + r"""const LiveTranscriber={available:!!SR,
  start({onLevel,onText,onError,onStall,onPause,onResume}){
    let finals='',interim='',stopped=false,done=null,level=0,raf=0,lastHeard=0,heard=false,rec=null,active=false,endedAt=0,tries=0,paused=false;
    const t0=performance.now(),FATAL=['not-allowed','service-not-allowed','audio-capture','language-not-supported'];
    // a finished phrase: capital first letter, "I" on its own, and a full stop if it has no ending
    // join a finished phrase on: "I" on its own, a capital after a sentence ends, and a full stop after a real phrase (five words or more)
    const join=(prev,x)=>{x=(x||'').trim();if(!x)return prev;x=x.replace(/\bi\b/g,'I');const p=prev.trim();
      if(!p||/[.!?…]$/.test(p))x=x.charAt(0).toUpperCase()+x.slice(1);if(x.split(/\s+/).length>=5&&!/[.!?…,]$/.test(x))x+='.';return p+(p?' ':'')+x};
    const all=()=>(finals+' '+interim).replace(/\s+/g,' ').trim();
    const keepInterim=()=>{if(interim.trim()){finals=join(finals,interim);interim='';onText&&onText(all())}};
    const make=()=>{const r=new SR();r.continuous=true;r.interimResults=true;r.lang=navigator.language||'en-US';
      r.onstart=()=>{if(r!==rec)return;active=true;tries=0;if(paused){paused=false;onResume&&onResume()}};
      r.onresult=e=>{if(r!==rec)return;interim='';for(let k=e.resultIndex;k<e.results.length;k++){const x=e.results[k];if(x.isFinal)finals=join(finals,x[0].transcript);else interim+=x[0].transcript}
        lastHeard=performance.now();heard=true;onText&&onText(all())};
      r.onerror=e=>{if(r!==rec)return;if(!FATAL.includes(e.error))return;   // no-speech, aborted, network: the session ends and we start another
        stopped=true;clearInterval(dog);cancelAnimationFrame(raf);onLevel&&onLevel(0,0);onError&&onError(e.error)};
      r.onend=()=>{if(r!==rec)return;active=false;endedAt=performance.now();
        if(stopped){keepInterim();if(done)done(all());return}restart(180)};
      return r};
    const pause=()=>{if(paused||stopped)return;paused=true;keepInterim();onPause&&onPause()};
    const restart=delay=>{if(stopped||paused)return;setTimeout(()=>{if(stopped||active||paused)return;keepInterim();tries++;
      rec=make();try{rec.start()}catch(_){if(tries<4)restart(350*tries);else pause()}},delay)};
    // a watchdog: sometimes a session just stops without telling anyone
    const dog=setInterval(()=>{if(stopped){clearInterval(dog);return}
      if(!active&&!paused&&endedAt&&performance.now()-endedAt>2500){if(tries<4)restart(0);else pause()}},1500);
    let heardT=setTimeout(()=>{if(!heard&&!stopped)onStall&&onStall()},7000);
    const step=now=>{const target=!paused&&(now-lastHeard)<650?.45+.55*Math.abs(Math.sin(now/110)):.05;level+=(target-level)*.2;onLevel&&onLevel(level,(now-t0)/1000);raf=requestAnimationFrame(step)};raf=requestAnimationFrame(step);
    rec=make();try{rec.start()}catch(e){setTimeout(()=>{stopped=true;clearInterval(dog);cancelAnimationFrame(raf);onError&&onError('start-failed')},0)}
    return{
      stop(){stopped=true;clearTimeout(heardT);clearInterval(dog);cancelAnimationFrame(raf);onLevel&&onLevel(0,0);
        return new Promise(res=>{done=res;if(!active){keepInterim();res(all());return}try{rec.stop()}catch(_){keepInterim();res(all())}setTimeout(()=>{keepInterim();res(all())},1500)})},
      cancel(){stopped=true;clearTimeout(heardT);clearInterval(dog);cancelAnimationFrame(raf);onLevel&&onLevel(0,0);try{rec.abort()}catch(_){}},
      // called from a tap, which browsers always allow to start the microphone
      resume(){if(stopped)return;tries=0;rec=make();try{rec.start()}catch(e){onError&&onError('start-failed')}}}}};
""" + s[j:]

# the Talk screen: show the pause honestly, and a tap anywhere on the listening row picks it back up
rep("      onStall:()=>voiceMsg('Not hearing anything yet. If no words appear as you speak, live voice may be blocked here.',true),",
    "      onStall:()=>voiceMsg('Not hearing anything yet. If no words appear as you speak, live voice may be blocked here.',true),\n"
    "      onPause:()=>{const l=$('.listen');l.dataset.paused='true';$('#jListening').textContent='Paused. Tap to keep listening.'},\n"
    "      onResume:()=>{const l=$('.listen');delete l.dataset.paused;$('#jListening').textContent=session&&session.continued?'Still listening…':'Listening…'},")
rep("function stopListening(){",
    "$('.listen').addEventListener('click',()=>{const l=$('.listen');if(l.dataset.paused==='true'&&listenSess&&listenSess.resume)listenSess.resume()});\n"
    "function stopListening(){")
rep("</style>", """
.listen[data-paused="true"]{cursor:pointer}
.listen[data-paused="true"] #jListening{color:var(--ink);text-decoration:underline;text-underline-offset:3px}
</style>""")
open(dst, 'w').write(s)
print('voice ok', len(s))
