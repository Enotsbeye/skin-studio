"""Иконка приложения: изометрическая голова из скина-шаблона (верх, лицо, левый бок персонажа + внешний слой)."""
import sys, math
from PIL import Image, ImageDraw
src=Image.open(sys.argv[1]).convert('RGBA');out=sys.argv[2]
S=1024;U=S/17.5;C30=math.cos(math.radians(30));S30=0.5
cx,cy=S/2-8*C30*U,S/2-0.5*U   # точка (0,0,0) — левый нижний угол лица
def P(x,y,z):return (cx+(x+y)*C30*U, cy+(x-y)*S30*U-(z-4)*U)
img=Image.new('RGBA',(S,S),(0,0,0,0));d=ImageDraw.Draw(img)
def sh(c,k):return tuple(max(0,min(255,int(ch*k))) for ch in c[:3])+(255,)
for (fr,sd,tp,g) in [((8,8),(16,8),(8,0),0.0),((40,8),(48,8),(40,0),0.45)]:
    m=(8+2*g)/8;L=lambda v:-g+v*m
    for i in range(8):
        for j in range(8):
            c=src.getpixel((fr[0]+i,fr[1]+j))   # лицо: плоскость y=-g
            if c[3]>20:d.polygon([P(L(i),-g,L(8-j)),P(L(i+1),-g,L(8-j)),P(L(i+1),-g,L(7-j)),P(L(i),-g,L(7-j))],fill=sh(c,.93))
            c=src.getpixel((sd[0]+i,sd[1]+j))   # бок: плоскость x=8+g
            if c[3]>20:d.polygon([P(8+g,L(i),L(8-j)),P(8+g,L(i+1),L(8-j)),P(8+g,L(i+1),L(7-j)),P(8+g,L(i),L(7-j))],fill=sh(c,.72))
            c=src.getpixel((tp[0]+i,tp[1]+j))   # верх: плоскость z=8+g, нижняя строка текстуры — у лица
            if c[3]>20:d.polygon([P(L(i),L(7-j),8+g),P(L(i+1),L(7-j),8+g),P(L(i+1),L(8-j),8+g),P(L(i),L(8-j),8+g)],fill=sh(c,1.06))
bb=img.getbbox();img=img.crop(bb);w,h=img.size;s=max(w,h)
sq=Image.new('RGBA',(s,s),(0,0,0,0));sq.paste(img,((s-w)//2,(s-h)//2))
final=Image.new('RGBA',(S,S),(0,0,0,0));sq=sq.resize((940,940),Image.LANCZOS);final.paste(sq,(42,42))
final.save(out);final.resize((256,256),Image.LANCZOS).save(out.replace('.png','-256.png'))
final.save(out.replace('.png','.ico'),sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])
