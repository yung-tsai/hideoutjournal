"""python shot.py <page> t1,t2,... tag : canvas screenshots of a test page at those times (seconds), into shots/"""
import sys,threading,http.server,functools,base64
from playwright.sync_api import sync_playwright
page,times,tag=sys.argv[1],[float(x) for x in sys.argv[2].split(',')],sys.argv[3]
srv=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(http.server.SimpleHTTPRequestHandler,directory='.'));srv.RequestHandlerClass.log_message=lambda *a:None
threading.Thread(target=srv.serve_forever,daemon=True).start()
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page(viewport={'width':1000,'height':640});errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)[:300]))
    pg.goto(f'http://127.0.0.1:{srv.server_address[1]}/{page}');pg.wait_for_timeout(14000)
    for i,t in enumerate(times):
        pg.evaluate(f'window.__t({t})');pg.wait_for_timeout(600)
        d=pg.evaluate("document.getElementById('v').toDataURL('image/png')");open(f'shots/{tag}_{i}.png','wb').write(base64.b64decode(d.split(',')[1]))
    print('errors',errs);b.close()
