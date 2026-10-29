import threading,http.server,functools,base64
from playwright.sync_api import sync_playwright
srv=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(http.server.SimpleHTTPRequestHandler,directory='.'));srv.RequestHandlerClass.log_message=lambda *a:None
threading.Thread(target=srv.serve_forever,daemon=True).start()
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page(viewport={'width':1000,'height':680});errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)[:300]))
    pg.goto(f'http://127.0.0.1:{srv.server_address[1]}/index.html');pg.wait_for_timeout(15000)
    pg.evaluate('__t(40)');pg.wait_for_timeout(500);pg.click('#tw')
    for i,w in enumerate([1500,1500,1500]):
        pg.wait_for_timeout(w);d=pg.evaluate("document.getElementById('v').toDataURL('image/png')");open(f'shots/tw_{i}.png','wb').write(base64.b64decode(d.split(',')[1]))
    pg.screenshot(path='shots/tw_page.png');print('errors',errs);b.close()
