import json,base64,io,colorsys,sys
import numpy as np
from PIL import Image,ImageDraw
X0,Y0,X1,Y1=704,248,834,312
def base(k):
    d=json.load(open(f'newscene/{k}_set.json'))
    return Image.open(io.BytesIO(base64.b64decode(d['base'].split(',')[1]))).convert('RGB')
def hls(a):
    f=np.vectorize(lambda r,g,b:colorsys.rgb_to_hls(r,g,b),otypes=[float,float,float])
    return f(a[...,0],a[...,1],a[...,2])
# ---------- the van's body, drawn by hand (native pixels; all four scenes share it) ----------
def body_mask(day):
    W,H=X1-X0,Y1-Y0
    m=Image.new('L',(W,H),0);d=ImageDraw.Draw(m)
    poly=[(731,255),(815,255),(820,258),(823,262),(826,280),(827,300),(712,300),(711,290),(712,280),(714,276),(720,267),(726,259)]
    d.polygon([(x-X0,y-Y0) for x,y in poly],fill=255)
    for cx in (736,797):d.ellipse([cx-8.6-X0,301-8.6-Y0,cx+8.6-X0,301+8.6-Y0],fill=0)   # tyres (arch lip stays body)
    d.rectangle([711-X0,296-Y0,725-X0,300-Y0],fill=0);d.rectangle([816-X0,296-Y0,828-X0,300-Y0],fill=0)   # bumpers
    m=np.asarray(m)>0
    r=np.asarray(day).astype(float)[Y0:Y1,X0:X1]/255
    H_,L_,S_=hls(r);H_=H_*360
    yy=np.arange(Y0,Y1)[:,None]+np.zeros((1,X1-X0))
    xx=np.arange(X0,X1)[None,:]+np.zeros((Y1-Y0,1))
    glass=(yy>=260)&(yy<=279)&(xx>=714)&(xx<=818)&(L_<.46)            # glass and rubber; only the light pillars are body here
    lamp=(S_>.18)&((H_<180)|(H_>245))                                 # head and tail lights, grass bounce
    from scipy import ndimage
    near_edge=m&~ndimage.binary_erosion(m,iterations=2)
    sky=near_edge&(L_<.17)                                            # forest showing round the roofline
    tyre=(L_<.13)&(yy>=289)                                           # tyre rubber round the arches
    return m&~glass&~lamp&~sky&~tyre
# ---------- an Amiga-style ramp for a chosen colour: cool shadows, warm light ----------
def ramp(hexc,n=7,smax=.46):
    h,l,s=colorsys.rgb_to_hls(*[int(hexc[i:i+2],16)/255 for i in (1,3,5)])
    s=min(s,smax);l=min(max(l,.24),.80);out=[]
    for i in range(n):
        t=i/(n-1)
        hh=(h*360+(1-t)*(-10 if h*360<215 else 8)*(1 if (h*360)%360>40 else 1)+t*6*(1 if h*360<60 or h*360>300 else 0))%360
        ll=np.clip(l-.30+t*.56,.05,.95)
        ss=s*(.70+.45*np.sin(t*np.pi))
        out.append(colorsys.hls_to_rgb(hh/360,ll,min(ss,.6)))
    return np.array(out)
def recolour(img,mask,hexc,cast=None,lum_ref=None):
    r=np.asarray(img).astype(float)[Y0:Y1,X0:X1]/255
    Y=r@[.299,.587,.114]
    ref=lum_ref if lum_ref is not None else Y
    lo,hi=np.percentile(ref[mask],3),np.percentile(ref[mask],97)
    t=np.clip((Y-lo)/(hi-lo),0,1)
    R=ramp(hexc);idx=np.rint(t*(len(R)-1)).astype(int)
    out=r.copy();new=R[idx]
    if cast is not None:new=np.clip(new*cast,0,1)
    out[mask]=new[mask]
    full=np.asarray(img).copy();full[Y0:Y1,X0:X1]=(out*255).astype(np.uint8)
    return Image.fromarray(full)

# ---------- other times of day: carry the painting's own light across, pixel by pixel ----------
def relight(day,scene,mask,hexc,blur=1.4,desat=0.0):
    from scipy import ndimage
    d=np.asarray(day).astype(float)[Y0:Y1,X0:X1]/255
    sc=np.asarray(scene).astype(float)[Y0:Y1,X0:X1]/255
    def soft(a):
        out=np.empty_like(a);w=mask.astype(float)
        ww=ndimage.gaussian_filter(w,blur)+1e-6
        for c in range(3):out[...,c]=ndimage.gaussian_filter(a[...,c]*w,blur)/ww
        return out
    ratio=np.clip(soft(sc)/(soft(d)+1e-3),0.05,2.2)            # the light that falls on the van in this scene
    dayrec=np.asarray(recolour(day,mask,hexc)).astype(float)[Y0:Y1,X0:X1]/255
    new=np.clip(dayrec*ratio,0,1)
    if desat:
        g=(new@[.299,.587,.114])[...,None];new=new*(1-desat)+g*desat
    out=sc.copy();out[mask]=new[mask]
    full=np.asarray(scene).copy();full[Y0:Y1,X0:X1]=(out*255).astype(np.uint8)
    return Image.fromarray(full)

def twotone(day,mask,lower,split=281,upper='#e8e4d8'):
    yy=np.arange(Y0,Y1)[:,None]+np.zeros((1,X1-X0))
    lo=mask&(yy>=split);up=mask&(yy<split)
    im=recolour(day,lo,lower,lum_ref=None)
    if upper:im=recolour(im,up,upper)
    return im
def relight_img(day,scene,mask,dayrec,blur=1.4,desat=0.0):
    from scipy import ndimage
    d=np.asarray(day).astype(float)[Y0:Y1,X0:X1]/255
    sc=np.asarray(scene).astype(float)[Y0:Y1,X0:X1]/255
    w=mask.astype(float);ww=ndimage.gaussian_filter(w,blur)+1e-6
    soft=lambda a:np.stack([ndimage.gaussian_filter(a[...,c]*w,blur)/ww for c in range(3)],-1)
    ratio=np.clip(soft(sc)/(soft(d)+1e-3),0.05,2.2)
    dr=np.asarray(dayrec).astype(float)[Y0:Y1,X0:X1]/255
    new=np.clip(dr*ratio,0,1)
    if desat:g=(new@[.299,.587,.114])[...,None];new=new*(1-desat)+g*desat
    out=sc.copy();out[mask]=new[mask]
    full=np.asarray(scene).copy();full[Y0:Y1,X0:X1]=(out*255).astype(np.uint8)
    return Image.fromarray(full)
