import sys,json,io,base64
sys.path.insert(0,'sq')
import numpy as np
from PIL import Image
from scipy import ndimage
from recolour import base,body_mask,X0,Y0,X1,Y1
meta=json.load(open('up/layers.json'))
B={k:np.asarray(base(k)).astype(float)/255 for k in ('sunrise','day','sunset','night')}
bm=np.zeros(B['day'].shape[:2],bool);bm[Y0:Y1,X0:X1]=body_mask(base('day'))
def field(T,blur=2.5):
    w=bm.astype(float);ww=ndimage.gaussian_filter(w,blur)+1e-6
    soft=lambda a:np.stack([ndimage.gaussian_filter(a[...,c]*w,blur)/ww for c in range(3)],-1)
    r=np.clip(soft(B[T])/(soft(B['sunset'])+1e-3),0.15,3.0)
    # carry the van's light outward to things sitting on or beside it
    _,(iy,ix)=ndimage.distance_transform_edt(~bm,return_indices=True)
    return r[iy,ix]
def palette(T):
    c=(B[T]*255).reshape(-1,3).astype(int);return np.unique(c,axis=0)/255
def relit_layer(k,T,F,P):
    im=np.asarray(Image.open(f'up/layer_{k}.png')).astype(float)/255
    x,y=meta[k]['x'],meta[k]['y'];h,w=im.shape[:2]
    rgb=im[...,:3]
    if T!='sunset':
        rgb=np.clip(rgb*F[y:y+h,x:x+w],0,1)
        # snap to the colours this scene already uses, so it dithers and sits like the painting
        flat=rgb.reshape(-1,3);d=((flat[:,None,:]-P[None,:,:])**2).sum(2);rgb=P[d.argmin(1)].reshape(rgb.shape)
    out=np.dstack([rgb,im[...,3]]);return Image.fromarray((out*255).astype(np.uint8))
if __name__=='__main__':
    for T in ('sunrise','day','night','sunset'):
        F=field(T) if T!='sunset' else None;P=palette(T)
        for k in meta:relit_layer(k,T,F,P).save(f'up/layer_{k}_{T}.png')
        print(T,'ok',len(P),'colours')

# ---------- colour-for-colour: what does this sunset colour become at time T, around the camp? ----------
from scipy.spatial import cKDTree
def knn_map(T,K=14,box=(560,200,952,340)):
    x0,y0,x1,y1=box
    s=B['sunset'][y0:y1,x0:x1].reshape(-1,3);t=B[T][y0:y1,x0:x1].reshape(-1,3)
    return cKDTree(s),t,K
def relit_layer2(k,T,M,F,P,mix=.75):
    im=np.asarray(Image.open(f'up/layer_{k}.png')).astype(float)/255
    x,y=meta[k]['x'],meta[k]['y'];h,w=im.shape[:2];rgb=im[...,:3]
    if T!='sunset':
        tree,t,K=M;flat=rgb.reshape(-1,3)
        dist,idx=tree.query(flat,k=K);wt=1/(dist+.02);mapped=(t[idx]*wt[...,None]).sum(1)/wt.sum(1)[:,None]
        ratio=np.clip(rgb*F[y:y+h,x:x+w],0,1).reshape(-1,3)
        mixed=mapped*mix+ratio*(1-mix)                       # mostly colour-for-colour, a little of the van's local light
        d=((mixed[:,None,:]-P[None,:,:])**2).sum(2);rgb=P[d.argmin(1)].reshape(rgb.shape)
    return Image.fromarray((np.dstack([rgb,im[...,3]])*255).astype(np.uint8))

# ---------- grey things take the van's light; coloured things keep their own colour and take only the brightness ----------
import colorsys
SATK={'sunrise':.58,'day':.78,'night':.42}
def relit_layer3(k,T,F,P):
    im=np.asarray(Image.open(f'up/layer_{k}.png')).astype(float)/255
    x,y=meta[k]['x'],meta[k]['y'];h,w=im.shape[:2];rgb=im[...,:3]
    if T!='sunset':
        R=np.clip(rgb*F[y:y+h,x:x+w],0,1)
        out=R.copy()
        for j in range(h):
            for i in range(w):
                if im[j,i,3]==0:continue
                hh,ll,ss=colorsys.rgb_to_hls(*rgb[j,i])
                wgt=np.clip((ss-.16)/.22,0,1)             # how coloured this pixel is
                if wgt==0:continue
                _,lr,_=colorsys.rgb_to_hls(*R[j,i])
                Hc=np.array(colorsys.hls_to_rgb(hh,lr,ss*SATK[T]))
                out[j,i]=R[j,i]*(1-wgt)+Hc*wgt
        flat=out.reshape(-1,3);d=((flat[:,None,:]-P[None,:,:])**2).sum(2);rgb=P[d.argmin(1)].reshape(rgb.shape)
    return Image.fromarray((np.dstack([rgb,im[...,3]])*255).astype(np.uint8))

MATERIAL={'canoe'}          # items whose colour is paint or wood, not just light on grey
def relit_layer4(k,T,F,P):
    im=np.asarray(Image.open(f'up/layer_{k}.png')).astype(float)/255
    x,y=meta[k]['x'],meta[k]['y'];h,w=im.shape[:2];rgb=im[...,:3]
    if T=='sunset':return Image.fromarray((np.dstack([rgb,im[...,3]])*255).astype(np.uint8))
    src=rgb.copy()
    if k not in MATERIAL:                       # sunset rim light is light, not paint: calm it before carrying it over
        g=(rgb@[.299,.587,.114])[...,None];rgb=rgb*.45+g*.55
    R=np.clip(rgb*F[y:y+h,x:x+w],0,1)
    if k in MATERIAL:
        out=R.copy()
        for j in range(h):
            for i in range(w):
                if im[j,i,3]==0:continue
                hh,ll,ss=colorsys.rgb_to_hls(*src[j,i]);_,lr,_=colorsys.rgb_to_hls(*R[j,i])
                out[j,i]=colorsys.hls_to_rgb(hh,lr,ss*SATK[T])
        rgb=out                                   # its own browns: the scene palette has none to offer at midday
    else:
        flat=R.reshape(-1,3);d=((flat[:,None,:]-P[None,:,:])**2).sum(2);rgb=P[d.argmin(1)].reshape(rgb.shape)
    return Image.fromarray((np.dstack([rgb,im[...,3]])*255).astype(np.uint8))
