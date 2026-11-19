"""Каждая деталь должна менять только свои части тела, и ничего не должно попадать в неиспользуемые области."""
import os, sys, pathlib, tempfile; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from env import APP, URL, launch
INSTR = os.path.join(tempfile.gettempdir(), 'instr.html')
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    br = launch(p)
    pg = br.new_page(); pg.goto(URL+'?nostart'); pg.wait_for_timeout(700)
    out = pg.evaluate("""()=>{const NAMES=['head','hat','body','jacket','rarm','rsleeve','larm','lsleeve','rleg','rpants','lleg','lpants'];const res=[];
      const allow={face:['head','hat'],eyes:['head'],brows:['head'],mouth:['head'],cheeks:['head'],beard:['head','jacket'],hair:['head','hat','jacket','rpants','lpants'],
        shoes:['rleg','lleg','rpants','lpants'],bottom:['rleg','lleg','rpants','lpants','body','jacket'],hairDye:['head','hat','jacket','rpants','lpants']};
      const accAllow={glasses:['hat'],sunglasses:['hat'],cap:['hat'],beanie:['hat'],headband:['hat'],crown:['hat'],headphones:['hat'],mask:['hat'],scarf:['jacket','body'],backpack:['jacket'],gloves:['rarm','larm'],
        helmet:['hat'],gasmask:['hat'],balaclava:['hat'],platecarrier:['jacket'],chestrig:['jacket'],patches:['rsleeve','lsleeve'],fingerless:['rarm','larm'],kneepads:['rpants','lpants'],catears:['hat'],horns:['hat']};
      for(const m of ['classic','slim']){const M=rmap(m==='slim');
        const base=Object.assign(clone(DEFAULT),{model:m,acc:[],hair:'bald',beard:'none',clothes3d:'flat'});
        const diffParts=(a,b)=>{const s=new Set();let stray=0;for(let i=0;i<4096;i++){const j=i*4;if(a[j]!==b[j]||a[j+1]!==b[j+1]||a[j+2]!==b[j+2]||a[j+3]!==b[j+3]){if(M.p[i]<0)stray++;else s.add(NAMES[M.p[i]])}}return [s,stray]};
        const check=(label,st,allowed)=>{const a=paint(base),b=paint(st);const [s,stray]=diffParts(a,b);const bad=[...s].filter(x=>!allowed.includes(x));if(bad.length||stray)res.push(m+' '+label+': лишние части '+bad.join(',')+(stray?' / в пустой области '+stray:''))};
        for(const k of ['eyes','brows','mouth','cheeks','beard','hair','shoes','bottom'])for(const [v] of OPT[k])check(k+'='+v,Object.assign({},base,{[k]:v}),allow[k]);
        for(const [v] of OPT.hairDye)check('hairDye='+v,Object.assign({},base,{hair:'long',hairDye:v}),allow.hairDye.concat([]));
        for(const [a] of OPT.acc)check('acc='+a,Object.assign({},base,{acc:[a]}),accAllow[a]);
        // stray pixels for every full combination
        for(const [t] of OPT.top){const d=paint(Object.assign({},base,{top:t,clothes3d:'3d',figure:'gendermod'}));let st=0;for(let i=0;i<4096;i++)if(M.p[i]<0&&d[i*4+3])st++;if(st)res.push(m+' top='+t+': в пустой области '+st)}
      }return res}""")
    print('\n'.join('FAIL ' + x for x in out) if out else 'OK   все детали меняют только свои части')
    br.close()
