"""Автопроверка редактора скинов: python3 tests/check.py [путь к html]"""
import os, sys, pathlib, tempfile; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from env import APP, URL, launch
INSTR = os.path.join(tempfile.gettempdir(), 'instr.html')
import sys, json
from playwright.sync_api import sync_playwright
PATH = sys.argv[1] if len(sys.argv) > 1 else APP
results = []
def ok(name, cond, info=''):
    results.append((name, bool(cond), info))

with sync_playwright() as p:
    b = launch(p)
    # ---------- desktop ----------
    pg = b.new_page(viewport={'width': 1600, 'height': 900})
    errs = []
    pg.on('pageerror', lambda e: errs.append('pageerror: ' + str(e)))
    pg.on('console', lambda m: errs.append('console: ' + m.text) if m.type == 'error' else None)
    pg.goto(pathlib.Path(PATH).as_uri() + '?nostart'); pg.wait_for_timeout(900)
    pg.evaluate("()=>{try{localStorage.clear()}catch(e){}}")
    # 1. every option of every key, both models, figures, clothes modes
    bad = pg.evaluate("""()=>{const bad=[];const keys=Object.keys(OPT).filter(k=>k!=='acc');
      for(const k of keys)for(const [v] of OPT[k])for(const m of ['classic','slim'])for(const f of ['male','female3d','gendermod'])for(const c of ['3d','flat']){
        try{const d=paint(Object.assign({},state,{[k]:v,model:m,figure:f,clothes3d:c}));if(d.length!==16384)bad.push(k+':'+v)}catch(e){bad.push(k+':'+v+':'+e.message)}}
      for(const [v] of OPT.acc){try{paint(Object.assign({},state,{acc:[v]}))}catch(e){bad.push('acc:'+v+':'+e.message)}}
      for(const [v] of OPT.pattern)for(const t of ['tshirt','suit','robe','dress','hoodie_up'])for(const bt of ['jeans','skirt','overalls']){try{paint(Object.assign({},state,{topPattern:v,bottomPattern:v,top:t,bottom:bt}))}catch(e){bad.push('pattern:'+v+':'+e.message)}}
      for(const e of ['soft','classic','anime','big'])for(const a of ['gasmask','balaclava','helmet']){try{paint(Object.assign({},state,{eyes:e,acc:[a]}))}catch(er){bad.push(a+e+er.message)}}
      return bad.slice(0,10)}""")
    ok('все варианты рисуются', not bad, bad)
    # 2. every tab of every mode renders
    bad = pg.evaluate("()=>{const bad=[];for(let i=0;i<CATS.length;i++){try{go(i)}catch(e){bad.push(CATS[i].id+':'+e.message)}}go(0);return bad}")
    ok('все разделы открываются', not bad, bad)
    # 3. undo / redo, also with Russian layout
    r = pg.evaluate("""()=>{set('top','hoodie');set('top','suit');undo();const a=state.top;redo();const b=state.top;
      document.body.dispatchEvent(new KeyboardEvent('keydown',{key:'я',code:'KeyZ',ctrlKey:true,bubbles:true}));const c=state.top;return [a,b,c]}""")
    ok('отменить / повторить / Ctrl+Z на русской раскладке', r == ['hoodie', 'suit', 'hoodie'], r)
    # 4. 2D painting
    pg.evaluate("()=>{goMode('paint');tool='brush';mirror=false;brushSize=1;setPaint('#ff0000')}"); pg.wait_for_timeout(300)
    box = pg.evaluate("()=>{const r=document.getElementById('edc').getBoundingClientRect();return [r.x,r.y,r.width,r.height]}")
    before = pg.evaluate("editCount()")
    pg.mouse.click(box[0] + box[2] * (22.5 / 64), box[1] + box[3] * (25.5 / 64)); pg.wait_for_timeout(200)
    ok('рисование на развёртке', pg.evaluate("editCount()") > before, pg.evaluate("editCount()"))
    ok('цвет пикселя (22,25) красный', pg.evaluate("curPx(22,25).slice(0,3).join()") == '255,0,0')
    # 5. mirror
    pg.evaluate("()=>{mirror=true}")
    pg.mouse.click(box[0] + box[2] * (21.5 / 64), box[1] + box[3] * (28.5 / 64)); pg.wait_for_timeout(200)
    ok('зеркальная кисть', pg.evaluate("curPx(26,28).slice(0,3).join()") == '255,0,0', pg.evaluate("curPx(26,28)"))
    pg.evaluate("()=>{mirror=false}")
    # 6. 3D painting
    pg.evaluate("()=>{targetYaw=0}"); pg.wait_for_timeout(1300)
    fb = pg.evaluate("()=>{const f=faces.find(o=>o.el._tex&&o.el._tex[0]===8&&o.el._tex[1]===8&&!o.el.closest('.ov'));const r=f.el.getBoundingClientRect();return [r.x,r.y,r.width,r.height]}")
    before = pg.evaluate("editCount()")
    pg.mouse.click(fb[0] + fb[2] * 0.06, fb[1] + fb[3] * 0.06); pg.wait_for_timeout(200)
    ok('рисование по 3D-модели', pg.evaluate("editCount()") > before)
    # 6b. auto layer: stroke must be visible (on the layer you see)
    for part,tex in (('body',(20,20)),('rleg',(4,20)),('head',(8,8))):
        pg.evaluate("()=>{resetEdits();layer3d='auto';setPaint('#ff00ff')}"); pg.wait_for_timeout(150)
        fb = pg.evaluate("([u,v])=>{const all=[...document.querySelectorAll('#model .face')].filter(f=>f.getBoundingClientRect().width>0&&!f.classList.contains('plat'));const f=all.find(f=>f._tex&&f._tex[0]===u+(u===20?0:0)&&f._tex[1]===v&&f.closest('.ov'))||all.find(f=>f._tex&&f._tex[0]===u&&f._tex[1]===v);const r=f.getBoundingClientRect();return [r.x,r.y,r.width,r.height]}", list(tex))
        pg.mouse.click(fb[0]+fb[2]*0.5, fb[1]+fb[3]*0.5); pg.wait_for_timeout(200)
        vis = pg.evaluate("""()=>{const out=[];for(let y=0;y<64;y++)for(let x=0;x<64;x++){const c=curPx(x,y);if(c[0]===255&&c[1]===0&&c[2]===255&&c[3]===255)out.push([x,y])}
          return out.map(([x,y])=>{const r=regionAt(x,y);if(r.ov)return true;const o=regions().find(o=>o.k===OV_OF[r.k]&&o.fn===r.fn);const q=[o.r[0]+x-r.r[0],o.r[1]+y-r.r[1]];return curPx(q[0],q[1])[3]===0})}""")
        ok('авто-слой виден: '+part, len(vis)>0 and all(vis), vis)
    pg.evaluate("()=>{resetEdits()}")
    # 7. fill
    pg.evaluate("()=>{tool='fill';setPaint('#00ff00')}"); pg.mouse.click(box[0] + box[2] * (60.5 / 64), box[1] + box[3] * (4.5 / 64)); pg.wait_for_timeout(200)
    pg.evaluate("()=>{tool='brush'}")
    # 8. import / reset
    n = pg.evaluate("""async()=>{const blob=await new Promise(r=>skinCv.toBlob(r,'image/png'));importPNG(new File([blob],'t.png',{type:'image/png'}));
      await new Promise(r=>setTimeout(r,600));return editCount()}""")
    ok('импорт PNG', n == 4096, n)
    pg.evaluate("()=>resetEdits()")
    ok('сброс ручных правок', pg.evaluate("editCount()") == 0)
    # 9. operations (if present)
    for fn in ['opVolume', 'opShade', "()=>opMirrorPart('rarm')", "()=>opMirrorPart('rleg')", "()=>opSymmetry('head')"]:
        name = fn if fn.startswith('op') else fn[4:]
        exists = pg.evaluate(f"typeof {name.split('(')[0]}==='function'")
        if not exists: continue
        r = pg.evaluate(f"()=>{{try{{const a=editCount();({fn if not fn.startswith('op') else fn})();return [true,editCount()-a]}}catch(e){{return [false,e.message]}}}}")
        ok('операция ' + name, r[0], r)
    if pg.evaluate("typeof replaceColorAt==='function'"):
        r = pg.evaluate("()=>{const c=curPx(20,20);setPaint('#3355ff');return replaceColorAt(20,20)}")
        ok('замена цвета', r > 0, r)
    pg.evaluate("()=>resetEdits()")
    # 9b. operations really change the skin
    r = pg.evaluate("""()=>{set('clothes3d','flat');const cnt=()=>{let n=0;for(let y=36;y<48;y++)for(let x=16;x<40;x++)if(lastFinal[(y*64+x)*4+3])n++;return n};
      const a=cnt();opVolume();const b=cnt();undo();return [a,b]}""")
    ok('«Сделать объёмным» переносит одежду на 2-й слой', r[1] > r[0] + 50, r)
    r = pg.evaluate("""()=>{setPaint('#123456');tool='brush';strokeStart([45,24],null,false);strokeEnd();opMirrorPart('rarm');
      const m=mirrorOf(45,24);const v=curPx(m[0],m[1]).slice(0,3).join();resetEdits();return v}""")
    ok('копирование руки зеркально', r == '18,52,86', r)
    r = pg.evaluate("""()=>{set('hair','short');set('hairColor','#3b2416');setPaint('#e0b030');const n=replaceColorAt(9,0);const c=curPx(9,0);resetEdits();return [n,c[0]>c[2]+40]}""")
    ok('замена цвета перекрашивает волосы', r[0] > 20 and r[1], r)
    r = pg.evaluate("""()=>{setPaint('#ff0000');for(let x=20;x<28;x++)for(let y=20;y<32;y++){setPx(x,y,[255,0,0],255)}syncE();set('top','suit');
      const t=document.getElementById('toast').textContent;resetEdits();return t}""")
    ok('предупреждение о закрытых правками изменениях', 'закрыты' in r, r)
    # 9c. project file round trip
    r = pg.evaluate("""async()=>{set('hair','afro');setPx(1,1,[1,2,3],255);syncE();const data=JSON.stringify({app:'skin-studio',version:1,state});
      freshSkin();const before=state.hair;openProject(new File([data],'p.json'));await new Promise(r=>setTimeout(r,300));const res=[before,state.hair,editCount()];resetEdits();return res}""")
    ok('проект .json сохраняется и открывается', r[1] == 'afro' and r[2] >= 1, r)
    ok('8 слотов', pg.evaluate("getSlots().length") == 8)
    # 9d. poses and character picture
    r = pg.evaluate("""()=>{const bad=[];for(const [v] of POSES)for(const f of ['male','gendermod']){try{setPose(v);state.figure=f;const c=renderPNG(96,null);const d=c.getContext('2d').getImageData(0,0,96,96).data;let n=0;for(let i=3;i<d.length;i+=4)if(d[i]>0)n++;if(n<600)bad.push(v+f+':'+n)}catch(e){bad.push(v+f+':'+e.message)}}setPose('stand');state.figure='male';return bad}""")
    ok('позы и картинка персонажа рисуются', not r, r)
    # 9e. selection copy / paste on the texture
    pg.evaluate("()=>{goMode('paint');tool='select';renderToolbar('paint')}"); pg.wait_for_timeout(200)
    box = pg.evaluate("()=>{const r=document.getElementById('edc').getBoundingClientRect();return [r.x,r.y,r.width,r.height]}")
    tp = lambda tx, ty: (box[0] + box[2] * ((tx + .5) / 64), box[1] + box[3] * ((ty + .5) / 64))
    pg.mouse.move(*tp(8, 8)); pg.mouse.down(); pg.mouse.move(*tp(15, 15), steps=4); pg.mouse.up(); pg.wait_for_timeout(100)
    pg.keyboard.press('Control+c'); pg.keyboard.press('Control+v'); pg.mouse.move(*tp(40, 8)); pg.mouse.click(*tp(40, 8)); pg.wait_for_timeout(200)
    r = pg.evaluate("()=>{let same=0;for(let y=0;y<8;y++)for(let x=0;x<8;x++){const a=curPx(8+x,8+y),b=curPx(40+x,8+y);if(a.join()===b.join())same++}return same}")
    ok('выделение: копировать и вставить', r >= 60, r)
    pg.evaluate("()=>{selClear();resetEdits();tool='brush'}")
    # 9f. take parts from another skin
    r = pg.evaluate("""async()=>{const other=Object.assign({},state,{hair:'afro',hairColor:'#d94a8c'});const c=document.createElement('canvas');c.width=c.height=64;c.getContext('2d').putImageData(new ImageData(paint(other),64,64),0,0);
      const blob=await new Promise(r=>c.toBlob(r,'image/png'));mergeLoad(new File([blob],'other.png',{type:'image/png'}));await new Promise(r=>setTimeout(r,500));
      const vis=!document.getElementById('modal').hidden;document.querySelector('#mBody input[data-k="head"]').checked=true;document.querySelector('#mBody input[data-k="hat"]').checked=true;document.getElementById('mgGo').click();
      const top=curPx(9,0);const res=[vis,editCount(),top[0]>top[1]+60];resetEdits();return res}""")
    ok('взять части из другого скина', r[0] and r[1] > 100 and r[2], r)
    # 9g. state survives a page reload
    pg.evaluate("()=>{set('hair','afro');set('topColor','#123456');setPx(5,9,[1,2,3],255);syncE();save()}")
    pg.reload(); pg.wait_for_timeout(900)
    r = pg.evaluate("()=>[state.hair,state.topColor,editCount()]")
    ok('персонаж сохраняется после перезагрузки страницы', r == ['afro', '#123456', 1], r)
    pg.evaluate("()=>{resetEdits();state=clone(DEFAULT);loadE();update(true)}")
    # 10. download fallback does not throw
    r = pg.evaluate("async()=>{try{await downloadSkin();return 'ok'}catch(e){return e.message}}")
    ok('скачивание без ошибок', r == 'ok', r)
    # 11. menus open
    for m in ['file', 'edit', 'skin', 'paint', 'view', 'help']:
        pg.click(f'.mb[data-m={m}]'); pg.wait_for_timeout(80)
        ok('меню ' + m, pg.is_visible('#menuDrop'))
        pg.keyboard.press('Escape')
    pg.evaluate("()=>goMode('build')"); pg.wait_for_timeout(400); pg.screenshot(path='/tmp/chk-build.png')
    pg.evaluate("()=>goMode('paint')"); pg.wait_for_timeout(400); pg.screenshot(path='/tmp/chk-paint.png')
    pg.evaluate("()=>goMode('export')"); pg.wait_for_timeout(400); pg.screenshot(path='/tmp/chk-export.png')
    ok('нет ошибок в консоли (компьютер)', not errs, errs[:5])
    # ---------- phone with touch ----------
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, has_touch=True, is_mobile=True)
    mp = ctx.new_page(); merrs = []
    mp.on('pageerror', lambda e: merrs.append(str(e)))
    mp.goto(pathlib.Path(PATH).as_uri() + '?nostart'); mp.wait_for_timeout(900)
    ok('на телефоне страница не шире экрана', mp.evaluate('document.documentElement.scrollWidth') <= 392, mp.evaluate('document.documentElement.scrollWidth'))
    mp.evaluate("()=>{goMode('paint');tool='brush';setPaint('#ff00ff');targetYaw=0}"); mp.wait_for_timeout(1300)
    mp.evaluate("()=>document.getElementById('stage').scrollIntoView()")
    fb = mp.evaluate("()=>{const f=faces.find(o=>o.el._tex&&o.el._tex[0]===20&&o.el._tex[1]===20&&!o.el.closest('.ov'));const r=f.el.getBoundingClientRect();return [r.x,r.y,r.width,r.height]}")
    cdp = ctx.new_cdp_session(mp)
    x0, y0 = fb[0] + fb[2] * 0.2, fb[1] + fb[3] * 0.3
    cdp.send('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': x0, 'y': y0}]})
    for k in range(1, 6):
        cdp.send('Input.dispatchTouchEvent', {'type': 'touchMove', 'touchPoints': [{'x': x0 + k * fb[2] * 0.1, 'y': y0}]})
    cdp.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []})
    mp.wait_for_timeout(300)
    n = mp.evaluate("editCount()")
    ok('рисование пальцем по модели (телефон)', n >= 3, n)
    mp.evaluate("()=>{window.scrollTo(0,0);goMode('build')}"); mp.wait_for_timeout(500); mp.screenshot(path='/tmp/chk-phone.png')
    ok('нет ошибок в консоли (телефон)', not merrs, merrs[:5])
    b.close()

fails = [r for r in results if not r[1]]
for name, good, info in results:
    print(('OK   ' if good else 'FAIL ') + name + ('' if good else '  -> ' + json.dumps(info, ensure_ascii=False)[:300]))
print(f'\nИтого: {len(results) - len(fails)} из {len(results)} проверок прошли')
