#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
python_cmd=${PYTHON:-python3}
for vfs in minimal multiple deep; do
    "$python_cmd" -m src.main --vfs "fixtures/$vfs.json" \
        --script scripts/startup/stage3.txt </dev/null
done
