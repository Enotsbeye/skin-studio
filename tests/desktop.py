# Проверка настольной сборки: запускает Linux-версию того же приложения (те же вшитые ресурсы и настройки,
import os, sys, pathlib, tempfile; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from env import APP, URL, launch
INSTR = os.path.join(tempfile.gettempdir(), 'instr.html')
# что и в SkinStudio.exe) в режиме сервера и открывает её в Chrome. Проверяет, что мост к системе поднимается,
# сохранение пишет настоящий файл на диск, а приложение работает без ошибок.
import subprocess, time, os, json, tempfile, shutil
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
BIN = next((p for p in [os.path.join(HERE, '..', 'desktop', '.app', 'dist', 'SkinStudio', 'SkinStudio-linux_x64'), os.path.join(HERE, '..', 'desktop', 'build', '.app', 'dist', 'SkinStudio', 'SkinStudio-linux_x64')] if os.path.exists(p)), None)
if not BIN:
    print('приложение: нет сборки — сначала python3 desktop/build.py'); raise SystemExit
PORT = 47815
work = tempfile.mkdtemp()
shutil.copy(BIN, work + '/SkinStudio')
proc = subprocess.Popen([work + '/SkinStudio', '--mode=cloud'], cwd=work, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
res = []
try:
    import urllib.request
    for _ in range(50):
        try:
            urllib.request.urlopen(f'http://127.0.0.1:{PORT}/', timeout=1).read(); break
        except Exception:
            time.sleep(0.2)
    with sync_playwright() as p:
        b = launch(p)
        pg = b.new_page(viewport={'width': 1320, 'height': 840}, accept_downloads=True)
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(f'http://127.0.0.1:{PORT}/'); pg.wait_for_timeout(1500)
        r = pg.evaluate("()=>[!!NAT, typeof NL_PORT, NL_OS, document.documentElement.classList.contains('native')]")
        res.append(('мост к системе поднят (NAT, NL_PORT, класс native)', r[0] and r[1] == 'number' and r[3], r))
        out = os.path.join(work, 'out')
        os.makedirs(out)
        # окно «Сохранить как» в серверном режиме не открыть — подменяем только его, запись идёт настоящим API
        pg.evaluate(f"""()=>{{window._dlg=[];NAT.os.showSaveDialog=async(t,o)=>{{window._dlg.push([t,o.defaultPath]);return {json.dumps(out)}+'/мой скин'}}}}""")
        pg.evaluate("()=>{document.querySelector('.modal')&&closeModal();applyTemplate(3);update(true)}")
        pg.evaluate("()=>downloadSkin()"); pg.wait_for_timeout(800)
        f = os.path.join(out, 'мой скин.png')
        ok = os.path.exists(f) and open(f, 'rb').read(8) == b'\x89PNG\r\n\x1a\n'
        same = False
        if ok:
            from PIL import Image
            im = Image.open(f); same = im.size == (64, 64) and im.mode in ('RGBA', 'P', 'RGB')
        res.append(('«Скачать скин» пишет настоящий PNG 64×64 и дописывает .png', ok and same, os.listdir(out)))
        t = pg.evaluate("()=>document.querySelector('#toast').textContent")
        res.append(('после сохранения — кнопка «Показать в папке»', 'Показать в папке' in t, t))
        pg.evaluate("()=>saveProject()"); pg.wait_for_timeout(800)
        pj = [x for x in os.listdir(out) if x.endswith('.json')]
        okp = bool(pj) and json.load(open(os.path.join(out, pj[0]), encoding='utf-8')).get('app') == 'skin-studio'
        res.append(('«Сохранить проект» пишет .json', okp, os.listdir(out)))
        d = pg.evaluate("()=>window._dlg")
        res.append(('второе сохранение предлагает ту же папку', len(d) >= 2 and d[1][1].startswith(out), d))
        pg.evaluate("()=>{NAT.os.showSaveDialog=async()=>''}")
        pg.evaluate("()=>downloadSkin()"); pg.wait_for_timeout(500)
        t = pg.evaluate("()=>document.querySelector('#toast').textContent")
        res.append(('отмена окна сохранения — без ошибки', 'отменено' in t, t))
        # данные переживают перезапуск страницы (тот же порт → то же хранилище)
        pg.evaluate("()=>{state.name='Проверка';save()}")
        pg.reload(); pg.wait_for_timeout(1200)
        r = pg.evaluate("()=>[state.name,!!NAT]")
        res.append(('после перезагрузки окна: данные на месте и мост снова работает', r == ['Проверка', True], r))
        cm = pg.evaluate("()=>{const e=new MouseEvent('contextmenu',{bubbles:true,cancelable:true});document.querySelector('.topbar,header,body').dispatchEvent(e);return e.defaultPrevented}")
        res.append(('меню браузера по правой кнопке скрыто', cm, cm))
        pg2 = b.new_page(); e2 = []; pg2.on('pageerror', lambda e: e2.append(str(e)))
        pg2.goto(f'http://127.0.0.1:{PORT}/'); pg2.wait_for_timeout(1500)
        r = pg2.evaluate("()=>[!!document.querySelector('#stage'), !!NAT, document.body.innerText.includes('NE_CL'), typeof applyTemplate]")
        res.append(('если связь с системой не поднялась — страница цела, работает как обычно', r == [True, False, False, 'function'], r))
        pg2.close()
        r = pg.evaluate("""async()=>{const of=window.fetch;const answer=v=>window.fetch=async()=>({ok:true,json:async()=>v});
          answer({version:'9.9.9',url:'https://evil.example/x',notes:'тест'});let opened=null;NAT.os.open=u=>{opened=u;return Promise.resolve()};
          await checkUpdate(true);const t1=document.querySelector('#toast').textContent;document.querySelector('#toast button').click();
          answer({version:NL_APPVERSION});await checkUpdate(true);const t2=document.querySelector('#toast').textContent;
          window.fetch=async()=>{throw new Error('offline')};await checkUpdate(true);const t3=document.querySelector('#toast').textContent;window.fetch=of;
          return [NL_APPVERSION,t1.includes('9.9.9')&&t1.includes('Скачать'),opened,t2.includes('последняя'),t3.includes('Не получилось')]}""")
        res.append(('проверка обновлений: новая версия, ссылка только на релизы проекта, «последняя», без интернета', r[1] and r[2]=='https://github.com/Enotsbeye/skin-studio/releases/latest' and r[3] and r[4], r))
        res.append(('нет ошибок страницы', not errs, errs[:3]))
        b.close()
finally:
    proc.terminate()
    try: proc.wait(3)
    except Exception: proc.kill()
    log = proc.stdout.read().decode('utf-8', 'replace')
ok = 0
for n, v, *x in res:
    print('OK  ' if v else 'FAIL', n, '' if v else x)
    ok += bool(v)
print(f'приложение: {ok} из {len(res)}')
if ok < len(res): print(log[-1500:])
