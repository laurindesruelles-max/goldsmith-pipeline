import sys,json;sys.path.insert(0,'engine');import thumbnail as T
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import numpy as np
T.YELLOW=(70,235,255)
for t in 'b':
    c=json.load(open(f"videos/003-gta6-money/thumb_{t}.json"));c["background"]={"a":"videos/003-gta6-money/hero_vice_case.png","b":"videos/003-gta6-money/hero_vice_hands.png"}[t];c.pop("tag",None);c['y']=290;c['maxw']=600
    out=f'videos/003-gta6-money/thumb_{t}5.jpg';T.build(c,out)
    img=Image.open(out).convert('RGBA');W,H=img.size
    f=ImageFont.truetype(T.ANTON,230);txt="GTA 6"
    m=Image.new('L',(W,H),0);ImageDraw.Draw(m).text((50,20),txt,font=f,fill=255)
    bb=m.getbbox()
    # Sonnenuntergang: Pink oben -> Orange -> Gelb unten
    g=np.zeros((H,W,4),np.uint8);y0,y1=bb[1],bb[3]
    stops=[(0,(255,64,170)),(0.55,(255,110,80)),(1,(255,190,70))]
    for y in range(H):
        u=min(1,max(0,(y-y0)/max(1,y1-y0)))
        for (a,ca),(b,cb) in zip(stops,stops[1:]):
            if a<=u<=b: k=(u-a)/(b-a);col=[int(ca[i]+(cb[i]-ca[i])*k) for i in range(3)]
        g[y,:,:3]=col;g[y,:,3]=255
    grad=Image.fromarray(g)
    sh=Image.new('RGBA',(W,H),(0,0,0,0));ImageDraw.Draw(sh).text((62,32),txt,font=f,fill=(0,0,0,255),stroke_width=9,stroke_fill=(0,0,0,255))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(12)))
    ol=Image.new('RGBA',(W,H),(0,0,0,0));ImageDraw.Draw(ol).text((50,20),txt,font=f,fill=(0,0,0,255),stroke_width=11,stroke_fill=(0,0,0,255))
    img.alpha_composite(ol)
    glow=Image.new("RGBA",(W,H),(40,220,255,0));glow.putalpha(m.filter(ImageFilter.GaussianBlur(18)).point(lambda v:int(v*0.9)))
    pass
    fill=Image.new('RGBA',(W,H),(0,0,0,0));fill.paste(grad,(0,0),m);img.alpha_composite(fill)
    img.convert('RGB').save(out,quality=92)
