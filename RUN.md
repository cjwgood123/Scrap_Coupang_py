# 실행 방법

## 방법 1: 배치 파일 사용 (가장 간단) ⭐

### Windows CMD/PowerShell에서:
```bash
run.bat
```

### Git Bash에서:
```bash
chmod +x run.sh
./run.sh
```

---

## 방법 2: 직접 실행

### 1. 가상환경 활성화

#### Windows PowerShell:
```powershell
.\venv\Scripts\activate
```

#### Windows CMD:
```cmd
venv\Scripts\activate.bat
```

#### Git Bash:
```bash
source venv/Scripts/activate
```

### 2. 필요한 패키지 설치 (처음 한 번만)
```bash
pip install -r requirements.txt
```

### 3. 스크립트 실행
```bash
python coupang_scraper_final.py
```

---

## 실행 흐름

1. **Chrome 브라우저 시작**
   - Chrome을 디버깅 포트(9222)로 실행
   - 쿠키 저장 디렉토리: `chrome_cookie/`

2. **Google 검색**
   - 검색 쿼리: `site:coupang.com/vp/products/ "한 달간 100 명 이상 구매했어요"`
   - 검색 결과에서 쿠팡 상품 URL 추출

3. **페이지별 데이터 수집**
   - 1페이지 → 상품 추출 → 저장
   - 2페이지 → 상품 추출 → 저장
   - ...
   - 최종 페이지까지 반복

4. **엑셀 파일 저장**
   - 파일명: `coupang_products.xlsx`
   - 컬럼: URL, 제목

---

## 주의사항

### 1. Chrome 브라우저 필요
- Chrome 브라우저가 설치되어 있어야 합니다.
- Chrome 실행 파일 경로는 자동으로 찾습니다.

### 2. 디버깅 포트 충돌
- 포트 9222가 이미 사용 중이면 오류가 발생할 수 있습니다.
- 다른 Chrome 인스턴스가 실행 중이면 종료하세요.

### 3. 캡차 해결
- Google이 봇을 감지하면 캡차가 나타날 수 있습니다.
- 브라우저 창에서 캡차를 수동으로 해결해야 합니다.
- 캡차 해결 후 터미널에서 Enter 키를 누르면 계속 진행됩니다.

### 4. 쿠키 저장
- 쿠키는 `chrome_cookie/` 디렉토리에 저장됩니다.
- 재실행 시에도 쿠키가 유지됩니다.
- 캡차 발생 빈도가 줄어들 수 있습니다.

### 5. 실행 시간
- 각 페이지당 약 3-6초 정도 소요됩니다.
- 전체 페이지 수에 따라 실행 시간이 달라집니다.

---

## 문제 해결

### Chrome을 찾을 수 없음
- Chrome 브라우저가 설치되어 있는지 확인하세요.
- 일반적인 설치 경로:
  - Windows: `C:\Program Files\Google\Chrome\Application\chrome.exe`
  - macOS: `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`
  - Linux: `/usr/bin/google-chrome`

### 포트 9222가 이미 사용 중
- 다른 Chrome 인스턴스가 실행 중이면 종료하세요.
- 또는 다른 포트를 사용하도록 코드를 수정하세요.

### 패키지 설치 오류
- 가상환경이 활성화되어 있는지 확인하세요.
- Python 버전이 3.7 이상인지 확인하세요.

### 캡차가 계속 발생
- `chrome_cookie/` 디렉토리를 삭제하고 다시 시도하세요.
- VPN을 사용하여 IP 주소를 변경해보세요.
- 검색 쿼리를 변경하거나 검색 빈도를 줄이세요.

---

## 출력 파일

- **엑셀 파일**: `coupang_products.xlsx`
  - URL: 쿠팡 상품 URL
  - 제목: 상품 제목

---

## 실행 예시

```
[INFO] Chrome 브라우저 시작 중...
[INFO] Chrome 실행 파일: C:\Program Files\Google\Chrome\Application\chrome.exe
[INFO] 사용자 데이터 디렉토리: C:\Users\user\IdeaProjects\AIProject\coupang\chrome_cookie
[INFO] 디버깅 포트: 9222
[INFO] Chrome 프로세스 시작 중...
[SUCCESS] Chrome이 디버깅 포트로 시작되었습니다.
[SUCCESS] Chrome이 디버깅 포트로 연결되었습니다.
[INFO] 쿠키가 저장됩니다. 재실행 시에도 쿠키가 유지됩니다.
검색 중: site:coupang.com/vp/products/ "한 달간 100 명 이상 구매했어요"
목표: 마지막 페이지까지 모든 상품 수집

[페이지 1] 로드 중...
  페이지 로딩 대기 중... (4.2초)
[페이지 1] 상품 추출 중...
  → 10개 상품 발견 (누적 총 10개)
  ...
```
