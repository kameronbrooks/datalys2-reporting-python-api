$ErrorActionPreference = "Stop"

Write-Host "Step 1: Updating Versions..." -ForegroundColor Cyan
try {
    python tools/update_versions.py
    if ($LASTEXITCODE -ne 0) { throw "Version update failed." }
    Write-Host "Versions updated successfully." -ForegroundColor Green
}
catch {
    Write-Error "Version update failed. Aborting build."
    exit 1
}

Write-Host "`nStep 2: Running Unit Tests..." -ForegroundColor Cyan
try {
    # Run unittest discovery on the tests directory
    python -m unittest discover tests
    if ($LASTEXITCODE -ne 0) { throw "Tests failed." }
    Write-Host "Tests passed successfully." -ForegroundColor Green
}
catch {
    Write-Error "Unit tests failed. Aborting build."
    exit 1
}

Write-Host "`nStep 3: Building the Project..." -ForegroundColor Cyan
try {
    # Clean previous builds
    if (Test-Path "dist") { Remove-Item "dist" -Recurse -Force }
    if (Test-Path "build") { Remove-Item "build" -Recurse -Force }
    
    # helper to ensure 'build' module is installed: pip install build
    python -m build
    if ($LASTEXITCODE -ne 0) { throw "Build failed." }
    Write-Host "Build completed successfully." -ForegroundColor Green
}
catch {
    Write-Error "Build failed. Aborting upload."
    exit 1
}

Write-Host "`nStep 4: Uploading to PyPI..." -ForegroundColor Cyan
try {
    # Upload specifically the newly created files in dist/
    # This requires 'twine' to be installed: pip install twine
    # --skip-existing: don't fail on files already published (e.g. partial re-runs)
    twine upload --skip-existing dist/*
    if ($LASTEXITCODE -ne 0) { throw "Upload failed." }
    Write-Host "Uploaded to PyPI successfully." -ForegroundColor Green
}
catch {
    Write-Error "Upload to PyPI failed."
    exit 1
}
