#!/bin/bash
# 쿠팡 스크래퍼 실행 스크립트

# 가상환경 활성화 (Windows Git Bash용)
if [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
elif [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# Python 실행
python coupang_scraper_final.py