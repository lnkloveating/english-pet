#!/usr/bin/env sh
set -eu

repo_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$repo_root"

python -m compileall -q shared/python agent/src app/backend/src pet_pipeline/src
python -m ruff check shared/python agent app/backend pet_pipeline
python -m pytest agent/tests app/backend/tests pet_pipeline/tests
cd app/mobile
npm run typecheck
