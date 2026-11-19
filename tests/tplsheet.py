"""Контактные листы всех 100 шаблонов: спереди и сзади."""
import os, sys, pathlib, tempfile; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from env import APP, URL, launch
INSTR = os.path.join(tempfile.gettempdir(), 'instr.html')
import sys
from playwright.sync_api import sync_playwright
yaw=float(sys.argv[1]) if len(sys.argv)>1 else -24
with sync_playwright() as p:
    b=launch(p);pg=b.new_page(viewport={'width':1300,'height':900})
    pg.goto(URL+'?nostart');pg.wait_for_timeout(600)
    for part in (0,1):
        pg.evaluate("""([a,yaw])=>{const imgs=[];for(let i=a;i<a+50;i++){const st=tplState(i),c=document.createElement('canvas');c.width=c.height=64;c.getContext('2d').putImageData(new ImageData(paint(st),64,64),0,0);
          imgs.push([renderPNG(240,'#2a2e37',{src:c,st,yaw,pitch:-6,R:{head:[0,0,0],body:[0,0,0],rarm:[0,0,4],larm:[0,0,-4],rleg:[0,0,0],lleg:[0,0,0],off:0}}).toDataURL(),TEMPLATES[i].n])}
          document.body.innerHTML='';document.body.style.cssText='margin:0;background:#1b1d22;display:flex;flex-wrap:wrap;gap:2px;font:11px sans-serif;color:#ccc';
          imgs.forEach(([u,n])=>{const d=document.createElement('div');d.style.cssText='width:128px;text-align:center';const im=new Image();im.src=u;im.style.cssText='width:128px;height:170px;object-fit:cover';d.append(im,n);document.body.appendChild(d)})}""",[part*50,yaw])
        pg.wait_for_timeout(400);pg.screenshot(path=f'/tmp/tpl{part}{"b" if abs(yaw)>90 else ""}.png',full_page=True)
