# 빌드 가이드

## 자동 빌드 (GitHub Actions) - 권장

### 1. 태그 생성 및 푸시
```bash
git tag v2.0.0
git push origin v2.0.0
```

### 2. 빌드 확인
- GitHub 저장소의 **Actions** 탭에서 빌드 진행 상황 확인
- 빌드 완료 후 **Releases** 탭에서 다운로드

### 3. 결과물
- `PDF보안처리-macOS.zip`: 압축된 실행 파일
- GitHub Releases에 자동 업로드

---

## 로컬 빌드 (macOS)

### 사전 준비

#### 1. 가상환경 활성화
```bash
source pdf_secure/bin/activate
```

#### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 빌드 실행

#### 방법 1: 빌드 스크립트 사용 (권장)
```bash
chmod +x build.sh
./build.sh
```

#### 방법 2: 수동 빌드
```bash
pyinstaller --onefile --windowed --name="PDF보안처리" pdf_secure.py
```

### 빌드 결과

- **위치**: `dist/PDF보안처리`
- **크기**: 약 50-100MB
- **사용법**: 더블클릭으로 실행

---

## 빌드 옵션 설명

- `--onefile`: 단일 실행 파일로 패키징
- `--windowed`: 콘솔 창 없이 GUI만 표시
- `--name="PDF보안처리"`: 생성될 실행 파일 이름
- `--clean`: 이전 빌드 캐시 정리

---

## 빌드 후 테스트

1. **실행 파일 테스트**
   - `dist/` 폴더에서 실행 파일 실행
   - GUI가 정상적으로 표시되는지 확인
   - 파일 선택, 정보 입력, 처리 기능 테스트

2. **Gatekeeper 경고 확인**
   - macOS에서 실행 시 Gatekeeper 경고 가능
   - 시스템 설정에서 허용 필요

---

## 문제 해결

### 문제 1: "PyInstaller를 찾을 수 없습니다"
**해결**: `pip install pyinstaller`

### 문제 2: "모듈을 찾을 수 없습니다" 오류
**해결**: 
- 가상환경이 활성화되어 있는지 확인
- `pip install -r requirements.txt` 실행

### 문제 3: Gatekeeper 경고
**해결**: 
- 시스템 설정 > 보안 및 개인 정보 보호에서 허용
- 또는 터미널에서: `xattr -cr PDF보안처리`

### 문제 4: 실행 파일이 너무 큼
**해결**: 
- `--exclude-module` 옵션으로 불필요한 모듈 제외
- 예: `--exclude-module matplotlib --exclude-module numpy`

---

## 빌드 시간

- **첫 빌드**: 1-3분 (의존성 분석 포함)
- **이후 빌드**: 30초-1분 (캐시 사용)
- **GitHub Actions**: 약 3-5분

---

## 배포 준비

빌드 완료 후:

1. **실행 파일 확인**
   - `dist/` 폴더의 실행 파일 확인

2. **압축** (선택사항)
   ```bash
   cd dist
   zip -r PDF보안처리-macOS.zip PDF보안처리
   ```

3. **배포**
   - GitHub Releases에 업로드
   - 또는 직접 배포

---

## 다음 단계

빌드가 완료되면:
1. 실행 파일 테스트
2. GitHub Releases에 업로드
3. 사용자 가이드 작성
