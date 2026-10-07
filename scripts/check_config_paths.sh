#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
python_cmd=${PYTHON:-python3}
"$python_cmd" -m src.main --vfs fixtures/deep.json \
    --script scripts/startup/stage2.txt </dev/null
"$python_cmd" -m src.main --vfs fixtures/minimal.json </dev/null
if "$python_cmd" -m src.main --vfs fixtures/deep.json \
    --script scripts/startup/absent.txt </dev/null; then
    echo "Ожидалась ошибка отсутствующего скрипта" >&2
    exit 1
fi
