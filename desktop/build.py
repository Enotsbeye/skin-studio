"""Собирает настольное приложение «Скин-студия» (Neutralino.js) из skin-creator.html.

Результат: desktop/dist/SkinStudio-Windows.zip с одним SkinStudio.exe внутри
(ресурсы вшиты в exe), плюс Linux/macOS-бинарники для проверки.
"""
import json, os, re, shutil, subprocess, sys, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
# в репозитории приложение лежит рядом: ../index.html; при разработке — skin-creator.html
APP = os.environ.get('APP') or next(p for p in [os.path.join(HERE, '..', 'index.html'), '/home/claude/skin-creator.html'] if os.path.exists(p))
PROJ = os.path.join(HERE, '.app')        # рабочая папка Neutralino (создаётся сама)
OUT = os.path.join(HERE, 'dist')          # сюда кладётся готовый архив
_src = open(APP, encoding='utf-8').read()
_m = re.search(r"const APP_VERSION='([0-9.]+)'", _src)
VERSION = _m.group(1) if _m else (sys.argv[1] if len(sys.argv) > 1 else '1.0.0')  # номер версии — из самого приложения
PORT = 47815  # постоянный порт: от него зависит, где WebView2 хранит сохранённые данные (localStorage)
NL = '6.10.0'

res = PROJ + '/resources'
os.makedirs(res + '/js', exist_ok=True)
for f in os.listdir(res):  # чистим всё, кроме скачанной библиотеки neutralino.js
    p = os.path.join(res, f)
    if f != 'js': shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)

html = open(APP, encoding='utf-8').read()
# кусочки для сайта (установка с GitHub Pages) в программе не нужны
html = re.sub(r'\n<link rel="manifest"[^>]*>|\n<meta name="theme-color"[^>]*>|\n<link rel="(?:apple-touch-)?icon"[^>]*>', '', html)
html = re.sub(r"<script>if\('serviceWorker'.*?</script>\n?", '', html)
tag = '<script src="/js/neutralino.js"></script>'
assert '<head>' in html
html = html.replace('<head>', '<head>\n' + tag, 1)
open(res + '/index.html', 'w', encoding='utf-8').write(html)
shutil.copy(os.path.join(HERE, 'icon-256.png'), res + '/icon.png')

cfg = {
    "$schema": "https://raw.githubusercontent.com/neutralinojs/neutralinojs/main/schemas/neutralino.config.schema.json",
    "applicationId": "io.github.enotsbeye.skinstudio",
    "applicationName": "Скин-студия",
    "author": "Enotsbeye",
    "description": "Скин-студия — редактор скинов Minecraft",
    "version": VERSION,
    "defaultMode": "window",
    "port": PORT,
    "documentRoot": "/resources/",
    "url": "/",
    "enableServer": True,
    "enableNativeAPI": True,
    "tokenSecurity": "one-time",
    "dataLocation": "system",
    "logging": {"enabled": False, "writeToLogFile": False},
    "nativeAllowList": [
        "os.showSaveDialog", "os.getPath", "os.open",
        "filesystem.writeBinaryFile", "window.setTitle"
    ],
    "modes": {
        "window": {
            "title": "Скин-студия",
            "width": 1320, "height": 840, "minWidth": 980, "minHeight": 640,
            "center": True, "fullScreen": False, "alwaysOnTop": False,
            "icon": "/resources/icon.png",
            "enableInspector": False, "borderless": False, "maximize": False,
            "hidden": False, "resizable": True, "exitProcessOnClose": True,
            "useSavedState": True
        }
    },
    "cli": {
        "binaryName": "SkinStudio",
        "resourcesPath": "/resources/",
        "extensionsPath": "/extensions/",
        "clientLibrary": "/resources/js/neutralino.js",
        "binaryVersion": NL,
        "clientVersion": NL
    }
}
json.dump(cfg, open(PROJ + '/neutralino.config.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

if not os.path.exists(PROJ + '/bin/neutralino-win_x64.exe') or not os.path.exists(res + '/js/neutralino.js'):
    print('скачиваю Neutralino', NL, '(npm i -g @neutralinojs/neu, если команды neu нет)')
    subprocess.run(['neu', 'update'], cwd=PROJ, check=True)
shutil.rmtree(PROJ + '/dist', ignore_errors=True)
r = subprocess.run(['neu', 'build', '--release', '--embed-resources'], cwd=PROJ, capture_output=True, text=True)
log = r.stdout + r.stderr
if r.returncode:
    print(log); sys.exit(1)
d = PROJ + '/dist/SkinStudio'
print(sorted(os.listdir(d)))

out = OUT
os.makedirs(out, exist_ok=True)
readme = """Скин-студия — редактор скинов Minecraft (версия {v})

Как запустить:
1. Распакуй архив (правой кнопкой → «Извлечь всё»), не запускай прямо из архива.
2. Открой SkinStudio.exe.
3. Если Windows покажет синее окно «Система Windows защитила ваш компьютер» —
   нажми «Подробнее» → «Выполнить в любом случае». Так бывает с любой программой
   без платной цифровой подписи.

Твои скины и настройки хранятся в папке %APPDATA%\\SkinStudio.exe —
не переименовывай SkinStudio.exe, иначе программа начнёт с чистого листа.

Нужен Windows 10 или 11 (компонент WebView2 там уже стоит).

Не официальный продукт Minecraft. Не одобрен Mojang или Microsoft и не связан с ними.
NOT AN OFFICIAL MINECRAFT PRODUCT. NOT APPROVED BY OR ASSOCIATED WITH MOJANG OR MICROSOFT.

Программа сделана на Neutralino.js (MIT) — лицензии в THIRD-PARTY-NOTICES.txt.
""".format(v=VERSION)
zp = out + '/SkinStudio-Windows.zip'
with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED) as z:
    z.write(d + '/SkinStudio-win_x64.exe', 'SkinStudio/SkinStudio.exe')
    z.writestr('SkinStudio/README.txt', readme.replace('\n', '\r\n').encode('utf-8-sig'))
    z.write(os.path.join(HERE, 'THIRD-PARTY-NOTICES.txt'), 'SkinStudio/THIRD-PARTY-NOTICES.txt')
print('zip', zp, os.path.getsize(zp))
