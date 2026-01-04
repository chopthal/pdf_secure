#!/bin/bash
# macOS/Linux용 빌드 스크립트

echo "========================================"
echo "PDF 보안 처리 시스템 빌드 시작"
echo "========================================"

# PyInstaller 설치 확인
if ! python3 -m pip show pyinstaller &> /dev/null; then
    echo "PyInstaller가 설치되어 있지 않습니다. 설치 중..."
    python3 -m pip install pyinstaller
fi

# 기존 빌드 파일 정리
rm -rf build dist PDF보안처리.spec

echo ""
echo "실행 파일 생성 중..."
pyinstaller --onefile --windowed --name="PDF보안처리" --clean pdf_secure.py

if [ $? -ne 0 ]; then
    echo ""
    echo "빌드 실패!"
    exit 1
fi

echo ""
echo "========================================"
echo "빌드 완료!"
echo "========================================"
echo ""
echo "생성된 파일: dist/PDF보안처리"
echo ""

