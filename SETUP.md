# 쿠팡 스크래퍼 설치 및 실행 가이드

## 📋 사전 요구사항

1. **Python 3.7 이상**
   - [Python 공식 사이트](https://www.python.org/downloads/)에서 다운로드
   - 설치 시 "Add Python to PATH" 옵션 체크

2. **Google Chrome 브라우저**
   - [Chrome 다운로드](https://www.google.com/chrome/)
   - Chrome이 설치되어 있어야 합니다.

3. **인터넷 연결**
   - 패키지 다운로드 및 스크래핑에 필요합니다.

---

## 🚀 빠른 시작 (Windows)

### 1단계: 초기 설정 (처음 한 번만)

```cmd
setup.bat
```

이 명령어는 다음을 자동으로 수행합니다:
- 가상환경 생성
- 필요한 패키지 설치 (selenium, undetected-chromedriver 등)

### 2단계: 스크래퍼 실행

```cmd
run.bat
```

---

## 🚀 빠른 시작 (Linux/macOS/Git Bash)

### 1단계: 초기 설정 (처음 한 번만)

```bash
chmod +x setup.sh
./setup.sh
```

### 2단계: 스크래퍼 실행

```bash
chmod +x run.sh
./run.sh
```

---

## 📦 수동 설치 방법

### 1. 가상환경 생성

**Windows:**
```cmd
python -m venv venv
```

**Linux/macOS:**
```bash
python3 -m venv venv
```

### 2. 가상환경 활성화

**Windows CMD:**
```cmd
venv\Scripts\activate.bat
```

**Windows PowerShell:**
```powershell
.\venv\Scripts\Activate.ps1
```

**Linux/macOS/Git Bash:**
```bash
source venv/bin/activate
```

### 3. 패키지 설치

```bash
pip install -r requirements.txt
```

### 4. 스크립트 실행

```bash
python coupang_scraper_final.py
```

---

## 📚 설치되는 패키지

- **selenium**: 웹 자동화
- **undetected-chromedriver**: 봇 감지 우회용 Chrome 드라이버
- **beautifulsoup4**: HTML 파싱
- **lxml**: XML/HTML 파서
- **pymysql**: MySQL 데이터베이스 연결
- **pandas**: 데이터 처리
- **openpyxl**: Excel 파일 처리
- 기타 의존성 패키지

---

## ⚙️ 설정

### Chrome 브라우저 경로

스크립트는 자동으로 Chrome을 찾습니다. 일반적인 경로:
- **Windows**: 
  - `C:\Program Files\Google\Chrome\Application\chrome.exe`
  - `C:\Program Files (x86)\Google\Chrome\Application\chrome.exe`
- **macOS**: `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`
- **Linux**: `/usr/bin/google-chrome` 또는 `/usr/bin/chromium-browser`

### 데이터베이스 설정 (선택사항)

`coupang_scraper_final.py` 파일의 `DB_CONFIG` 섹션에서 데이터베이스 연결 정보를 수정할 수 있습니다.

```python
DB_CONFIG = {
    "host": "3.88.110.157",
    "port": 3306,
    "user": "cphuser",
    "password": "cphpw123",
    "database": "CouPangHelp",
    "charset": "utf8mb4",
}
```

---

## 🔧 문제 해결

### 1. "Python을 찾을 수 없습니다"

- Python이 설치되어 있는지 확인: `python --version`
- PATH 환경 변수에 Python이 추가되어 있는지 확인
- Python 재설치 시 "Add Python to PATH" 옵션 체크

### 2. "Chrome을 찾을 수 없습니다"

- Chrome 브라우저가 설치되어 있는지 확인
- Chrome 실행 파일 경로가 올바른지 확인
- Chrome을 재설치해보세요

### 3. "포트 9222가 이미 사용 중입니다"

- 다른 Chrome 인스턴스가 실행 중인지 확인
- 작업 관리자에서 Chrome 프로세스 종료
- 또는 스크립트의 `debug_port` 값을 변경

### 4. 패키지 설치 오류

- 인터넷 연결 확인
- pip 업그레이드: `python -m pip install --upgrade pip`
- 가상환경이 활성화되어 있는지 확인
- 관리자 권한으로 실행 (Windows)

### 5. 캡차가 계속 나타납니다

- `chrome_cookie/` 디렉토리 삭제 후 재실행
- VPN 사용하여 IP 주소 변경
- 검색 빈도 줄이기 (대기 시간 증가)

### 6. "ModuleNotFoundError"

- 가상환경이 활성화되어 있는지 확인
- `pip install -r requirements.txt` 다시 실행

---

## 📝 실행 흐름

1. **Chrome 브라우저 시작**
   - Chrome을 디버깅 포트(9222)로 실행
   - 쿠키 저장 디렉토리: `chrome_cookie/`

2. **Google 검색**
   - 검색 쿼리: `site:coupang.com/vp/products/ "한 달간 {숫자} 명 이상 구매했어요"`
   - 검색 결과에서 쿠팡 상품 URL 추출

3. **페이지별 데이터 수집**
   - 1페이지 → 상품 추출 → DB 저장
   - 2페이지 → 상품 추출 → DB 저장
   - ...
   - 최종 페이지까지 반복

4. **데이터베이스 저장**
   - 각 페이지마다 자동으로 DB에 저장
   - 중복 제거 (productID 기준)

---

## 📁 생성되는 파일/폴더

- `venv/`: 가상환경 디렉토리
- `chrome_cookie/`: Chrome 쿠키 저장 디렉토리
- `chrome_user_profile/`: Chrome 사용자 프로필 디렉토리

---

## ⚠️ 주의사항

1. **캡차 해결**
   - Google이 봇을 감지하면 캡차가 나타날 수 있습니다.
   - 브라우저 창에서 캡차를 수동으로 해결해야 합니다.
   - 캡차 해결 후 터미널에서 Enter 키를 누르면 계속 진행됩니다.

2. **실행 시간**
   - 각 페이지당 약 15-45초 정도 소요됩니다 (사람처럼 자연스러운 대기).
   - 전체 페이지 수에 따라 실행 시간이 달라집니다.

3. **데이터베이스 연결**
   - DB 연결이 실패해도 스크래핑은 계속됩니다.
   - DB 저장은 선택사항입니다.

---

## 📞 추가 도움말

- `RUN.md`: 실행 방법 상세 가이드
- `ANTI_BOT_TIPS.md`: 봇 감지 우회 팁

---

## ✅ 체크리스트

설치 전 확인:
- [ ] Python 3.7 이상 설치됨
- [ ] Google Chrome 설치됨
- [ ] 인터넷 연결됨

설치 후 확인:
- [ ] `setup.bat` 또는 `setup.sh` 실행 완료
- [ ] 가상환경 활성화됨
- [ ] 패키지 설치 완료
- [ ] `run.bat` 또는 `run.sh` 실행 가능

