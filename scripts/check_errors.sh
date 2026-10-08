#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
python_cmd=${PYTHON:-python3}
work_dir=$(mktemp -d)
trap 'rm -rf "$work_dir"' EXIT HUP INT TERM
for command in 'unknown' 'ls -z' 'ls a b' 'ls missing' \
    'cd a b' 'cd readme.txt' 'cd missing/..' 'cd "bad' \
    'pwd extra' 'date extra' 'uptime extra' 'conf-dump extra' \
    'exit extra' 'rm' 'rm missing' 'rm docs' 'rm -q readme.txt' \
    'rm -r /'; do
    printf '%s\n' "$command" 'conf-dump' > "$work_dir/error.txt"
    if "$python_cmd" -m src.main --vfs fixtures/multiple.json \
        --script "$work_dir/error.txt" </dev/null; then
        echo "Не получена ожидаемая ошибка: $command" >&2
        exit 1
    fi
done
if "$python_cmd" -m src.main --vfs fixtures/multiple.json \
    --script scripts/startup/stage5_cwd_error.txt </dev/null; then
    echo "Ожидалась ошибка удаления текущего каталога" >&2
    exit 1
fi
