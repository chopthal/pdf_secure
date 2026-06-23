# Railway 배포 가이드 (Phase 3)

PDF 보안 처리 웹앱을 Railway + Supabase로 배포하는 방법입니다.

## 아키텍처

```
[브라우저] ──HTTPS──▶ [Railway Docker]
                         ├── FastAPI (uvicorn)
                         ├── /tmp/pdf_secure (임시 PDF)
                         └── Supabase Auth (JWT)
```

## 사전 준비

1. [Railway](https://railway.com) 계정 (Hobby $5/월)
2. [Supabase](https://supabase.com) 프로젝트
3. GitHub 저장소 연결 (`chopthal/pdf_secure`)

---

## 1. Supabase 설정

### 1.1 프로젝트 생성

Supabase 대시보드 → New project

### 1.2 Auth 사용자 추가

Authentication → Users → Add user (팀원 이메일·비밀번호)

Google OAuth를 쓰려면 Authentication → Providers에서 Google 활성화.

### 1.3 API 키 확인

Project Settings → API:

| 값 | Railway 환경 변수 |
|----|-------------------|
| Project URL | `SUPABASE_URL` |
| anon public | `SUPABASE_ANON_KEY` |
| JWT Secret | `SUPABASE_JWT_SECRET` |

`SUPABASE_JWT_SECRET`은 **JWT Secret** (Settings → API → JWT Settings).

---

## 2. Railway 배포

### 2.1 새 프로젝트

1. Railway → New Project → **Deploy from GitHub repo**
2. `pdf_secure` 저장소 선택
3. 브랜치: `web-phase3-deploy` (또는 `master`)

### 2.2 빌드 설정

저장소에 포함된 파일을 사용합니다:

- `Dockerfile`
- `railway.toml` (헬스체크 `/health`)

Railway가 Dockerfile을 자동 감지합니다.

### 2.3 환경 변수

Railway → Service → Variables:

| 변수 | 필수 | 예시 |
|------|------|------|
| `SUPABASE_URL` | ✅ | `https://xxxx.supabase.co` |
| `SUPABASE_ANON_KEY` | ✅ | `eyJhbG...` |
| `SUPABASE_JWT_SECRET` | ✅ | JWT Secret |
| `COOKIE_SECURE` | ✅ | `1` (HTTPS 쿠키) |
| `AUTH_DISABLED` | ❌ | 설정하지 않음 (운영) |
| `PDF_SECURE_TEMP_ROOT` | ❌ | 기본 `/tmp/pdf_secure` |
| `JOB_RETENTION_SECONDS` | ❌ | `3600` |
| `CLEANUP_INTERVAL_SECONDS` | ❌ | `300` |
| `MAX_UPLOAD_BYTES` | ❌ | `104857600` |

`PORT`는 Railway가 자동 주입합니다.

### 2.4 도메인

Settings → Networking → Generate Domain  
→ `https://your-app.up.railway.app`

HTTPS는 Railway가 자동 제공합니다.

### 2.5 헬스체크

배포 후 확인:

```bash
curl https://your-app.up.railway.app/health
# {"status":"ok"}
```

---

## 3. 배포 후 테스트

1. `/login` — Supabase 계정으로 로그인
2. PDF 업로드 → 처리 → 다운로드
3. PDF 뷰어에서 워터마크·비밀번호 확인

### 대용량 PDF (200페이지)

로컬에서:

```powershell
pytest -m slow tests/test_large_pdf.py
```

---

## 4. 로컬 Docker 테스트

Docker Desktop 설치 후:

```powershell
docker build -t pdf-secure .
docker run --rm -p 8000:8000 -e AUTH_DISABLED=1 pdf-secure
```

http://127.0.0.1:8000/health

---

## 5. 문제 해결

| 증상 | 원인 | 해결 |
|------|------|------|
| 앱 시작 실패 | Supabase env 누락 | Variables 확인, `AUTH_DISABLED` 제거 |
| 로그인 후 바로 로그아웃 | `COOKIE_SECURE=0` on HTTPS | `COOKIE_SECURE=1` |
| 502 / 헬스체크 실패 | 빌드·포트 오류 | Deploy logs, `PORT` 확인 |
| PDF 처리 OOM | 메모리 부족 | Railway 플랜 업그레이드 또는 PDF 크기 제한 |

---

## 6. 비용 (참고)

- Railway Hobby: ~$5/월
- Supabase Free tier: 소규모 Auth·DB 무료
- 주간 ~10건 사용 시 추가 비용 거의 없음

---

## 7. 관련 파일

| 파일 | 역할 |
|------|------|
| `Dockerfile` | 컨테이너 이미지 |
| `requirements-prod.txt` | 운영 의존성 |
| `railway.toml` | Railway 설정 |
| `.env.example` | 환경 변수 템플릿 |
