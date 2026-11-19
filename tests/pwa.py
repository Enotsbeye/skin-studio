# Проверка установки с сайта: манифест, иконки, офлайн-кэш (service worker)
import os, sys, subprocess, time; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from env import launch
from playwright.sync_api import sync_playwright
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
srv=subprocess.Popen(['python3','-m','http.server','8765','--bind','127.0.0.1'],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
res=[]
try:
  with sync_playwright() as p:
    b=launch(p)
    ctx=b.new_context();pg=ctx.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('http://localhost:8765/?nostart');pg.wait_for_timeout(1500)
    m=pg.evaluate("async()=>{const r=await fetch(document.querySelector('link[rel=manifest]').href);const j=await r.json();const ic=await Promise.all(j.icons.map(i=>fetch(i.src).then(x=>x.ok)));return [j.short_name,j.display,ic.every(Boolean)]}")
    res.append(('манифест читается, иконки на месте',m==['Скин-студия','standalone',True],m))
    pg.evaluate("()=>navigator.serviceWorker.ready");pg.reload();pg.wait_for_timeout(1200)
    ctl=pg.evaluate("()=>!!navigator.serviceWorker.controller");res.append(('офлайн-кэш (service worker) включился',ctl,ctl))
    ctx.set_offline(True);pg.reload();pg.wait_for_timeout(1200)
    ok=pg.evaluate("()=>typeof applyTemplate==='function'&&!!document.querySelector('#stage')");res.append(('без интернета открывается из кэша',ok,ok))
    res.append(('нет ошибок',not errs,errs[:2]));b.close()
finally:srv.terminate()
ok=0
for n,v,*x in res:
    print('OK  ' if v else 'FAIL',n,'' if v else x);ok+=bool(v)
print(f'сайт-приложение: {ok} из {len(res)}')
