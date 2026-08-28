$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
Push-Location $repoRoot
try {
    python -m compileall -q shared/python agent/src app/backend/src pet_pipeline/src
    python -m ruff check shared/python agent app/backend pet_pipeline
    python -m pytest agent/tests app/backend/tests pet_pipeline/tests
    Push-Location app/mobile
    try {
        npm run typecheck
    }
    finally {
        Pop-Location
    }
}
finally {
    Pop-Location
}
