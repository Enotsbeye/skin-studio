"""Общие пути для тестов: редактор — это index.html в корне репозитория.
Браузер: Chromium из Playwright (`playwright install chromium`) или свой Chrome через переменную CHROME."""
import os, pathlib
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
APP = os.path.join(ROOT, 'index.html')
URL = pathlib.Path(APP).as_uri()

def launch(p, **kw):
    exe = os.environ.get('CHROME')
    if exe:
        kw['executable_path'] = exe
    kw.setdefault('args', ['--no-sandbox'])
    return p.chromium.launch(**kw)
