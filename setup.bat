@echo off
REM 쿠팡 스크래퍼 초기 설정 스크립트 (Windows용)
REM 가상환경 생성 및 패키지 설치

echo ========================================
echo 쿠팡 스크래퍼 초기 설정
echo ========================================
echo.

REM Python 설치 확인 (여러 방법 시도)
set PYTHON_CMD=
python --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python
    goto :python_found
)

py -3 --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=py -3
    goto :python_found
)

python3 --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python3
    goto :python_found
)

REM Python을 찾을 수 없음
echo [ERROR] Python을 찾을 수 없습니다.
echo [INFO] Python 3.7 이상을 설치해주세요.
echo [INFO] https://www.python.org/downloads/
echo.
echo [TIP] Python 설치 후 다음을 확인하세요:
echo   1. Python 설치 시 "Add Python to PATH" 옵션 체크
echo   2. 명령 프롬프트를 재시작
echo   3. python --version 명령어로 확인
echo.
pause
exit /b 1

:python_found

echo [INFO] Python 버전 확인 중...
%PYTHON_CMD% --version
echo.

REM 가상환경이 이미 있는지 확인
if exist "venv\Scripts\activate.bat" (
    echo [INFO] 가상환경이 이미 존재합니다.
    echo [INFO] 기존 가상환경을 사용합니다.
    echo.
) else (
    echo [INFO] 가상환경 생성 중...
    %PYTHON_CMD% -m venv venv
    if errorlevel 1 (
        echo [ERROR] 가상환경 생성 실패
        pause
        exit /b 1
    )
    echo [SUCCESS] 가상환경 생성 완료
    echo.
)

REM 가상환경 활성화
echo [INFO] 가상환경 활성화 중...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] 가상환경 활성화 실패
    pause
    exit /b 1
)
echo [SUCCESS] 가상환경 활성화 완료
echo.

REM pip 업그레이드
echo [INFO] pip 업그레이드 중...
%PYTHON_CMD% -m pip install --upgrade pip
echo.

REM 패키지 설치
echo [INFO] 필요한 패키지 설치 중...
echo [INFO] 이 작업은 몇 분 정도 걸릴 수 있습니다...
echo.
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] 패키지 설치 실패
    echo [TIP] 인터넷 연결을 확인하거나 관리자 권한으로 실행해보세요.
    pause
    exit /b 1
)
echo.
echo [SUCCESS] 패키지 설치 완료
echo.

REM Chrome 브라우저 확인
echo [INFO] Chrome 브라우저 확인 중...
where chrome >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Chrome 브라우저를 찾을 수 없습니다.
    echo [INFO] Chrome 브라우저가 설치되어 있는지 확인하세요.
    echo [INFO] 일반적인 설치 경로:
    echo [INFO]   C:\Program Files\Google\Chrome\Application\chrome.exe
    echo [INFO]   C:\Program Files (x86)\Google\Chrome\Application\chrome.exe
    echo.
) else (
    echo [SUCCESS] Chrome 브라우저 확인 완료
    echo.
)

echo ========================================
echo 초기 설정 완료!
echo ========================================
echo.
echo [INFO] 이제 run.bat을 실행하여 스크래퍼를 시작할 수 있습니다.
echo.
pause

