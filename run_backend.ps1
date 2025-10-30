# Windows quick run script for backend
# Usage: right-click -> Run with PowerShell (from project root)

.\venv\Scripts\Activate.ps1
uvicorn backend.main:app --reload --port 8000
