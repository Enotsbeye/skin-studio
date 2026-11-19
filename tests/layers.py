# Слои: порядок, видимость, прозрачность, объединение, отмена, сохранение, проект
import os, sys, pathlib, tempfile; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from env import APP, URL, launch
INSTR = os.path.join(tempfile.gettempdir(), 'instr.html')
from playwright.sync_api import sync_playwright
res=[]
def ok(n,c,d=None):res.append((n,bool(c),d))
with sync_playwright() as p:
    b=launch(p);pg=b.new_page(viewport={'width':1400,'height':860})
    errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(URL+'?nostart');pg.wait_for_timeout(600)
    pg.evaluate("()=>{setSimple(false);goMode('paint');resetEdits()}");pg.wait_for_timeout(200)
    P="(x,y)=>curPx(x,y).slice(0,3).join(',')"
    r=pg.evaluate("""()=>{const px=(x,y)=>curPx(x,y).slice(0,3).join(',');
      setPaint('#0000ff');strokeStart([10,10],{button:0});strokeEnd();
      addLayer();setPaint('#ff0000');strokeStart([10,10],{button:0});strokeEnd();
      const top=px(10,10),n=L.length;L[1].v=false;syncE();refreshSkin();const hid=px(10,10);L[1].v=true;L[1].o=.5;syncE();refreshSkin();const half=px(10,10);
      return {n,top,hid,half}}""")
    ok('2 слоя',r['n']==2,r);ok('верхний слой перекрывает',r['top']=='255,0,0');ok('скрытый слой не виден',r['hid']=='0,0,255');ok('прозрачность 50%',r['half'] in ('128,0,128','127,0,128','128,0,127'),r['half'])
    r=pg.evaluate("()=>{const before=curPx(10,10).join(',');mergeDown();return [L.length,curPx(10,10).join(','),before]}")
    ok('объединение сохраняет вид',r[0]==1 and r[1]==r[2],r)
    pg.keyboard.press('Control+z');pg.wait_for_timeout(200);ok('Ctrl+Z отменяет объединение',pg.evaluate("()=>L.length")==2)
    r=pg.evaluate("()=>{AL=1;E=L[1].E;moveLayer(-1);return [AL,L[0].n,curPx(10,10).slice(0,3).join(',')]}")
    ok('перемещение слоя вниз',r[0]==0 and r[2]=='0,0,255',r)
    r=pg.evaluate("()=>{L[0].v=false;syncE();refreshSkin();setPaint('#00ff00');const st=strokeStart([12,12],{button:0});L[0].v=true;syncE();refreshSkin();return [st,curPx(12,12).slice(0,3).join(',')]}")
    ok('на скрытом слое не рисуется',r[0]==False and r[1]!='0,255,0',r)
    pg.evaluate("()=>{dupLayer()}");n=pg.evaluate("()=>L.length")
    pg.reload();pg.wait_for_timeout(700);ok('слои сохраняются после перезагрузки',pg.evaluate("()=>L.length")==n,n)
    r=pg.evaluate("""async()=>{syncE();const data=JSON.stringify({app:'skin-studio',version:1,state}),n=L.length;resetEdits();openProject(new File([data],'p.json'));await new Promise(r=>setTimeout(r,300));return [n,L.length]}""")
    ok('проект .json хранит слои',r[0]==r[1] and r[0]>1,r)
    r=pg.evaluate("()=>{const a=Array.from(lastFinal).join(','),m=mergedE(),c=applyEdits(paint(state),m);return a===Array.from(c).join(',')}")
    ok('сведённый вид совпадает с экспортом',r)
    r=pg.evaluate("()=>{delLayer();delLayer();delLayer();return [L.length,editCount()]}");ok('удаление до одного слоя',r[0]==1,r)
    pg.evaluate("()=>goMode('paint')");pg.wait_for_timeout(200);ok('панель слоёв видна в полном режиме',pg.evaluate("()=>getComputedStyle(document.getElementById('pnlLayers')).display!=='none'&&document.querySelectorAll('.lyrow').length>=1"))
    ok('нет ошибок',not errs,errs)
for n,c,d in res:print(('OK   ' if c else 'FAIL ')+n+('' if c or d is None else ' '+str(d)))
print('слои: %d из %d'%(sum(c for _,c,_ in res),len(res)))
