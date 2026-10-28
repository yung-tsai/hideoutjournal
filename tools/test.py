"""Drive the built index.html in a headless browser and take screenshots.
   pip install playwright && python3 -m playwright install chromium
   python3 tools/test.py desk|phone '<steps json>' tag
   steps: ["js","code"] ["wait",ms] ["waitfn","js condition"] ["click","css"] ["rclick","css"] (a real click)
          ["fill","css","text"] ["key","Enter"] ["hover","css"] ["shot","name"]  -> build/shots/<tag>_<size>_<name>.png
   e.g. python3 tools/test.py desk '[["wait",4000],["shot","home"]]' check"""
import sys, json, os, threading, http.server, functools
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
size = sys.argv[1]; steps = json.loads(sys.argv[2]); tag = sys.argv[3]
dims = {'desk': (1440, 900, 1), 'phone': (390, 844, 2)}[size]
os.makedirs(os.path.join(ROOT, 'build', 'shots'), exist_ok=True)
# serve over http: ES modules (the 3D scene) don't load from file://
srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT))
threading.Thread(target=srv.serve_forever, daemon=True).start()
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={'width': dims[0], 'height': dims[1]}, device_scale_factor=dims[2], has_touch=(size == 'phone'), is_mobile=(size == 'phone'))
    pg = ctx.new_page(); logs = []
    pg.on('console', lambda m: logs.append(m.type + ': ' + m.text[:300]) if m.type in ('error', 'warning') else None)
    pg.on('pageerror', lambda e: logs.append('ERR ' + str(e)[:500]))
    pg.goto(f'http://127.0.0.1:{srv.server_address[1]}/index.html')
    pg.wait_for_function('window.__talio && window.__talio.isReady()', timeout=90000)
    for st in steps:
        k = st[0]
        if k == 'js': print('js->', pg.evaluate(st[1]))
        elif k == 'wait': pg.wait_for_timeout(st[1])
        elif k == 'waitfn': pg.wait_for_function(st[1], timeout=90000)
        elif k == 'click': pg.evaluate('q=>document.querySelector(q).click()', st[1])
        elif k == 'rclick': pg.click(st[1])
        elif k == 'fill': pg.evaluate('([q,v])=>{const e=document.querySelector(q);e.value=v;e.dispatchEvent(new Event("input"))}', [st[1], st[2]])
        elif k == 'key': pg.keyboard.press(st[1])
        elif k == 'hover': pg.hover(st[1], force=True)
        elif k == 'shot':
            out = os.path.join(ROOT, 'build', 'shots', f'{tag}_{size}_{st[1]}.png')
            pg.screenshot(path=out, scale='css', timeout=120000); print('shot', out, logs[-4:]); logs.clear()
    if logs: print('console:', logs)
    b.close()
srv.shutdown()
