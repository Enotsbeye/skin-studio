"""Проверка облачной галереи на имитации базы данных страницы."""
import os, sys, pathlib, tempfile; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from env import APP, URL, launch
INSTR = os.path.join(tempfile.gettempdir(), 'instr.html')
from playwright.sync_api import sync_playwright
MOCK = r"""
(()=>{const store=new Map(),subs=[];const snapOf=(col)=>{const docs=[...store.entries()].filter(([p])=>p.startsWith(col+'/')&&p.split('/').length===col.split('/').length+1)
  .map(([p,v])=>({id:p.split('/').pop(),exists:true,data:()=>v,metadata:{fromCache:false,hasPendingWrites:false}})).sort((a,b)=>b.data().updated-a.data().updated);
  return {docs,size:docs.length,empty:!docs.length,docChanges:()=>[],metadata:{fromCache:false,hasPendingWrites:false}}};
const notify=()=>subs.forEach(s=>s.cb(snapOf(s.col)));
const coll=(col)=>({path:col,orderBy(){return this},limit(){return this},onSnapshot(cb){subs.push({col,cb});setTimeout(()=>cb(snapOf(col)),50);return()=>{}},
  doc:(id)=>({id,set:async b=>{if(JSON.stringify(b).length>256*1024){throw {code:'invalid_argument'}}store.set(col+'/'+id,JSON.parse(JSON.stringify(b)));notify()},delete:async()=>{store.delete(col+'/'+id);notify()}})});
const db={collection:coll,doc:()=>{}},user={id:async()=>'u123',isOwner:()=>true};
window.__store=store;window.claude={use:async n=>n==='db'?db:n==='user'?user:null};})();
"""
with sync_playwright() as p:
    b = launch(p)
    pg = b.new_page(viewport={'width': 1600, 'height': 900}); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.add_init_script(MOCK)
    pg.goto(URL+'?nostart'); pg.wait_for_timeout(900)
    res = pg.evaluate("""async()=>{goMode('export');await new Promise(r=>setTimeout(r,200));const st0=cloudState;
      set('hair','afro');setPx(2,2,[9,9,9],255);syncE();await cloudSave(false);const n1=window.__store.size;const size=JSON.stringify([...window.__store.values()][0]).length;
      freshSkin();const h0=state.hair;await new Promise(r=>setTimeout(r,100));cloudLoad(cloudList[0]);const h1=state.hair,e1=editCount();
      await cloudSave(true);const n2=window.__store.size;await cloudRemove(cloudList[0]);await cloudRemove(cloudList[0]);await new Promise(r=>setTimeout(r,100));
      return {st0,n1,size,h0,h1,e1,n2,n3:window.__store.size,list:document.querySelectorAll('#pbody .slot.full').length}}""")
    pg.screenshot(path='/tmp/cloud.png')
    print(res, errs)
    good = res['st0'] == 'ready' and res['n1'] == 1 and res['h1'] == 'afro' and res['e1'] >= 1 and res['n2'] == 2 and res['n3'] == 1 and not errs
    print('OK   облачная галерея' if good else 'FAIL облачная галерея')
    b.close()
