import os,base64,json,io
from PIL import Image
from playwright.sync_api import sync_playwright
S={"width":952,"denoise":0,"bright":6,"contrast":-4,"sat":7,"hue":0,"temp":-3,"match":100,"shadows":-16,"colors":80,"dstr":42,"dsim":50,"sky":25,"scan":0,"glow":50,"vig":100,"dither":"bayer4","amiga":False}
src=open('wrapT.html').read();i=src.index('const IMGS=');j=src.index(';\nconst $',i)
imgs=json.loads(src[i+len('const IMGS='):j])
def uri(path):
    b=io.BytesIO();Image.open(path).convert('RGB').save(b,'JPEG',quality=93);return 'data:image/jpeg;base64,'+base64.b64encode(b.getvalue()).decode()
# the original framed sunset first, as a control: it should reproduce the app's base exactly
jobs=[('orig',None),('edit1','up/edit1_raw.png'),('edit3','up/edit3_raw.png')]
with sync_playwright() as p:
    b=p.chromium.launch()
    for name,f in jobs:
        im=dict(imgs)
        if f:im['framed']=uri(f)
        open('up/wrapE.html','w').write(src[:i]+'const IMGS='+json.dumps(im)+src[j:])
        pg=b.new_page(viewport={'width':1440,'height':900});pg.goto('file://'+os.path.abspath('up/wrapE.html'))
        pg.evaluate("s=>localStorage.setItem('pixel-tuner',JSON.stringify(s))",S);pg.reload()
        pg.wait_for_function("document.querySelector('#status').textContent.startsWith('952')",timeout=90000)
        d=pg.evaluate("document.querySelector('#out').toDataURL('image/png')")
        open(f'up/{name}_tuned.png','wb').write(base64.b64decode(d.split(',')[1]));pg.close();print(name,'ok')
    b.close()
