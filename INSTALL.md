# Python 명령어로 직접 설치하기

## 🚀 빠른 설치 (Git Bash / 터미널)

### 1단계: 가상환경 생성

```bash
python -m venv venv
```

또는 Python3가 필요한 경우:

```bash
python3 -m venv venv
```

### 2단계: 가상환경 활성화

**Windows Git Bash:**
```bash
source venv/Scripts/activate
```

**Linux/macOS:**
```bash
source venv/bin/activate
```

### 3단계: 패키지 설치

```bash
pip install -r requirements.txt
```

### 4단계: 스크래퍼 실행

```bash
python coupang_scraper_final.py
```

---

## 📝 전체 명령어 (한 번에 복사해서 실행)

### Windows Git Bash:

```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화
source venv/Scripts/activate

# 패키지 설치
pip install -r requirements.txt

# 실행
python coupang_scraper_final.py
```

### Linux/macOS:

```bash
# 가상환경 생성
python3 -m venv venv

# 가상환경 활성화
source venv/bin/activate

# 패키지 설치
pip install -r requirements.txt

# 실행
python coupang_scraper_final.py
```

---

## 💡 팁

- 가상환경이 활성화되면 프롬프트 앞에 `(venv)`가 표시됩니다.
- 가상환경을 비활성화하려면: `deactivate`
- 다음에 실행할 때는 가상환경만 활성화하면 됩니다:
  ```bash
  source venv/Scripts/activate  # Windows Git Bash
  python coupang_scraper_final.py
  ```

