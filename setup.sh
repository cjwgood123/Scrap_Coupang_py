#!/bin/bash
# 쿠팡 스크래퍼 초기 설정 스크립트
# 가상환경 생성 및 패키지 설치

echo "========================================"
echo "쿠팡 스크래퍼 초기 설정"
echo "========================================"
echo ""

# Python 설치 확인
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "[ERROR] Python이 설치되어 있지 않습니다."
    echo "[INFO] Python 3.7 이상을 설치해주세요."
    echo "[INFO] https://www.python.org/downloads/"
    exit 1
fi

# Python 버전 확인
echo "[INFO] Python 버전 확인 중..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
    python3 --version
else
    PYTHON_CMD=python
    python --version
fi
echo ""

# 가상환경이 이미 있는지 확인
if [ -f "venv/bin/activate" ] || [ -f "venv/Scripts/activate" ]; then
    echo "[INFO] 가상환경이 이미 존재합니다."
    echo "[INFO] 기존 가상환경을 사용합니다."
    echo ""
else
    echo "[INFO] 가상환경 생성 중..."
    $PYTHON_CMD -m venv venv
    if [ $? -ne 0 ]; then
        echo "[ERROR] 가상환경 생성 실패"
        exit 1
    fi
    echo "[SUCCESS] 가상환경 생성 완료"
    echo ""
fi

# 가상환경 활성화
echo "[INFO] 가상환경 활성화 중..."
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
elif [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
else
    echo "[ERROR] 가상환경 활성화 스크립트를 찾을 수 없습니다."
    exit 1
fi
echo "[SUCCESS] 가상환경 활성화 완료"
echo ""

# pip 업그레이드
echo "[INFO] pip 업그레이드 중..."
python -m pip install --upgrade pip
echo ""

# 패키지 설치
echo "[INFO] 필요한 패키지 설치 중..."
echo "[INFO] 이 작업은 몇 분 정도 걸릴 수 있습니다..."
echo ""
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "[ERROR] 패키지 설치 실패"
    echo "[TIP] 인터넷 연결을 확인하거나 sudo 권한이 필요할 수 있습니다."
    exit 1
fi
echo ""
echo "[SUCCESS] 패키지 설치 완료"
echo ""

# Chrome 브라우저 확인
echo "[INFO] Chrome 브라우저 확인 중..."
if command -v google-chrome &> /dev/null || command -v chromium-browser &> /dev/null || command -v chromium &> /dev/null; then
    echo "[SUCCESS] Chrome 브라우저 확인 완료"
    echo ""
else
    echo "[WARNING] Chrome 브라우저를 찾을 수 없습니다."
    echo "[INFO] Chrome 브라우저가 설치되어 있는지 확인하세요."
    echo "[INFO] Linux: sudo apt-get install google-chrome-stable"
    echo "[INFO] macOS: https://www.google.com/chrome/"
    echo ""
fi

echo "========================================"
echo "초기 설정 완료!"
echo "========================================"
echo ""
echo "[INFO] 이제 ./run.sh를 실행하여 스크래퍼를 시작할 수 있습니다."
echo ""

