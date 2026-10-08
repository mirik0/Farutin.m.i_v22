#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
python_cmd=${PYTHON:-python3}
for stage in stage4 stage5 stage5_relative; do
    "$python_cmd" -m src.main --vfs fixtures/multiple.json \
        --script "scripts/startup/$stage.txt" </dev/null
done
"$python_cmd" -m src.main --vfs fixtures/deep.json \
    --script scripts/startup/stage4_deep.txt </dev/null
