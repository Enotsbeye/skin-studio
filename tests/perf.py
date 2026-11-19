"""Замеры скорости основных операций."""
import os, sys, pathlib, tempfile; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from env import APP, URL, launch
INSTR = os.path.join(tempfile.gettempdir(), 'instr.html')
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    br = launch(p)
    pg = br.new_page(viewport={'width': 1600, 'height': 900})
    pg.goto(URL+'?nostart'); pg.wait_for_timeout(1000)
    r = pg.evaluate("""()=>{const t=(f,n=20)=>{const a=performance.now();for(let i=0;i<n;i++)f();return +((performance.now()-a)/n).toFixed(2)};const res={};
      res.paint=t(()=>paint(state),50);res.refreshSkin=t(()=>refreshSkin(),30);res.applyRot=t(()=>applyRot(),50);
      res.thumb_bodyFB=t(()=>thumb(state,'bodyFB'),30);
      for(const id of ['body','face','hair','top','bottom','shoes','acc','paint','done']){const i=CATS.findIndex(c=>c.id===id);res['tab_'+id]=t(()=>go(i),3)}
      go(CATS.findIndex(c=>c.id==='top'));res.set_top=t(()=>set('top',state.top==='tshirt'?'hoodie':'tshirt'),10);
      res.renderPNG_1024=t(()=>renderPNG(1024,null),3);res.buildModel=t(()=>buildModel(),5);return res}""")
    for k, v in r.items(): print(f'{k:16s} {v} мс')
    br.close()
