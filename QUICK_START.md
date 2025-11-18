# 빠른 시작 가이드

## 🚀 Windows에서 실행하기

### 방법 1: 명령 프롬프트(CMD) 사용 (권장)

1. **명령 프롬프트 열기**
   - `Win + R` → `cmd` 입력 → Enter

2. **프로젝트 폴더로 이동**
   ```cmd
   cd C:\JProject\coupang_batch
   ```

3. **초기 설정 (처음 한 번만)**
   ```cmd
   setup.bat
   ```

4. **스크래퍼 실행**
   ```cmd
   run.bat
   ```

### 방법 2: PowerShell 사용

1. **PowerShell 열기**
   - `Win + X` → `Windows PowerShell` 선택

2. **프로젝트 폴더로 이동**
   ```powershell
   cd C:\JProject\coupang_batch
   ```

3. **초기 설정 (처음 한 번만)**
   ```powershell
   .\setup.bat
   ```

4. **스크래퍼 실행**
   ```powershell
   .\run.bat
   ```

### 방법 3: Git Bash 사용

⚠️ **주의**: Git Bash에서는 `.bat` 파일 대신 `.sh` 파일을 사용해야 합니다!

1. **Git Bash 열기**

2. **프로젝트 폴더로 이동**
   ```bash
   cd /c/JProject/coupang_batch
   ```

3. **초기 설정 (처음 한 번만)**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

4. **스크래퍼 실행**
   ```bash
   chmod +x run.sh
   ./run.sh
   ```

---

## ❌ Python을 찾을 수 없는 경우

### 해결 방법 1: Python 재설치

1. [Python 공식 사이트](https://www.python.org/downloads/)에서 Python 3.7 이상 다운로드
2. 설치 시 **반드시 "Add Python to PATH" 옵션을 체크**하세요!
3. 설치 완료 후 **명령 프롬프트를 재시작**하세요
4. 다음 명령어로 확인:
   ```cmd
   python --version
   ```

### 해결 방법 2: Python Launcher 사용

Windows에 Python이 설치되어 있지만 PATH에 없을 수 있습니다. 다음을 시도해보세요:

```cmd
py --version
```

또는

```cmd
py -3 --version
```

### 해결 방법 3: 수동으로 Python 경로 추가

1. Python 설치 경로 확인 (예: `C:\Users\사용자명\AppData\Local\Programs\Python\Python39\`)
2. 시스템 환경 변수 PATH에 Python 경로 추가
3. 명령 프롬프트 재시작

---

## 🔍 Python 설치 확인

다음 명령어 중 하나가 작동해야 합니다:

```cmd
python --version
```

또는

```cmd
py --version
```

또는

```cmd
python3 --version
```

---

## 💡 팁

- **Git Bash 사용 시**: 반드시 `setup.sh`와 `run.sh`를 사용하세요!
- **CMD/PowerShell 사용 시**: `setup.bat`과 `run.bat`을 사용하세요!
- Python이 설치되어 있지만 인식되지 않으면 명령 프롬프트를 재시작해보세요.

