"""Случайные сценарии: сотни действий подряд и проверка инвариантов после каждого."""
import os, sys, pathlib, tempfile; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from env import APP, URL, launch
INSTR = os.path.join(tempfile.gettempdir(), 'instr.html')
import sys, json
from playwright.sync_api import sync_playwright
STEPS = int(sys.argv[1]) if len(sys.argv) > 1 else 400
SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 1
JS = r"""async ({steps,seed})=>{
 let r=seed;const rnd=()=>{r=(r*1103515245+12345)%2147483648;return r/2147483648};const pick=a=>a[Math.floor(rnd()*a.length)];
 const hex=()=>'#'+[0,0,0].map(()=>Math.floor(rnd()*256).toString(16).padStart(2,'0')).join('');
 const log=[],fails=[];const J=()=>JSON.stringify(state);
 const eqE=(d,e)=>{if(!d)return layerCount(e)===0;for(let i=0;i<4096;i++){if(d.m[i]!==e.m[i])return false;if(d.m[i]){const j=i*4;for(let c=0;c<4;c++)if(d.px[j+c]!==e.px[j+c])return false}}return true};
 const sameE=()=>{if(E!==L[AL].E)return false;if(state.layers){if(state.layers.length!==L.length)return false;return state.layers.every((l,i)=>eqE(deser(l),L[i].E)&&l.v===L[i].v&&l.o===L[i].o)}return L.length===1&&eqE(deser(state.edits),L[0].E)};
 const renderOK=()=>{const a=compositeLayers(paint(state)),b=sctx.getImageData(0,0,64,64).data;for(let i=0;i<16384;i+=4){if(a[i+3]!==b[i+3])return false;if(a[i+3]===255&&(a[i]!==b[i]||a[i+1]!==b[i+1]||a[i+2]!==b[i+2]))return false}return true};
 const keys=Object.keys(OPT).filter(k=>!['acc','pattern'].includes(k)).concat(['topPattern','bottomPattern']);
 const colorKeys=['skin','eyeColor','eyeColor2','hairColor','hairColor2','topColor','topColor2','bottomColor','bottomColor2','shoesColor','accColor'];
 const A={
  setOpt:()=>{const k=pick(keys);const list=OPT[k]||OPT.pattern;set(k,pick(list)[0])},
  setColor:()=>set(pick(colorKeys),hex()),
  setColorQuiet:()=>set(pick(colorKeys),hex(),true),
  acc:()=>{const a=pick(OPT.acc)[0];set('acc',state.acc.includes(a)?state.acc.filter(x=>x!==a):withAcc(a))},
  shade:()=>set('shadeK',Math.round(rnd()*20)/10,true),
  go:()=>go(Math.floor(rnd()*CATS.length)),
  stroke:()=>{tool=pick(['brush','eraser','dark','light']);brushSize=1+Math.floor(rnd()*4);brushShape=pick(['square','circle']);mirror=rnd()<.5;noise=rnd()<.3?20:0;setPaint(hex());
    const p=[Math.floor(rnd()*64),Math.floor(rnd()*64)];if(strokeStart(p,null,false)){for(let i=0;i<5;i++)strokeMove([Math.min(63,Math.max(0,p[0]+Math.floor(rnd()*9)-4)),Math.min(63,Math.max(0,p[1]+Math.floor(rnd()*9)-4))]);strokeEnd()}},
  fill:()=>{tool='fill';setPaint(hex());strokeStart([Math.floor(rnd()*64),Math.floor(rnd()*64)],null,false)},
  replace:()=>{tool='replace';tol=Math.floor(rnd()*60);replaceScope=pick(['all','part']);setPaint(hex());strokeStart([Math.floor(rnd()*64),Math.floor(rnd()*64)],null,false)},
  shiftLine:()=>{tool='brush';strokeStart([Math.floor(rnd()*64),Math.floor(rnd()*64)],{shiftKey:true},rnd()<.5)},
  op:()=>pick([opVolume,opShade,()=>opMirrorPart(pick(['rarm','larm','rleg','lleg'])),()=>opSymmetry(pick(['head','body'])),fillHoles])(),
  sel:()=>{sel=[Math.floor(rnd()*64),Math.floor(rnd()*64),Math.floor(rnd()*64),Math.floor(rnd()*64)];const w=Math.abs(sel[2]-sel[0])+1,h=Math.abs(sel[3]-sel[1])+1;if(w*h>400)sel[2]=sel[0];
    const c=rnd();if(c<.3){selCopy(false);selPlace([Math.floor(rnd()*60),Math.floor(rnd()*60)])}else if(c<.5)selCopy(true);else if(c<.7)selDelete();else selFlip();sel=null;pasting=false},
  reset:()=>{if(editCount())resetEdits()},
  undo:()=>undo(),redo:()=>redo(),
  newSkin:()=>freshSkin(),harm:()=>harmonize(),rand:()=>randomize(),
  pose:()=>setPose(pick(POSES)[0]),
  model:()=>set('model',pick(['classic','slim'])),
  figure:()=>set('figure',pick(OPT.figure)[0]),
  zoom:()=>setZoom(0.5+rnd()*4),
  hide:()=>{const k=pick(TREE.flat().filter(x=>typeof x==='string'&&!x.includes(' ')));hiddenParts.has(k)?hiddenParts.delete(k):hiddenParts.add(k);applyVisibility()},
  render:()=>{renderPNG(64,null)},
  lyAdd:()=>addLayer(),lyDup:()=>dupLayer(),lyMerge:()=>mergeDown(),lyDel:()=>delLayer(),lyMove:()=>moveLayer(rnd()<.5?1:-1),
  lyVis:()=>{pushHist('');L[Math.floor(rnd()*L.length)].v^=true;L.forEach(l=>l.v=!!l.v);syncE();update(true)},
  lyOp:()=>{pushHist('');L[AL].o=Math.round(rnd()*10)/10;syncE();update(true)},
  lySel:()=>{AL=Math.floor(rnd()*L.length);E=L[AL].E;syncE();save()},
  tpl:()=>applyTemplate(Math.floor(rnd()*100)),
  tryOn:()=>{previewTemplate(Math.floor(rnd()*100))},tryOff:()=>endPreview(),
  base:()=>baseSkin(rnd()<.5?'classic':'slim'),
  simple:()=>setSimple(rnd()<.5),
 };
 const names=Object.keys(A);
 for(let s=0;s<steps;s++){const name=pick(names);const before=J(),hb=hist.length;
   try{await A[name]()}catch(e){fails.push(s+' '+name+': исключение '+e.message);break}
   if(stroking){strokeEnd()}
   await new Promise(res=>requestAnimationFrame(()=>res()));
   const after=J();
   if(!sameE())fails.push(s+' '+name+': правки не совпадают с сохранёнными');
   if(lastFinal.length!==16384)fails.push(s+' '+name+': размер скина');
   if(!editCount()&&baseHoles().length)fails.push(s+' '+name+': дыры в основном слое без ручных правок ('+baseHoles().length+')');
   if(s%7===0&&!renderOK())fails.push(s+' '+name+': картинка скина не совпадает с состоянием');
   if(tplPrev<0&&(builtModel!==state.model||builtFigure!==state.figure))fails.push(s+' '+name+': модель на экране не та (руки/фигура)');
   try{const sv=JSON.parse(localStorage.getItem('mcskin.state.v1'));if(sv&&sv.hair!==state.hair)fails.push(s+' '+name+': сохранено не то, что на экране')}catch(e){}
   if(name!=='undo'&&name!=='redo'&&hist.length>hb&&after!==before){undo();if(J()!==before)fails.push(s+' '+name+': отмена вернула не то состояние');redo();if(J()!==after)fails.push(s+' '+name+': повтор вернул не то состояние')}
   log.push(name);if(fails.length>8)break}
 return {fails,steps:log.length,counts:log.reduce((a,n)=>(a[n]=(a[n]||0)+1,a),{})}}"""
with sync_playwright() as p:
    br = launch(p)
    pg = br.new_page(viewport={'width': 1400, 'height': 850}); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
    pg.goto(URL+'?nostart'); pg.wait_for_timeout(800)
    res = pg.evaluate(JS, {'steps': STEPS, 'seed': SEED})
    print(f"seed {SEED}: шагов {res['steps']}, ошибок {len(res['fails'])}, ошибок страницы {len(errs)}")
    for f in res['fails']: print('FAIL', f)
    for e in errs[:5]: print('PAGE', e[:300])
    br.close()
