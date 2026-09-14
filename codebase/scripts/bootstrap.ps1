# Bootstrap local dev environment for python-auto-data-profiling
$ErrorActionPreference = "Stop"
$Root = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
Set-Location $Root

Write-Host "Creating venv..."
python -m venv .venv
& "$Root\.venv\Scripts\Activate.ps1"

Write-Host "Installing dependencies..."
pip install -e ".[dev]"

Write-Host "Generating synthetic sample..."
python codebase/scripts/generate_sample.py

Write-Host "Running certification..."
python codebase/scripts/certify_profile_run.py

Write-Host "Running tests..."
pytest tests/ -q

Write-Host "Ruff check..."
ruff check codebase packages tests

Write-Host "Bootstrap complete."
