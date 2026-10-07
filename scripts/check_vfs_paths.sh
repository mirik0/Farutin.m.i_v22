#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
python_cmd=${PYTHON:-python3}
for vfs in minimal multiple deep; do
    "$python_cmd" -m src.main --vfs "fixtures/$vfs.json" \
        --script scripts/startup/stage3.txt </dev/null
done
"$python_cmd" -m src.main --vfs fixtures/multiple.json \
    --script scripts/startup/stage3_quotes.txt </dev/null
if "$python_cmd" -m src.main --vfs fixtures/multiple.json \
    --script scripts/startup/stage3_error.txt </dev/null; then
    echo "Ожидалась ошибка аргументов cd" >&2
    exit 1
fi
