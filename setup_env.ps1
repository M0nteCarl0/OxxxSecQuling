# ==============================================================================
# Quick Environment Setup for Qiling Framework (Windows PowerShell)
# ==============================================================================

[CmdletBinding()]
param (
    [string]$VenvPath = ".venv"
)

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " 🚀 Qiling Framework Environment Quick Setup" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# 1. Check Python installation
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Host "[-] Python is not found in PATH! Please install Python 3.8-3.12." -ForegroundColor Red
    exit 1
}

$pyVersion = python --version
Write-Host "[+] Found: $pyVersion" -ForegroundColor Green

# 2. Configure TEMP directories to prevent disk space exhaustion
if (-not (Test-Path "D:\Temp")) {
    New-Item -ItemType Directory -Path "D:\Temp" -Force | Out-Null
}
$env:TEMP = "D:\Temp"
$env:TMP = "D:\Temp"

# 3. Create virtual environment if it doesn't exist
if (-not (Test-Path $VenvPath)) {
    Write-Host "[*] Creating virtual environment at '$VenvPath'..." -ForegroundColor Yellow
    python -m venv $VenvPath
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[-] Failed to create virtual environment!" -ForegroundColor Red
        exit 1
    }
    Write-Host "[+] Virtual environment created successfully." -ForegroundColor Green
} else {
    Write-Host "[+] Virtual environment '$VenvPath' already exists." -ForegroundColor Green
}

$venvPython = Join-Path $VenvPath "Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    Write-Host "[-] Virtualenv python executable not found at: $venvPython" -ForegroundColor Red
    exit 1
}

# 4. Install / Update dependencies
Write-Host "[*] Installing dependencies from requirements.txt..." -ForegroundColor Yellow
& $venvPython -m pip install --no-cache-dir -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "[-] Dependency installation encountered errors!" -ForegroundColor Red
    exit 1
}
Write-Host "[+] All dependencies installed successfully!" -ForegroundColor Green

# 5. Run verification script
Write-Host "[*] Running environment verification..." -ForegroundColor Yellow
& $venvPython verify_all.py

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " [OK] Environment setup completed!" -ForegroundColor Green
Write-Host " To activate the environment in PowerShell, run:" -ForegroundColor White
Write-Host "    .\$VenvPath\Scripts\Activate.ps1"
Write-Host "============================================================" -ForegroundColor Cyan
