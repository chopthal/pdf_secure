# PDF Secure — Windows 개발 환경 설정
# 사용법 (PowerShell, 프로젝트 루트에서):
#   .\scripts\setup-dev.ps1
#   .\.venv\Scripts\Activate.ps1
#   pytest

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

function Find-Python {
    $candidates = @(
        "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe"
    )
    foreach ($path in $candidates) {
        if (Test-Path $path) { return $path }
    }
    $cmd = Get-Command python -ErrorAction SilentlyContinue
    if ($cmd -and $cmd.Source -notmatch "WindowsApps") {
        return $cmd.Source
    }
    return $null
}

$python = Find-Python
if (-not $python) {
    Write-Host "Python이 없습니다. 설치 중..." -ForegroundColor Yellow
    winget install Python.Python.3.12 --accept-package-agreements --accept-source-agreements
    $python = Find-Python
    if (-not $python) {
        throw "Python 설치 후 터미널을 다시 열고 이 스크립트를 재실행하세요."
    }
}

Write-Host "Python: $python" -ForegroundColor Cyan
& $python --version

if (-not (Test-Path ".venv")) {
    Write-Host "가상환경 생성 (.venv)..." -ForegroundColor Cyan
    & $python -m venv .venv
}

$venvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -r requirements-dev.txt

Write-Host ""
Write-Host "설정 완료." -ForegroundColor Green
Write-Host "  활성화:  .\.venv\Scripts\Activate.ps1"
Write-Host "           (실행 정책 오류 시: Set-ExecutionPolicy -Scope CurrentUser RemoteSigned)"
Write-Host "  웹 서버:  `$env:AUTH_DISABLED='1'; .\.venv\Scripts\uvicorn.exe web.main:app --reload"
Write-Host "  테스트:  .\.venv\Scripts\python.exe -m pytest"
