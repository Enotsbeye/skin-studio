"""Проверка границ: каждая функция рисования должна попадать в свою грань развёртки."""
import os, sys, pathlib, tempfile; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from env import APP, URL, launch
INSTR = os.path.join(tempfile.gettempdir(), 'instr.html')
import re, sys
from playwright.sync_api import sync_playwright
src = open(APP, encoding='utf-8').read()
CHK = r"""window.__V={};function __chk(ok,what){if(!ok){const st=(new Error().stack||'').split('\n').slice(2,4).map(s=>{const m=s.match(/:(\d+):\d+\)?$/);return m?m[1]:'?'}).join('<');const k=what+' line '+st;window.__V[k]=(window.__V[k]||0)+1}}
const band=(p,r0,r1,c,n)=>{__chk(r0>=0&&r1<=p.h&&r0<r1,'band');rect(p.u,p.v+p.d+r0,2*(p.d+p.w),r1-r0,c,n)};
const capT=(p,c,n)=>rect(p.u+p.d,p.v,p.w,p.d,c,n);
const capB=(p,c,n)=>rect(p.u+p.d+p.w,p.v,p.w,p.d,c,n);
const F=(p,x,y,c,n)=>{__chk(x>=0&&x<p.w&&y>=0&&y<p.h,'F(front px)');put(p.u+p.d+x,p.v+p.d+y,c,n)};
const Fr=(p,x,y,w,h,c,n)=>{__chk(x>=0&&y>=0&&x+w<=p.w&&y+h<=p.h,'Fr(front rect)');rect(p.u+p.d+x,p.v+p.d+y,w,h,c,n)};
const Fclr=(p,x,y,w,h)=>{__chk(x>=0&&y>=0&&x+w<=p.w&&y+h<=p.h,'Fclr');for(let j=0;j<h;j++)for(let i=0;i<w;i++)clr(p.u+p.d+x+i,p.v+p.d+y+j)};
const Bk=(p,x,y,c,n)=>{__chk(x>=0&&x<p.w&&y>=0&&y<p.h,'Bk(back px)');put(p.u+2*p.d+p.w+x,p.v+p.d+y,c,n)};
const Bkr=(p,x,y,w,h,c,n)=>{__chk(x>=0&&y>=0&&x+w<=p.w&&y+h<=p.h,'Bkr(back rect)');rect(p.u+2*p.d+p.w+x,p.v+p.d+y,w,h,c,n)};
const S=(p,x,y,c,n)=>{__chk(x>=0&&x<2*(p.d+p.w)&&y>=0&&y<p.h,'S(strip px)');put(p.u+x,p.v+p.d+y,c,n)};
const T=(p,x,z,c,n)=>{__chk(x>=0&&x<p.w&&z>=0&&z<p.d,'T(top px)');put(p.u+p.d+x,p.v+z,c,n)};
const sideR=(p,x,y,w,h,c,n)=>{__chk(x>=0&&y>=0&&x+w<=p.d&&y+h<=p.h,'sideR');rect(p.u+x,p.v+p.d+y,w,h,c,n)};
const sideL=(p,x,y,w,h,c,n)=>{__chk(x>=0&&y>=0&&x+w<=p.d&&y+h<=p.h,'sideL');rect(p.u+p.d+p.w+x,p.v+p.d+y,w,h,c,n)};
const sidesBack=(p,r0,r1,c,n)=>{__chk(r0>=0&&r1<=p.h,'sidesBack');rect(p.u,p.v+p.d+r0,p.d,r1-r0,c,n);rect(p.u+p.d+p.w,p.v+p.d+r0,p.d+p.w,r1-r0,c,n)};"""
a = src.index('const band=('); b = src.index('const pts=(')
# keep line count identical so reported line numbers match the real file
orig_lines = src[a:b].count('\n')
chk = CHK.replace('\n', ' ') + '\n' * orig_lines
inst = src[:a] + chk + src[b:]
open(INSTR, 'w', encoding='utf-8').write(inst)
lines = src.split('\n')
with sync_playwright() as p:
    br = launch(p)
    pg = br.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(pathlib.Path(INSTR).as_uri()+'?nostart'); pg.wait_for_timeout(800)
    n = pg.evaluate("""()=>{let n=0;const keys=Object.keys(OPT).filter(k=>!['acc','pattern'].includes(k));
      const eyes=OPT.eyes.map(o=>o[0]),hairs=OPT.hair.map(o=>o[0]);
      for(const m of ['classic','slim']){
        for(const k of keys)for(const [v] of OPT[k])for(const f of ['male','female3d','gendermod'])for(const c of ['3d','flat']){paint(Object.assign({},state,{[k]:v,model:m,figure:f,clothes3d:c}));n++}
        for(const e of eyes)for(const h of hairs){paint(Object.assign({},state,{eyes:e,hair:h,model:m}));n++}
        for(const e of eyes)for(const [a] of OPT.acc){paint(Object.assign({},state,{eyes:e,acc:[a],model:m}));n++}
        for(const [t] of OPT.top)for(const [bt] of OPT.bottom)for(const [pt] of OPT.pattern){paint(Object.assign({},state,{top:t,bottom:bt,topPattern:pt,bottomPattern:pt,model:m}));n++}
        for(const e of eyes)for(const [mo] of OPT.mouth)for(const [bd] of OPT.beard)for(const [ch] of OPT.cheeks){paint(Object.assign({},state,{eyes:e,mouth:mo,beard:bd,cheeks:ch,model:m}));n++}
      }return n}""")
    v = pg.evaluate("window.__V")
    print('рендеров:', n, 'ошибок страницы:', errs[:3])
    if not v: print('OK   все функции рисования попадают в свои грани')
    for k, cnt in sorted(v.items(), key=lambda x: -x[1]):
        m = re.search(r'line (\d+)', k); ln = int(m.group(1)) if m else 0
        print(f'FAIL {k}  x{cnt}\n     {lines[ln-1].strip()[:220] if ln else ""}')
    br.close()
