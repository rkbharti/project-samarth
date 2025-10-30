# Windows quick start
# Usage: right-click -> Run with PowerShell (from project root)

Write-Host "[1/4] Creating venv" -ForegroundColor Cyan
python -m venv venv

Write-Host "[2/4] Activating venv" -ForegroundColor Cyan
.\venv\Scripts\Activate.ps1

Write-Host "[3/4] Installing dependencies" -ForegroundColor Cyan
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt -c constraints.txt --upgrade

Write-Host "[4/4] Building vectorstore (can take 1-3 min)" -ForegroundColor Cyan
python scripts/setup_data.py

Write-Host "Done. Start backend with: uvicorn backend.main:app --reload --port 8000" -ForegroundColor Green
