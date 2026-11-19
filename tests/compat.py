"""Старые сохранения: состояние первой версии, битые правки, неизвестные значения — приложение должно открываться без ошибок."""
import os, sys, pathlib, tempfile; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from env import APP, URL, launch
INSTR = os.path.join(tempfile.gettempdir(), 'instr.html')
from playwright.sync_api import sync_playwright
OLD = {'name':'old-skin','model':'classic','skin':'#e8b48a','eyes':'classic','eyeColor':'#3b6fd6','brows':'normal','mouth':'smile','cheeks':'none','beard':'none',
       'hair':'short','hairColor':'#3b2416','top':'tshirt','topColor':'#2f80d1','topColor2':'#f2f2f2','print':'band','bottom':'jeans','bottomColor':'#1f3c73',
       'shoes':'sneakers','shoesColor':'#c62828','acc':['glasses'],'accColor':'#2b2b2e','preset':'citizen'}
CASES = {
  'первая версия': OLD,
  'битые правки': dict(OLD, edits={'px':'@@@не base64','m':'xx'}),
  'неизвестные значения': dict(OLD, hair='unicorn', top='spacesuit', acc=['jetpack', 'glasses'], eyeColor='blue', shadeK='много'),
  'мусор': 'не json',
}
import json
with sync_playwright() as p:
    br = launch(p)
    for name, st in CASES.items():
        ctx = br.new_context(); pg = ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        val = st if isinstance(st, str) else json.dumps(st)
        pg.add_init_script("try{if(!sessionStorage.getItem('x')){localStorage.setItem('mcskin.state.v1',%s);localStorage.setItem('mcskin.slots.v1','[%s,null]');sessionStorage.setItem('x','1')}}catch(e){}" % (json.dumps(val), val if not isinstance(st, str) else 'null'))
        pg.goto(URL+'?nostart'); pg.wait_for_timeout(900)
        r = pg.evaluate("()=>{for(let i=0;i<CATS.length;i++)go(i);go(0);return [state.name,state.hair,lastFinal.length,getSlots().length]}")
        expect_name = 'my-skin' if isinstance(st, str) else 'old-skin'
        good = not errs and r[0] == expect_name and r[1] == 'short' and r[2] == 16384
        extra = pg.evaluate("()=>[state.eyeColor,state.shadeK,state.acc.join()]")
        if name == 'неизвестные значения': good = good and extra == ['#3b6fd6', 1, 'glasses']
        print(('OK   ' if good else 'FAIL ') + name, r, extra, errs[:2])
        ctx.close()
    br.close()
