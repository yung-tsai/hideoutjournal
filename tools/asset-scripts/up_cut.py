import numpy as np
from PIL import Image
from scipy import ndimage
L=lambda f:np.asarray(Image.open(f).convert('RGB')).astype(int)
orig=L('up/orig_tuned.png');e1=L('up/edit1_tuned.png');e3=L('up/edit3_tuned.png')
# item: (source, box x0,y0,x1,y1 inclusive, threshold)
ITEMS={'canoe':(e1,(735,241,820,257),22,True),
       'roofbox':(e3,(754,242,809,256),22,True),
       'ladder':(e3,(806,252,816,300),34,False),   # just the metal: the van shows between the rungs
       'tire':(e3,(816,267,834,295),18,True)}
def cut(src,box,T,fill=True):
    x0,y0,x1,y1=box
    d=np.abs(src-orig).max(2)
    m=np.zeros(d.shape,bool);m[y0:y1+1,x0:x1+1]=d[y0:y1+1,x0:x1+1]>T
    lab,n=ndimage.label(m,structure=np.ones((3,3)))
    if n:
        sz=ndimage.sum(m,lab,range(1,n+1))
        for i,s in enumerate(sz):
            if s<(5 if fill else 3):m[lab==i+1]=False
    if fill:m=ndimage.binary_fill_holes(m)
    rgba=np.zeros((*m.shape,4),np.uint8);rgba[...,:3]=src;rgba[...,3]=m*255
    return rgba,m
if __name__=='__main__':
    import json
    meta={}
    for k,(src,box,T,fill) in ITEMS.items():
        rgba,m=cut(src,box,T,fill)
        if k=='tire':                                   # just the tire: rubber and rim, not the fire-lit bracket around it
            yy,xx=np.mgrid[0:m.shape[0],0:m.shape[1]];m&=((xx-823.5)/8.3)**2+((yy-280.5)/12.3)**2<=1;rgba[...,3]=m*255
        ys,xs=np.where(m);bb=(int(xs.min()),int(ys.min()),int(xs.max())+1,int(ys.max())+1)
        Image.fromarray(rgba).crop(bb).save(f'up/layer_{k}.png');meta[k]={'x':bb[0],'y':bb[1],'n':int(m.sum())}
        print(k,bb,int(m.sum()),'px')
    json.dump(meta,open('up/layers.json','w'))
