import os, sys, pathlib, tempfile; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from env import APP, URL, launch
INSTR = os.path.join(tempfile.gettempdir(), 'instr.html')
import os
# Доп. проверки: заморозка позы при рисовании, предупреждение о недоступной памяти, Ctrl+колёсико по развёртке
from playwright.sync_api import sync_playwright
res=[]
with sync_playwright() as p:
    b=launch(p)
    pg=b.new_page(viewport={'width':1400,'height':900});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(URL+'?nostart');pg.wait_for_timeout(800)
    g="()=>pivs.rarm.style.transform"
    pg.evaluate("()=>setPose('walk')");a=pg.evaluate(g);pg.wait_for_timeout(300);res.append(('поза двигается в конструкторе',a!=pg.evaluate(g)))
    pg.evaluate("()=>goMode('paint')");pg.wait_for_timeout(100);a=pg.evaluate(g);pg.wait_for_timeout(400);res.append(('поза замирает при рисовании',a==pg.evaluate(g)))
    r=pg.evaluate("()=>{const c=document.getElementById('edc').getBoundingClientRect();return [c.x+c.width*.6,c.y+c.height*.6]}")
    pg.mouse.move(*r);pg.keyboard.down('Control');pg.mouse.wheel(0,-100);pg.wait_for_timeout(100);pg.keyboard.up('Control');pg.wait_for_timeout(150)
    res.append(('Ctrl+колёсико масштабирует развёртку',pg.evaluate("()=>edZoom")==2))
    t=pg.evaluate("""()=>{const keys=new Set(),bad=[];TEMPLATES.forEach((t,i)=>{const s=tplState(i);for(const k in t.s)if(JSON.stringify(s[k])!==JSON.stringify(t.s[k]))bad.push(t.n+':'+k);
        let h=0;const px=paint(s);for(let j=0;j<px.length;j++)h=(h*31+px[j])|0;keys.add(h)});return {n:TEMPLATES.length,bad,uniq:keys.size}}""")
    res.append(('100 шаблонов, все поля допустимы',t['n']==100 and not t['bad'],t['bad'][:5]))
    res.append(('все 100 шаблонов выглядят по-разному',t['uniq']==100,t['uniq']))
    res.append(('длинных причёсок в шаблонах ≥ 40',pg.evaluate("()=>TEMPLATES.filter(t=>LONG_HAIR.includes(t.s.hair)).length")>=40))
    pg.evaluate("()=>go(0)");pg.wait_for_function("()=>TPL_THUMB.filter(Boolean).length===100",timeout=20000)
    before=pg.evaluate("()=>JSON.stringify(state)");pg.click('.tplt >> nth=20');pg.wait_for_timeout(200)
    res.append(('клик по шаблону ставит его',pg.evaluate("()=>state.hair===TEMPLATES[20].s.hair&&state.top===TEMPLATES[20].s.top")))
    pg.keyboard.press('Control+z');pg.wait_for_timeout(200);res.append(('Ctrl+Z возвращает прошлого персонажа',pg.evaluate("()=>JSON.stringify(state)")==before))
    pg.click('.tplf button >> nth=3');pg.wait_for_timeout(200);res.append(('фильтр «Длинные волосы»',pg.evaluate("()=>[...document.querySelectorAll('.tplt')].every(b=>LONG_HAIR.includes(TEMPLATES[+b.dataset.i].s.hair))&&document.querySelectorAll('.tplt').length>=40")))
    res.append(('простой вид: правая колонка скрыта в конструкторе',pg.evaluate("()=>document.body.classList.contains('simple')&&getComputedStyle(document.querySelector('.side.right')).display==='none'")))
    pg.evaluate("()=>goMode('paint')");pg.wait_for_timeout(200)
    res.append(('простой вид: палитра видна, структура скрыта при рисовании',pg.evaluate("()=>getComputedStyle(document.getElementById('pnlPal')).display!=='none'&&getComputedStyle(document.getElementById('pnlOut')).display==='none'")))
    pg.mouse.move(700,400);pg.keyboard.press('r');pg.wait_for_timeout(200)
    res.append(('горячая клавиша скрытого инструмента включает полный вид',pg.evaluate("()=>!uiSimple&&tool==='replace'")))
    pg.click('#uiBtn');pg.wait_for_timeout(200);res.append(('кнопка возвращает простой вид',pg.evaluate("()=>uiSimple&&tool==='brush'")))
    pg.reload();pg.wait_for_timeout(600);res.append(('выбор вида запоминается',pg.evaluate("()=>uiSimple")))
    pg.click('#uiBtn');pg.reload();pg.wait_for_timeout(600);res.append(('полный вид запоминается',pg.evaluate("()=>!uiSimple")));pg.click('#uiBtn')
    pg.evaluate("()=>{setSimple(true);goMode('paint');setPaint('#ff0000');paintColor2='#00ff00';updColorUI();resetEdits()}");pg.wait_for_timeout(300)
    r=pg.evaluate("()=>{const c=document.getElementById('edc').getBoundingClientRect();return [c.x,c.y,c.width]}");s_=r[2]/64
    pg.mouse.click(r[0]+s_*10.5,r[1]+s_*10.5,button='right');pg.mouse.click(r[0]+s_*12.5,r[1]+s_*10.5);pg.wait_for_timeout(150)
    res.append(('ПКМ рисует вторым цветом, ЛКМ — основным',pg.evaluate("()=>curPx(10,10).slice(0,3).join()==='0,255,0'&&curPx(12,10).slice(0,3).join()==='255,0,0'")))
    pg.mouse.move(700,420);pg.keyboard.press('x');res.append(('X меняет цвета местами',pg.evaluate("()=>paintColor==='#00ff00'&&paintColor2==='#ff0000'")))
    pg.keyboard.press('Digit1');res.append(('1–7 берут оттенок из лестницы, основа не сдвигается',pg.evaluate("()=>rampBase==='#00ff00'&&paintColor!=='#00ff00'&&document.querySelectorAll('#ramp button').length===7")))
    pg.keyboard.press('BracketRight');res.append(('] увеличивает кисть',pg.evaluate("()=>brushSize")==2));pg.keyboard.press('BracketLeft')
    fb=pg.evaluate("()=>{const f=[...document.querySelectorAll('#model .face')].find(f=>f._tex&&f._tex[0]===20&&f._tex[1]===20);const r=f.getBoundingClientRect();return [r.x+r.width/2,r.y+r.height/2+4]}")
    pg.mouse.move(*fb);pg.wait_for_timeout(80);pg.keyboard.press('q');res.append(('Q показывает одну часть',pg.evaluate("()=>hiddenParts.size===10&&!hiddenParts.has('body')")))
    pg.keyboard.press('q');res.append(('второй Q возвращает всё',pg.evaluate("()=>hiddenParts.size===0")))
    pg.keyboard.down('c');a_=pg.evaluate("()=>!document.getElementById('beforeTag').hidden");pg.keyboard.up('c')
    res.append(('держать C — скин до правок',a_ and pg.evaluate("()=>document.getElementById('beforeTag').hidden")))
    pg.evaluate("()=>{const c=document.createElement('canvas');c.width=40;c.height=20;const x=c.getContext('2d');x.fillStyle='#ab3344';x.fillRect(0,0,40,20);refCv=c;renderRef()}")
    rr=pg.evaluate("()=>{const c=document.querySelector('#refBody canvas').getBoundingClientRect();return [c.x+c.width/2,c.y+c.height/2]}");pg.mouse.click(*rr)
    res.append(('пипетка по образцу',pg.evaluate("()=>paintColor")=='#ab3344'))
    r=pg.evaluate("""()=>{const cnt=(m)=>{let n=0,semi=0,holes=0;for(let i=0;i<100;i++){const st=tplState(i);st.clothes3d=m;const px=paint(st);
        for(let j=3;j<px.length;j+=4)if(px[j]>0&&px[j]<255)semi++;}return semi};
      const ov=m=>{const st=tplState(0);st.clothes3d=m;const px=paint(st);let n=0;for(let y=32;y<48;y++)for(let x=16;x<40;x++)if(px[(y*64+x)*4+3])n++;return n};
      const st=sanitize({top:'tshirt',clothes3d:'3d'});return {semi:cnt('detail'),full:ov('3d'),det:ov('detail'),flat:ov('flat'),mig:st.clothes3d,def:DEFAULT.clothes3d}}""")
    res.append(('объёмные детали: на 2-м слое меньше, чем при «целиком», но не пусто',r['flat']<r['det']<r['full'],r))
    res.append(('объёмные детали без полупрозрачных пикселей',r['semi']==0,r['semi']))
    res.append(('старые сохранения переходят на объёмные детали',r['mig']=='detail' and r['def']=='detail',r))
    r=pg.evaluate("""()=>{setSimple(true);goMode('paint');resetEdits();setPaint('#ff0000');paintColor2='#0000ff';tool='dither';
      strokeStart([20,22],{button:0});strokeMove([23,22],true);strokeEnd();const row=[20,21,22,23].map(x=>curPx(x,22).slice(0,3).join());tool='brush';return row}""")
    res.append(('сетка чередует основной и второй цвет',r==['255,0,0','0,0,255','255,0,0','0,0,255'],r))
    pg.evaluate("()=>{applyTemplate(60);go(0)}");pg.wait_for_timeout(2900);bx=pg.locator('.tplt').nth(4).bounding_box()
    h0=pg.evaluate("()=>[state.hair,faces.map(f=>f.sig).join()]")
    pg.mouse.move(bx['x']+40,bx['y']+40);pg.wait_for_timeout(450);h1=pg.evaluate("()=>[state.hair,faces.map(f=>f.sig).join(),tplPrev]")
    pg.mouse.click(bx['x']+40,bx['y']+40);pg.wait_for_timeout(300);h2=pg.evaluate("()=>state.hair===TEMPLATES[4].s.hair")
    res.append(('шаблон: наведение ничего не меняет, клик применяет',h1[:2]==h0 and h1[2]==-1 and h2,[h0,h1,h2]))
    pg.evaluate("()=>{applyTemplate(56);go(CATS.findIndex(c=>c.id==='hair'))}");pg.wait_for_timeout(1500);bx=pg.locator('.opt').nth(17).bounding_box()
    pg.mouse.move(bx['x']+30,bx['y']+30);pg.wait_for_timeout(450);on=pg.evaluate("()=>[tplPrev,state.hair]")
    pg.mouse.click(bx['x']+30,bx['y']+30);pg.wait_for_timeout(300);after=pg.evaluate("()=>state.hair")
    res.append(('причёска: наведение без примерки, клик меняет',on==[-1,TEMPLATES_HAIR56] if False else (on[0]==-1 and on[1]!=after),[on,after]))
    r=pg.evaluate("""()=>{applyTemplate(12);goMode('paint');const before=Array.from(lastFinal).join(),n0=L.length;openAdjust();
      const rg=document.querySelectorAll('.adjrow input')[0];rg.value=90;rg.dispatchEvent(new Event('input'));const changed=Array.from(lastFinal).join()!==before;
      closeModal();const back=Array.from(lastFinal).join()===before&&L.length===n0;
      openAdjust();const r2=document.querySelectorAll('.adjrow input')[2];r2.value=-30;r2.dispatchEvent(new Event('input'));[...document.querySelectorAll('#mBody .btn')].find(b=>b.textContent==='Применить').click();
      return [changed,back,L.length===n0+1&&L[L.length-1].n==='Цвет']}""")
    res.append(('«Цвет и яркость»: живое превью, отмена без следов, применение отдельным слоем',all(r),r))
    r=pg.evaluate("()=>{resetEdits();for(const [x,y] of [[20,22],[21,22],[22,22]])setPx(x,y,[0,0,0],0);syncE();refreshSkin();const n=baseHoles().length;fillHoles();return [n,baseHoles().length]}")
    res.append(('заделка дыр цветом соседей',r==[3,0],r))
    r=pg.evaluate("""()=>{goMode('paint');const c=renderPNG(256,'#88aacc');refCv=c;refPalCache=null;renderRef();palMode='ref';renderPalette();
      const n=document.querySelectorAll('#paletteBody .pal button').length;document.getElementById('refClear').click();return [n,palMode]}""")
    res.append(('палитра из образца',r[0]>=8 and r[1]=='def',r))
    r=pg.evaluate("""()=>{localStorage.removeItem('mcskin.slots.v1');window._slots=null;applyTemplate(30);go(0);document.querySelector('.addslot').click();
      applyTemplate(5);go(0);const card=document.querySelector('.myrow .tplc:not(.addslot)');card.click();const loaded=state.hair===TEMPLATES[30].s.hair;
      go(0);document.querySelector('.myrow .tplc .x').click();return [loaded,getSlots().filter(Boolean).length]}""")
    res.append(('«Мои персонажи» во вкладке шаблонов: сохранить, загрузить, удалить',r==[True,0],r))
    code=os.environ.get('GIFT_CODE','')  # сам код в тестах не хранится: задаётся переменной окружения
    r=pg.evaluate("""(code)=>{setGift(null);const before=document.documentElement.outerHTML;openCode();const i=document.querySelector('#mBody input');
      i.value='неверно';i.dispatchEvent(new KeyboardEvent('keydown',{key:'Enter'}));const bad=document.body.classList.contains('gift');if(!code){closeModal();return [bad,null]}
      i.value=code;i.dispatchEvent(new KeyboardEvent('keydown',{key:'Enter'}));const good=document.body.classList.contains('gift')&&document.title===GT.brand&&$('#brandName').textContent===GT.brand;
      const stored=localStorage.getItem('mcskin.d')||'',low=s=>s.toLowerCase(),c=low(code);
      const hidden=!before.includes(GT.brand)&&!before.includes(GT.hi)&&!low(before).includes(c)&&!low(stored).includes(c);
      setGift(null);return [bad,good,hidden,document.body.classList.contains('gift')]}""",code)
    res.append(('особый режим: чужой код не подходит'+('; свой включает, тексты и код не видны в странице, выключается' if code else ' (GIFT_CODE не задан — включение не проверялось)'),
                r==[False,True,True,False] if code else r[0] is False,r))
    if code:
        pg.evaluate("(c)=>{openCode();const i=document.querySelector('#mBody input');i.value=c;i.dispatchEvent(new KeyboardEvent('keydown',{key:'Enter'}))}",code)
        pg.reload();pg.wait_for_timeout(700);r=pg.evaluate("()=>[giftMode,!!(GT&&GT.brand),/^\\d+$/.test(localStorage.getItem('mcskin.d')||'')]")
        res.append(('особый режим держится после перезапуска (на устройстве лежит только ключ)',r==[True,True,True],r));pg.evaluate("()=>setGift(null)")
    pg.evaluate("()=>localStorage.setItem('mcskin.d','1')")
    pg.reload();pg.wait_for_timeout(700)
    r=pg.evaluate("()=>[giftMode,document.body.classList.contains('gift'),localStorage.getItem('mcskin.d')]");pg.evaluate("()=>localStorage.removeItem('mcskin.d')")
    res.append(('старая метка «1» без кода режим не включает',r[0] is False and r[1] is False,r))
    r=pg.evaluate("""()=>{setSimple(true);const vis=getComputedStyle($('#ovBtn')).display!=='none';$('#ovBtn').click();const hid=$('#model').classList.contains('flat');
      setSimple(false);setSimple(true);goMode('paint');layer3d='auto';applyPaintMode();applyTemplate(7);go(0);goMode('paint');return [vis,hid,$('#model').classList.contains('flat'),$('#ovBtn').getAttribute('aria-pressed')]}""")
    pg.reload();pg.wait_for_timeout(700);r2=pg.evaluate("()=>[$('#model').classList.contains('flat'),$('#ovBtn').getAttribute('aria-pressed')]");pg.evaluate("()=>setOv(true)")
    res.append(('2-й слой: кнопка видна в простом режиме, скрытый слой сам не включается и помнится после перезапуска',r==[True,True,True,'false'] and r2==[True,'false'],[r,r2]))
    r=pg.evaluate("""async()=>{applyTemplate(20);goMode('paint');layer3d='auto';await new Promise(r=>setTimeout(r,200));const s0=faces.map(f=>f.sig);
      pushHist('');setPx(12,12,[255,0,255],255);syncE();refreshSkin();const s1=faces.map(f=>f.sig);const changed=s1.filter((v,i)=>v!==s0[i]).length;
      const f=faces.find(f=>{const t=f.el._tex;return t&&!f.ov&&12>=t[0]&&12<t[0]+t[2]&&12>=t[1]&&12<t[1]+t[3]});
      const img=new Image();img.src=f.el.style.backgroundImage.slice(5,-2);await img.decode();const c=document.createElement('canvas');c.width=img.width;c.height=img.height;const x=c.getContext('2d');x.drawImage(img,0,0);
      const t=f.el._tex,k=SHADE_LO+(SHADE_HI-SHADE_LO)*f.lv/(SHADE_N-1),got=[...x.getImageData(12-t[0],12-t[1],1,1).data],want=[255*k,0,255*k].map(v=>Math.round(Math.min(255,v)));
      showBefore(true);const sb=f.sig;showBefore(false);const sa=f.sig;undo();
      return [changed,Math.abs(got[0]-want[0])<=2&&got[1]<=2&&Math.abs(got[2]-want[2])<=2,sb!==s1[faces.indexOf(f)],sa===s1[faces.indexOf(f)],[got,want]]}""")
    res.append(('3D: мазок перерисовывает только свою грань, цвет и свет верные, «До/после» работает',r[0]==1 and r[1] and r[2] and r[3],r))
    r=pg.evaluate("()=>[!!$('#platModel').querySelector('.platbox'),!$('#model').querySelector('.platbox'),[...document.querySelectorAll('#model .face')].every(e=>!e.style.filter)]")
    res.append(('подставка в своём 3D-слое, у граней нет CSS-фильтров',r==[True,True,True],r))
    r=pg.evaluate("""()=>{let bad=[];for(let t=0;t<100;t+=3){const st=Object.assign(tplState(t),{figure:'gendermod',hair:'bald',beard:'none'});const px=paint(st);let n=0;
      for(let y=34;y<44;y++)for(let x=17;x<31;x++)if(px[(y*64+x)*4+3])n++;if(n)bad.push(TEMPLATES[t].n+':'+n)}return bad}""")
    res.append(('Female Gender Mod: на груди нет висящих кусков второго слоя (без волос и бороды)',not r,r[:5]))
    r=pg.evaluate("""async()=>{const of=window.fetch;const ans=v=>window.fetch=async()=>({ok:true,json:async()=>v});
      const menuHas=t=>{openMenu&&0;return MENUS.help.some(it=>it.l&&it.l.includes(t)&&(!it.show||it.show()))};
      ans({version:'1.2.0',donate:'https://evil.example/pay'});await siteInfo();const bad=!DONATE&&!menuHas('Поддержать');
      ans({version:'1.2.0',donate:'https://ko-fi.com/skinstudio'});await siteInfo();const good=DONATE==='https://ko-fi.com/skinstudio'&&menuHas('Поддержать');
      window.fetch=of;DONATE='';openAbout();const ab=$('#mBody').textContent;closeModal();openStart(false);const st=$('#mBody').textContent;closeModal();
      return [bad,good,ab.includes('Не официальный продукт Minecraft')&&ab.includes('NOT AN OFFICIAL MINECRAFT'),st.includes('Не официальный продукт Minecraft'),APP_VERSION]}""")
    res.append(('«О программе» и стартовый экран с пометкой Mojang; «Поддержать» только с проверенной ссылкой',r[:4]==[True,True,True,True],r))
    res.append(('нет ошибок',not errs))
    pg2=b.new_page();e2=[];pg2.on('pageerror',lambda e:e2.append(str(e)))
    pg2.add_init_script("Storage.prototype.setItem=function(){throw new Error('QuotaExceeded')}")
    pg2.goto(URL+'?nostart');pg2.wait_for_timeout(800)
    pg2.evaluate("()=>{state.hair=OPT.hair[2][0];update()}");pg2.wait_for_timeout(300)
    res.append(('предупреждение, если память браузера недоступна','не даёт сохранять' in pg2.evaluate("()=>document.getElementById('toast').textContent") and not e2))
for n,c,*d in res:print(('OK   ' if c else 'FAIL ')+n+('' if c or not d else ' '+str(d)))
print('доп: %d из %d'%(sum(bool(x[1]) for x in res),len(res)))
