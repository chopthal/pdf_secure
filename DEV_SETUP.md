# 개발 환경 설정

로컬에서 `pytest` 및 웹 개발을 위한 환경 구성 가이드입니다.

## 요구 사항

- **Python 3.11+** (권장: 3.12)
- Windows: PowerShell

## 한 번에 설정 (Windows)

프로젝트 루트에서:

```powershell
.\scripts\setup-dev.ps1
```

Python이 없으면 스크립트가 `winget`으로 Python 3.12 설치를 시도합니다.

## 수동 설정

```powershell
# 1. 가상환경
python -m venv .venv

# 2. 활성화 (PowerShell)

```powershell
.\.venv\Scripts\Activate.ps1
```

**`PSSecurityException` / 실행 정책 오류**가 나면 아래 중 하나를 사용하세요.

```powershell
# A. 현재 사용자만 스크립트 허용 (권장, 한 번만)
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned

# B. 활성화 없이 venv 실행 파일 직접 사용 (가장 간단)
$env:AUTH_DISABLED = "1"
.\.venv\Scripts\uvicorn.exe web.main:app --reload
```

```powershell
# 3. 의존성
pip install -r requirements-dev.txt

# 4. 테스트
pytest
```

## 테스트 실행

| 명령 | 설명 |
|------|------|
| `pytest` | 전체 (Phase 1 + 2) |
| `pytest tests/web/` | 웹 레이어만 |
| `pytest tests/test_config.py` | Task 1 — 설정 |
| `pytest tests/test_fonts.py` | Task 2 — 폰트 |
| `pytest tests/test_watermark.py` | Task 3 — 워터마크 |
| `pytest tests/test_integration.py` | Task 4 — 연동 |
| `pytest -v` | 상세 출력 |

## 웹 서버 (Phase 2)

```powershell
$env:AUTH_DISABLED = "1"
.\.venv\Scripts\uvicorn.exe web.main:app --reload
```

`Activate.ps1`이 막히면 위처럼 **venv 경로를 직접** 쓰면 됩니다. 브라우저: http://127.0.0.1:8000

운영 시 `.env.example` · [DEPLOY.md](DEPLOY.md) 참고.

## 디렉터리

```
.venv/              # 가상환경 (git 제외)
assets/fonts/       # 나눔고딕 번들 (테스트·배포 공용)
core/               # PDF 처리 핵심 로직
tests/              # 단위 테스트
scripts/setup-dev.ps1
```

## 환경 변수 (선택)

| 변수 | 용도 |
|------|------|
| `PDF_SECURE_FONT_PATH` | 워터마크 폰트 TTF 경로 오버라이드 |

## CI

`git push` 시 GitHub Actions `.github/workflows/test.yml`에서 동일한 `pytest`가 실행됩니다.

## 문제 해결

### `python`이 Microsoft Store로만 연결됨

[python.org](https://www.python.org/downloads/)에서 설치하거나:

```powershell
winget install Python.Python.3.12
```

설치 시 **"Add python.exe to PATH"** 를 체크하세요.

### PowerShell에서 스크립트 실행 거부

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

### 가상환경 활성화 후에도 pytest 없음

```powershell
.\.venv\Scripts\python.exe -m pytest
```
