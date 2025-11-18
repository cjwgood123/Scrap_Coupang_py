@echo off
REM 쿠팡 스크래퍼 실행 스크립트 (Windows용)

REM 가상환경 활성화
call venv\Scripts\activate.bat

REM Python 실행
python coupang_scraper_final.py

pause