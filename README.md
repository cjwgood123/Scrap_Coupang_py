# 쿠팡 상품 스크래퍼

Google 검색을 통해 쿠팡 상품 정보를 수집하는 자동화 스크립트입니다.

## 🚀 빠른 시작

### Windows 사용자

1. **초기 설정 (처음 한 번만)**
   ```cmd
   setup.bat
   ```

2. **스크래퍼 실행**
   ```cmd
   run.bat
   ```

### Linux/macOS/Git Bash 사용자

1. **초기 설정 (처음 한 번만)**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

2. **스크래퍼 실행**
   ```bash
   chmod +x run.sh
   ./run.sh
   ```

## 📋 사전 요구사항

- Python 3.7 이상
- Google Chrome 브라우저
- 인터넷 연결

## 📚 상세 가이드

- **[SETUP.md](SETUP.md)**: 설치 및 설정 가이드
- **[RUN.md](RUN.md)**: 실행 방법 상세 가이드

## ✨ 주요 기능

- ✅ Google 검색을 통한 쿠팡 상품 URL 추출
- ✅ 상품 제목, 상품평, 카테고리 정보 수집
- ✅ 자동 페이지 탐색 (1페이지부터 마지막 페이지까지)
- ✅ MySQL 데이터베이스 자동 저장
- ✅ 봇 감지 우회 (undetected-chromedriver 사용)
- ✅ 사람처럼 자연스러운 브라우저 동작
- ✅ 캡차 자동 해결 시도

## 🔧 기술 스택

- **Selenium**: 웹 자동화
- **undetected-chromedriver**: 봇 감지 우회
- **BeautifulSoup**: HTML 파싱
- **PyMySQL**: MySQL 데이터베이스 연결

## 📝 사용 방법

1. 스크립트를 실행하면 검색 시작 숫자를 입력하라는 메시지가 나타납니다.
2. 엔터만 누르면 처음부터 시작합니다.
3. 스크립트가 자동으로 Google 검색을 수행하고 쿠팡 상품 정보를 수집합니다.
4. 각 페이지마다 데이터베이스에 자동으로 저장됩니다.

## ⚠️ 주의사항

- Google이 봇을 감지하면 캡차가 나타날 수 있습니다.
- 캡차가 나타나면 브라우저 창에서 수동으로 해결해야 합니다.
- 캡차 해결 후 터미널에서 Enter 키를 누르면 계속 진행됩니다.

## 📁 파일 구조

```
coupang_batch/
├── coupang_scraper_final.py  # 메인 스크립트
├── setup.bat                  # Windows 초기 설정 스크립트
├── setup.sh                   # Linux/macOS 초기 설정 스크립트
├── run.bat                    # Windows 실행 스크립트
├── run.sh                     # Linux/macOS 실행 스크립트
├── requirements.txt           # Python 패키지 목록
├── SETUP.md                   # 설치 가이드
├── RUN.md                     # 실행 가이드
└── README.md                  # 이 파일
```

## 🐛 문제 해결

자세한 문제 해결 방법은 [SETUP.md](SETUP.md)의 "문제 해결" 섹션을 참고하세요.

## 📄 라이선스

이 프로젝트는 개인 사용 목적으로 제작되었습니다.
