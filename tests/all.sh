#!/usr/bin/env bash
# Все автотесты редактора. Нужно: pip install playwright && playwright install chromium
# Свой Chrome вместо Chromium: CHROME=/путь/к/chrome ./tests/all.sh
cd "$(dirname "$0")/.."
for t in check bounds parts compat cloud_check imports extra layers; do
  python3 tests/$t.py 2>&1 | grep -E "Error:|Traceback|FAIL|Итого|^OK   (все|облач)|рендеров|^импорт|^доп|^слои"
done
python3 tests/desktop.py 2>&1 | grep -E "FAIL|^приложение"
python3 tests/pwa.py 2>&1 | grep -E "FAIL|^сайт"
for seed in 11 12; do python3 tests/fuzz.py 250 $seed 2>&1 | tail -1; done
