import os, sys, pathlib, tempfile; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from env import APP, URL, launch
INSTR = os.path.join(tempfile.gettempdir(), 'instr.html')
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=launch(p);pg=b.new_page(viewport={'width':1400,'height':900})
    errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(URL+'?nostart');pg.wait_for_timeout(800)
    r=pg.evaluate("""async()=>{const mk=(w,h,f)=>{const c=document.createElement('canvas');c.width=w;c.height=h;const x=c.getContext('2d');f(x);return new Promise(r=>c.toBlob(b=>r(new File([b],'t.png',{type:'image/png'})),'image/png'))};
      const res={};
      // legacy: right leg front 4x12 at (4,20): left column red, rest blue; right arm front (44,20) left column green
      let f=await mk(64,32,x=>{x.fillStyle='#888';x.fillRect(0,0,64,32);x.fillStyle='#00f';x.fillRect(4,20,4,12);x.fillStyle='#f00';x.fillRect(4,20,1,12);x.fillStyle='#0f0';x.fillRect(44,20,1,12)});
      importPNG(f);await new Promise(r=>setTimeout(r,500));
      res.legLeftFront=[curPx(20,52),curPx(23,52)];res.armLeftFront=[curPx(36,52),curPx(39,52)];res.hat=curPx(40,10)[3];res.model=state.model;
      // HD 128x128 checker: 2x2 blocks
      freshSkin();const o20=curPx(20,20).slice(0,3).join();
      f=await mk(128,128,x=>{x.imageSmoothingEnabled=false;x.drawImage(skinCv,0,0,128,128);x.fillStyle='#0f0';x.fillRect(16,16,16,16)});
      importPNG(f);await new Promise(r=>setTimeout(r,500));res.hd=[curPx(8,8),curPx(20,20).slice(0,3).join()===o20];
      // картинка персонажа 512×512 (не развёртка) -> в «Образец», скин не трогаем
      freshSkin();const before=Array.from(lastFinal).join();f=await mk(512,512,x=>x.drawImage(renderPNG(512,null),0,0));
      importPNG(f);await new Promise(r=>setTimeout(r,600));res.pic=[Array.from(lastFinal).join()===before,!!refCv,document.querySelector('.toast').textContent.includes('Образец')];
      document.querySelector('.toast button').click();await new Promise(r=>setTimeout(r,600));res.force=Array.from(lastFinal).join()!==before;
      // скриншот 640×360 -> тоже в «Образец»
      freshSkin();refCv=null;f=await mk(640,360,x=>{x.fillStyle='#345';x.fillRect(0,0,640,360)});importPNG(f);await new Promise(r=>setTimeout(r,500));res.shot=[Array.from(lastFinal).join()===Array.from(lastFinal).join(),!!refCv];res.toast=document.querySelector('.toast')&&document.querySelector('.toast').textContent;
      // drop
      freshSkin();f=await mk(64,64,x=>{x.drawImage(skinCv,0,0);x.fillStyle='#123456';x.fillRect(8,8,8,8)});const dt=new DataTransfer();dt.items.add(f);
      document.dispatchEvent(new DragEvent('dragover',{dataTransfer:dt,cancelable:true}));res.dropCls=document.body.classList.contains('dropping');
      document.dispatchEvent(new DragEvent('drop',{dataTransfer:dt,cancelable:true}));await new Promise(r=>setTimeout(r,500));res.drop=curPx(10,10);res.dropCls2=document.body.classList.contains('dropping');
      // bad size
      f=await mk(100,50,x=>{});importPNG(f);await new Promise(r=>setTimeout(r,400));res.bad=document.querySelector('.toast')&&document.querySelector('.toast').textContent;
      return res}""")
    chk=[('старый 64×32: левая нога отражена',r['legLeftFront'][1][:3]==[255,0,0] and r['legLeftFront'][0][:3]==[0,0,255]),
         ('старый 64×32: левая рука отражена',r['armLeftFront'][1][:3]==[0,255,0]),('старый 64×32: сплошная шапка убрана',r['hat']==0),
         ('HD 128×128 уменьшен',r['hd'][0][:3]==[0,255,0] and r['hd'][1]),('картинка персонажа не ломает скин, идёт в «Образец»',all(r['pic'])),('кнопка «Всё равно открыть как скин»',r['force']),('скриншот идёт в «Образец»',r['shot'][1]),('перетаскивание PNG',r['drop'][:3]==[18,52,86] and r['dropCls'] and not r['dropCls2']),
         ('картинка 100×50 — в «Образец»','100×50' in (r['bad'] or '')),('нет ошибок',not errs)]
    for n,c in chk:print(('OK   ' if c else 'FAIL ')+n)
    print('импорт: %d из %d'%(sum(c for _,c in chk),len(chk)))
