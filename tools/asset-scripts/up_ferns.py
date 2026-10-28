import json,io,base64
import numpy as np
from PIL import Image
from scipy import ndimage
def load(k):
    d=json.load(open(f'newscene/{k}_set.json'))
    dec=lambda u:Image.open(io.BytesIO(base64.b64decode(u.split(',')[1])))
    return d,np.asarray(dec(d['base']).convert('RGB')).astype(int),np.asarray(dec(d['water']).convert('RGBA'))[...,3]>0
_,day,water=load('day')
H,W=day.shape[:2];yy,xx=np.mgrid[0:H,0:W]
r,g,b=day[...,0],day[...,1],day[...,2];lum=day@[.299,.587,.114]
green=(g>r+8)&(g>=b-6)&(r<115)&~((r>95)&(g>120))
# [x0,y0,x1,y1, base row, sway px, what moves]
GROUPS=[[0,395,172,536,536,1.6,'green'],
        [172,406,262,480,480,2.2,'dark'],
        [333,470,372,528,528,2.0,'dark'],
        [372,480,424,532,532,2.0,'dark'],
        [478,485,514,522,522,1.6,'dark'],
        [772,385,952,505,505,1.6,'green']]
m=np.zeros((H,W),bool)
for x0,y0,x1,y1,base,A,kind in GROUPS:
    box=(xx>=x0)&(xx<x1)&(yy>=y0)&(yy<=y1)
    if kind=='green':pick=green
    else:
        pick=((lum<78)|green)&~water          # anything dark against the water; rock near the base never moves (see the sway curve)
    m|=box&pick
lab,n=ndimage.label(m,structure=np.ones((3,3)));sz=ndimage.sum(m,lab,range(1,n+1));keep=np.zeros(n+1,bool);keep[1:]=sz>=12;m=keep[lab]
def fill(img,mask):
    out=img.astype(float).copy();todo=mask.copy()
    for _ in range(40):                                   # grow the surroundings inward, a ring at a time
        if not todo.any():break
        known=~todo;acc=np.zeros_like(out);cnt=np.zeros((H,W))
        for dy,dx in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,-1),(1,-1),(-1,1)):
            sh=np.roll(np.roll(known,dy,0),dx,1);v=np.roll(np.roll(out,dy,0),dx,1)
            acc+=v*sh[...,None];cnt+=sh
        ring=todo&(cnt>0);out[ring]=acc[ring]/cnt[ring][:,None];todo&=~ring
    return out.astype(np.uint8)
uri=lambda a:'data:image/png;base64,'+base64.b64encode((lambda b:(Image.fromarray(a).save(b,'PNG',optimize=True),b.getvalue())[1])(io.BytesIO())).decode()
out={'groups':[[x0,y0,x1,y1,base,A] for x0,y0,x1,y1,base,A,_ in GROUPS],'sets':{}}
for k in ('sunrise','day','sunset','night'):
    _,base,_w=load(k)
    lay=np.zeros((H,W,4),np.uint8);lay[...,:3]=base*m[...,None];lay[...,3]=m*255   # nothing stored under the clear pixels
    out['sets'][k]={'base':uri(fill(base,m)),'ferns':uri(lay)}
json.dump(out,open('up/ferns.json','w'))
ov=day.copy().astype(float);ov[m]=ov[m]*.3+np.array([255,40,200])*.7
Image.fromarray(ov.astype(np.uint8)).crop((0,380,952,536)).resize((1904,312),Image.NEAREST).save('sq/fern_mask2.png')
print('fern px',int(m.sum()))
