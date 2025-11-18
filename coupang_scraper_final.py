#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
쿠팡 상품 URL 및 제목 추출 스크립트
Google 검색을 통해 쿠팡 상품 페이지 URL을 추출하고 제목을 가져와 엑셀 파일로 저장합니다.
"""

try:
    import undetected_chromedriver as uc
    USE_UNDETECTED_AVAILABLE = True
except ImportError:
    USE_UNDETECTED_AVAILABLE = False
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import time
import urllib.parse
import re
import random
import os
import tempfile
import subprocess
import platform
from typing import List, Dict, Any
from pathlib import Path
from datetime import datetime

try:
    import pymysql
    from pymysql.cursors import DictCursor
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False
    pymysql = None
    DictCursor = None


DB_CONFIG = {
    "host": "3.88.110.157",
    "port": 3306,
    "user": "cphuser",
    "password": "cphpw123",
    "database": "CouPangHelp",
    "charset": "utf8mb4",
}

if MYSQL_AVAILABLE:
    DB_CONFIG["cursorclass"] = DictCursor


def human_like_wait(base_min: float = 15.0, base_max: float = 45.0):
    """
    사람처럼 자연스러운 대기 시간 생성.
    사람은 페이지를 읽고, 생각하고, 다른 작업을 하기도 함.
    빠르게 넘길 수도 있고 오래 넘길 수도 있게 변동성을 유지하되,
    최대 범위(base_max)를 초과하지 않도록 제한.
    
    Args:
        base_min: 기본 최소 대기 시간 (초)
        base_max: 기본 최대 대기 시간 (초)
        
    Returns:
        대기 시간 (초) - base_min과 base_max 사이의 값
    """
    # 베이스 대기 시간 (15-45초)
    base_wait = random.uniform(base_min, base_max)
    
    # 변동성 추가: 때때로 더 긴 대기 시간 (사람이 다른 탭을 보거나 다른 일을 할 때)
    # 하지만 최대 범위를 초과하지 않도록 주의
    if random.random() < 0.2:  # 20% 확률로 약간 더 긴 대기
        # 현재 base_wait이 base_max에 가까울 수 있으므로, 남은 범위 내에서만 추가
        remaining_range = max(0, base_max - base_wait)
        if remaining_range > 0:
            # 남은 범위의 일부만 사용 (최대 10초 추가)
            extra_wait = min(remaining_range, random.uniform(2, 10))
            base_wait += extra_wait
        # base_wait은 이미 base_max 이하이므로 추가 제한 불필요
    
    # 변동성 추가: 때때로 짧은 대기 시간 (빠르게 스크롤할 때)
    if random.random() < 0.25:  # 25% 확률로 짧은 대기 (더 자주 빠르게)
        # base_wait을 줄이되, base_min보다 짧아지지 않도록
        reduction_factor = random.uniform(0.6, 0.9)  # 0.6-0.9배 (기존보다 덜 줄임)
        base_wait *= reduction_factor
        # 최소 범위보다 짧아지지 않도록 제한
        if base_wait < base_min:
            base_wait = base_min
    
    # 최종 범위 확인 및 제한
    base_wait = max(base_min, min(base_wait, base_max))
    
    return base_wait


def human_like_scroll(driver):
    """
    사람처럼 자연스럽게 스크롤.
    사람은 목적을 가지고 스크롤하고, 때때로 멈추고, 다시 스크롤함.
    
    Args:
        driver: Selenium WebDriver
    """
    try:
        # 스크롤 패턴 선택 (목적 있는 스크롤)
        scroll_patterns = [
            # 패턴 1: 천천히 아래로 스크롤 (읽으면서)
            {'direction': 'down', 'speed': 'slow', 'steps': random.randint(3, 6), 'pause': (1.5, 3.0)},
            # 패턴 2: 빠르게 아래로 스크롤 (찾고 있음)
            {'direction': 'down', 'speed': 'fast', 'steps': random.randint(2, 4), 'pause': (0.5, 1.5)},
            # 패턴 3: 위아래로 왔다갔다 (확인 중)
            {'direction': 'mixed', 'speed': 'medium', 'steps': random.randint(4, 8), 'pause': (0.8, 2.0)},
        ]
        
        pattern = random.choice(scroll_patterns)
        steps = pattern['steps']
        pause_min, pause_max = pattern['pause']
        
        # 현재 스크롤 위치
        current_scroll = driver.execute_script("return window.pageYOffset;")
        page_height = driver.execute_script("return document.body.scrollHeight;")
        viewport_height = driver.execute_script("return window.innerHeight;")
        
        for i in range(steps):
            # 목적 있는 스크롤 (특정 위치로)
            if pattern['direction'] == 'down':
                # 아래로 스크롤
                scroll_amount = random.uniform(viewport_height * 0.3, viewport_height * 0.7)
                if pattern['speed'] == 'slow':
                    # 천천히 스크롤 (여러 단계로)
                    for j in range(3):
                        driver.execute_script(f"window.scrollBy(0, {scroll_amount / 3});")
                        time.sleep(random.uniform(0.3, 0.8))
                else:
                    # 빠르게 스크롤
                    driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            
            elif pattern['direction'] == 'mixed':
                # 위아래로 왔다갔다
                if i % 2 == 0:
                    scroll_amount = random.uniform(viewport_height * 0.2, viewport_height * 0.5)
                    driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                else:
                    scroll_amount = random.uniform(viewport_height * 0.1, viewport_height * 0.3)
                    driver.execute_script(f"window.scrollBy(0, -{scroll_amount});")
            
            # 스크롤 후 멈춤 (읽는 시간)
            pause_time = random.uniform(pause_min, pause_max)
            time.sleep(pause_time)
            
            # 때때로 더 긴 멈춤 (사람이 생각하는 시간)
            if random.random() < 0.3:  # 30% 확률
                thinking_time = random.uniform(2, 5)
                time.sleep(thinking_time)
        
        # 때때로 맨 위로 돌아가기 (다시 확인)
        if random.random() < 0.2:  # 20% 확률
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(random.uniform(1, 3))
            
    except Exception as e:
        pass


def human_like_mouse_movement(driver):
    """
    사람처럼 자연스러운 마우스 움직임.
    사람은 목적을 가지고 마우스를 움직이고, 때때로 망설임이 있음.
    
    Args:
        driver: Selenium WebDriver
    """
    try:
        actions = ActionChains(driver)
        
        # 마우스 움직임 패턴 선택
        movement_patterns = [
            # 패턴 1: 작은 움직임 (클릭 전 망설임)
            {'moves': random.randint(1, 3), 'range': (10, 50), 'speed': 'slow'},
            # 패턴 2: 큰 움직임 (다른 위치로 이동)
            {'moves': random.randint(2, 4), 'range': (50, 200), 'speed': 'fast'},
            # 패턴 3: 혼합 (목적 있는 움직임)
            {'moves': random.randint(3, 5), 'range': (20, 100), 'speed': 'medium'},
        ]
        
        pattern = random.choice(movement_patterns)
        moves = pattern['moves']
        move_min, move_max = pattern['range']
        
        for i in range(moves):
            # 목적 있는 움직임 (특정 방향으로)
            offset_x = random.randint(-move_max, move_max)
            offset_y = random.randint(-move_max, move_max)
            
            # 망설임 (사람처럼)
            if pattern['speed'] == 'slow':
                actions.move_by_offset(offset_x, offset_y)
                actions.pause(random.uniform(0.5, 1.5))
            elif pattern['speed'] == 'fast':
                actions.move_by_offset(offset_x, offset_y)
                actions.pause(random.uniform(0.2, 0.8))
            else:
                actions.move_by_offset(offset_x, offset_y)
                actions.pause(random.uniform(0.3, 1.2))
        
        actions.perform()
        
        # 때때로 더 긴 멈춤 (사람이 생각하는 시간)
        if random.random() < 0.3:  # 30% 확률
            time.sleep(random.uniform(1, 3))
            
    except Exception as e:
        pass


def human_like_click(driver, element):
    """
    사람처럼 자연스럽게 클릭.
    사람은 클릭 전에 망설이고, 마우스를 요소로 이동하고, 잠시 멈춘 후 클릭함.
    
    Args:
        driver: Selenium WebDriver
        element: 클릭할 요소
    """
    try:
        # 요소로 스크롤 (사람처럼)
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
        
        # 스크롤 후 대기 (사람이 요소를 찾는 시간)
        time.sleep(random.uniform(1, 3))
        
        # 마우스를 요소로 이동 (목적 있는 움직임)
        actions = ActionChains(driver)
        
        # 클릭 전 망설임 (사람처럼)
        # 먼저 요소 근처로 이동
        actions.move_to_element_with_offset(element, random.randint(-20, 20), random.randint(-20, 20))
        actions.pause(random.uniform(0.5, 1.5))
        
        # 요소로 정확히 이동
        actions.move_to_element(element)
        actions.pause(random.uniform(0.5, 2.0))  # 클릭 전 멈춤 (사람이 생각하는 시간)
        
        # 클릭
        actions.click()
        actions.perform()
        
        # 클릭 후 짧은 대기 (사람이 반응을 기다리는 시간)
        time.sleep(random.uniform(0.5, 1.5))
        
    except Exception as e:
        # ActionChains 실패 시 일반 클릭
        try:
            element.click()
        except:
            driver.execute_script("arguments[0].click();", element)


def find_chrome_executable():
    """
    시스템에 설치된 Chrome 실행 파일 경로를 찾습니다.
    
    Returns:
        Chrome 실행 파일 경로
    """
    system = platform.system()
    
    if system == "Windows":
        # Windows에서 Chrome 경로 찾기
        possible_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
    elif system == "Darwin":  # macOS
        possible_paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
    elif system == "Linux":
        possible_paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium-browser",
            "/usr/bin/chromium",
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
    
    # PATH에서 찾기
    try:
        import shutil
        chrome_path = shutil.which("google-chrome") or shutil.which("chrome") or shutil.which("chromium")
        if chrome_path:
            return chrome_path
    except:
        pass
    
    return None


def start_chrome_with_debugging_port(user_data_dir: str, debug_port: int = 9222):
    """
    Chrome을 디버깅 포트로 실행합니다.
    쿠키 저장을 위해 user-data-dir를 사용합니다.
    
    Args:
        user_data_dir: Chrome 사용자 데이터 디렉토리 경로
        debug_port: 디버깅 포트 (기본값: 9222)
        
    Returns:
        Chrome 프로세스 객체
    """
    chrome_path = find_chrome_executable()
    
    if not chrome_path:
        raise FileNotFoundError("Chrome 실행 파일을 찾을 수 없습니다.")
    
    print(f"[INFO] Chrome 실행 파일: {chrome_path}")
    print(f"[INFO] 사용자 데이터 디렉토리: {user_data_dir}")
    print(f"[INFO] 디버깅 포트: {debug_port}")
    
    # user-data-dir 디렉토리 생성
    os.makedirs(user_data_dir, exist_ok=True)
    
    # Chrome 실행 명령어
    chrome_args = [
        chrome_path,
        f"--remote-debugging-port={debug_port}",
        f"--user-data-dir={user_data_dir}",
        "--disable-notifications",
        "--disable-popup-blocking",
        "--start-maximized",
        "--lang=ko-KR",
    ]
    
    # Chrome 프로세스 시작
    try:
        if platform.system() == "Windows":
            # Windows에서 실행
            try:
                # CREATE_NEW_CONSOLE 플래그 사용 (Windows 전용)
                process = subprocess.Popen(
                    chrome_args,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
            except AttributeError:
                # CREATE_NEW_CONSOLE이 없는 경우 (구버전 Python)
                process = subprocess.Popen(
                    chrome_args,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
        else:
            # Linux/macOS에서 실행
            process = subprocess.Popen(
                chrome_args,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        
        # Chrome이 시작될 때까지 대기
        print("[INFO] Chrome 프로세스 시작 중...")
        time.sleep(3)
        
        print("[SUCCESS] Chrome이 디버깅 포트로 시작되었습니다.")
        return process
        
    except Exception as e:
        print(f"[ERROR] Chrome 프로세스 시작 실패: {e}")
        raise


def setup_chrome_driver(headless: bool = False, use_debugging_port: bool = True, debug_port: int = 9222):
    """
    Chrome 드라이버를 설정합니다.
    쿠키 저장을 위해 디버깅 포트를 사용하여 Chrome을 실행합니다.
    
    Args:
        headless: 헤드리스 모드로 실행할지 여부 (False 권장)
        use_debugging_port: 디버깅 포트를 사용하여 Chrome을 실행할지 여부 (True 권장)
        debug_port: 디버깅 포트 (기본값: 9222)
        
    Returns:
        Chrome WebDriver 인스턴스
    """
    # 디버깅 포트를 사용하여 Chrome 실행 (쿠키 저장)
    if use_debugging_port and not headless:
        try:
            print("[INFO] Chrome 디버깅 모드로 시작 중...")
            
            # 사용자 데이터 디렉토리 설정
            user_data_dir = os.path.join(os.getcwd(), 'chrome_cookie')
            
            # Chrome을 디버깅 포트로 실행
            chrome_process = start_chrome_with_debugging_port(user_data_dir, debug_port)
            
            # Selenium WebDriver 옵션 설정
            if USE_UNDETECTED_AVAILABLE:
                options = uc.ChromeOptions()
            else:
                from selenium.webdriver.chrome.options import Options
                options = Options()
            
            # 디버깅 포트로 연결
            options.add_experimental_option("debuggerAddress", f"127.0.0.1:{debug_port}")
            
            # 최소한의 설정만 (일반 사용자 브라우저와 유사)
            options.add_argument('--disable-notifications')
            options.add_argument('--disable-popup-blocking')
            options.add_argument('--lang=ko-KR')
            
            # 언어 설정
            options.add_experimental_option('prefs', {
                'intl.accept_languages': 'ko-KR,ko,en-US,en',
            })
            
            # WebDriver 생성
            if USE_UNDETECTED_AVAILABLE:
                driver = uc.Chrome(options=options, version_main=None, use_subprocess=False)
            else:
                from selenium import webdriver
                driver = webdriver.Chrome(options=options)
            
            # navigator.webdriver 숨기기 제거 (이미 구글이 알고 있는 봇 행동)
            # undetected-chromedriver가 이미 적절히 처리함
            
            print("[SUCCESS] Chrome이 디버깅 포트로 연결되었습니다.")
            print("[INFO] 쿠키가 저장됩니다. 재실행 시에도 쿠키가 유지됩니다.")
            return driver
            
        except Exception as e:
            print(f"[WARNING] 디버깅 포트 모드 사용 실패: {e}")
            print("[INFO] 일반 모드로 대체합니다...")
            use_debugging_port = False
    
    # 일반 모드 (디버깅 포트 사용 안 함)
    # undetected-chromedriver 사용 (최소한의 설정만)
    if USE_UNDETECTED_AVAILABLE:
        try:
            print("[INFO] Chrome 브라우저 시작 중...")
            
            # undetected-chromedriver 옵션 설정 (최소한만)
            options = uc.ChromeOptions()
            
            # 헤드리스 모드는 사용하지 않음
            if headless:
                options.add_argument('--headless=new')
            
            # Chrome 사용자 프로필 사용 (실제 사용자처럼)
            user_data_dir = os.path.join(os.getcwd(), 'chrome_user_profile')
            os.makedirs(user_data_dir, exist_ok=True)
            options.add_argument(f'--user-data-dir={user_data_dir}')
            print(f"[INFO] Chrome 사용자 프로필 사용: {user_data_dir}")
            
            # 자동화 배너 제거 설정 (필수)
            options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
            options.add_experimental_option("useAutomationExtension", False)
            options.add_argument("--disable-blink-features=AutomationControlled")
            
            # 최소한의 필수 설정만 (일반 사용자 브라우저와 유사)
            options.add_argument('--start-maximized')
            options.add_argument('--lang=ko-KR')
            
            # 언어 설정 (일반 사용자 설정)
            options.add_experimental_option('prefs', {
                'intl.accept_languages': 'ko-KR,ko,en-US,en',
            })
            
            # undetected-chromedriver로 드라이버 생성 (기본 설정만)
            driver = uc.Chrome(
                options=options, 
                version_main=None, 
                use_subprocess=True,
            )
            
            # navigator.webdriver 숨기기 제거 (이미 구글이 알고 있는 봇 행동)
            # undetected-chromedriver가 이미 적절히 처리함
            
            print("[SUCCESS] Chrome 브라우저 시작 완료")
            return driver
            
        except Exception as e:
            print(f"[WARNING] undetected-chromedriver 사용 실패: {e}")
            print("[INFO] 일반 Selenium으로 대체합니다...")
    
    # 일반 Selenium 사용 (fallback) - 최소한의 설정만
    try:
        if not USE_UNDETECTED_AVAILABLE:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
        
        chrome_options = Options()
        
        if headless:
            chrome_options.add_argument('--headless=new')
        
        # 자동화 배너 제거 설정 (필수)
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        
        # 최소한의 설정만 (일반 사용자 브라우저와 유사)
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--lang=ko-KR')
        
        # Chrome 사용자 프로필 사용
        user_data_dir = os.path.join(os.getcwd(), 'chrome_user_profile')
        os.makedirs(user_data_dir, exist_ok=True)
        chrome_options.add_argument(f'--user-data-dir={user_data_dir}')
        print(f"[INFO] Chrome 사용자 프로필 사용: {user_data_dir}")
        
        # 언어 설정
        chrome_options.add_experimental_option('prefs', {
            'intl.accept_languages': 'ko-KR,ko,en-US,en',
        })
        
        driver = webdriver.Chrome(options=chrome_options)
        
        # navigator.webdriver 숨기기 제거 (이미 구글이 알고 있는 봇 행동)
        # 일반 Selenium에서는 최소한만 사용 (필요시)
        
        print("[SUCCESS] Chrome 브라우저 시작 완료 (일반 Selenium)")
        return driver
        
    except Exception as e:
        print(f"[ERROR] Chrome 드라이버 설정 오류: {e}")
        print("[TIP] Chrome 브라우저가 설치되어 있는지 확인하세요.")
        raise


def check_captcha(driver) -> bool:
    """
    실제 캡차 페이지인지 확인합니다.
    일반 검색 결과 페이지에서도 캡차 관련 키워드가 있을 수 있으므로,
    실제 캡차 요소를 확인합니다.
    
    Args:
        driver: Selenium WebDriver
        
    Returns:
        캡차 페이지이면 True, 아니면 False
    """
    try:
        # 1. URL 확인 (캡차 페이지는 특정 URL 패턴을 가짐)
        current_url = driver.current_url.lower()
        if 'sorry/index' in current_url or ('sorry' in current_url and 'unusual' in current_url):
            return True
        
        # 2. 페이지 제목 확인 (캡차 페이지는 특정 제목을 가짐)
        page_title = driver.title.lower()
        if 'sorry' in page_title and ('unusual traffic' in page_title or 'robot' in page_title):
            return True
        
        # 3. 실제 캡차 요소 확인 (reCAPTCHA iframe)
        try:
            # reCAPTCHA iframe 확인
            iframes = driver.find_elements(By.CSS_SELECTOR, 'iframe[src*="recaptcha"]')
            if iframes:
                for iframe in iframes:
                    if iframe.is_displayed():
                        return True
        except:
            pass
        
        # 4. 캡차 페이지의 고유한 요소 확인
        try:
            # "Our systems have detected unusual traffic" 메시지 확인
            captcha_message = driver.find_elements(By.XPATH, "//*[contains(text(), 'Our systems have detected unusual traffic') or contains(text(), 'unusual traffic from your computer network')]")
            if captcha_message:
                for msg in captcha_message:
                    if msg.is_displayed():
                        return True
        except:
            pass
        
        # 5. 검색 결과가 실제로 있는지 확인 (검색 결과가 없으면 캡차일 수 있음)
        try:
            # Google 검색 결과 컨테이너 확인
            search_results = driver.find_elements(By.CSS_SELECTOR, 'div.MjjYud, div.g, div[data-hveid]')
            if len(search_results) == 0:
                # 검색 결과가 없고, 캡차 관련 메시지가 있으면 캡차로 판단
                page_text = driver.page_source.lower()
                if 'unusual traffic' in page_text and 'sorry' in page_text:
                    return True
        except:
            pass
        
        # 6. 페이지 소스에서 캡차 관련 강한 신호 확인 (더 정확하게)
        page_text = driver.page_source.lower()
        
        # 강한 캡차 신호만 확인 (일반 검색 결과에서는 나타나지 않는 조합)
        # "sorry"와 "unusual traffic"이 함께 나타나면 캡차
        if 'sorry' in page_text and 'unusual traffic' in page_text:
            # 검색 결과 컨테이너가 있는지 다시 확인
            try:
                search_results = driver.find_elements(By.CSS_SELECTOR, 'div.MjjYud, div.g')
                # 검색 결과가 없으면 캡차로 판단
                if len(search_results) == 0:
                    return True
            except:
                # 검색 결과를 찾을 수 없으면 캡차로 판단
                return True
        
        # 모든 검사를 통과했으면 캡차가 아님
        return False
        
    except Exception as e:
        # 오류 발생 시 안전하게 False 반환 (캡차가 아닌 것으로 간주)
        return False


def _check_image_challenge(driver) -> bool:
    """
    이미지 선택 챌린지가 나타났는지 확인합니다.
    
    Args:
        driver: Selenium WebDriver
        
    Returns:
        이미지 선택 챌린지가 나타났으면 True, 아니면 False
    """
    try:
        driver.switch_to.default_content()
        
        # 이미지 선택 챌린지 iframe 확인
        challenge_selectors = [
            'iframe[src*="bframe"]',
            'iframe[title*="recaptcha challenge"]',
            'iframe[src*="/recaptcha/api2/bframe"]',
        ]
        
        for selector in challenge_selectors:
            try:
                challenge_iframes = driver.find_elements(By.CSS_SELECTOR, selector)
                for challenge_iframe in challenge_iframes:
                    try:
                        if challenge_iframe.is_displayed():
                            # bframe이 있는 경우 이미지 선택 챌린지일 수 있음
                            src = challenge_iframe.get_attribute('src') or ''
                            if 'bframe' in src.lower():
                                print("[INFO] reCAPTCHA 이미지 선택 챌린지가 나타났습니다.")
                                print("[INFO] 수동 해결이 필요합니다.")
                                return True
                    except:
                        continue
            except:
                continue
    except:
        pass
    
    return False


def try_auto_solve_recaptcha(driver, max_retries: int = 3) -> bool:
    """
    reCAPTCHA 체크박스를 자동으로 클릭 시도합니다.
    간단한 체크박스만 있는 경우 자동으로 해결합니다.
    
    Args:
        driver: Selenium WebDriver
        max_retries: 최대 재시도 횟수 (기본값: 3)
        
    Returns:
        자동으로 해결되었으면 True, 아니면 False (이미지 선택 등이 필요한 경우)
    """
    for retry in range(max_retries):
        try:
            if retry > 0:
                print(f"[INFO] reCAPTCHA 체크박스 찾기 재시도 {retry}/{max_retries - 1}...")
                time.sleep(random.uniform(2, 4))
            
            # reCAPTCHA iframe 찾기 (여러 종류의 iframe 선택자 시도)
            iframe_selectors = [
                'iframe[src*="recaptcha"]',
                'iframe[title*="reCAPTCHA"]',
                'iframe[title*="recaptcha"]',
                'iframe[id*="recaptcha"]',
                'iframe[name*="recaptcha"]',
                'iframe[src*="google.com/recaptcha"]',
                'iframe[src*="gstatic.com/recaptcha"]',
            ]
            
            iframes = []
            for selector in iframe_selectors:
                try:
                    found_iframes = driver.find_elements(By.CSS_SELECTOR, selector)
                    for iframe in found_iframes:
                        try:
                            if iframe.is_displayed():
                                iframes.append(iframe)
                        except:
                            pass
                except:
                    continue
            
            if not iframes:
                print(f"[WARNING] reCAPTCHA iframe을 찾을 수 없습니다. (재시도 {retry + 1}/{max_retries})")
                if retry < max_retries - 1:
                    continue
                return False
            
            # reCAPTCHA iframe으로 전환
            checkbox_found = False
            for iframe in iframes:
                try:
                    # iframe으로 전환
                    driver.switch_to.frame(iframe)
                    
                    # 체크박스 찾기 (여러 선택자 시도, 우선순위 순서)
                    # 사용자 제공 HTML 구조 기반: <span id="recaptcha-anchor" class="recaptcha-checkbox" role="checkbox">
                    checkbox_selectors = [
                        '#recaptcha-anchor',  # ID가 가장 명확
                        'span#recaptcha-anchor',  # span + ID
                        'span.recaptcha-checkbox[role="checkbox"]',  # 클래스 + role
                        'span[role="checkbox"][id="recaptcha-anchor"]',  # role + ID
                        'span.recaptcha-checkbox',  # 클래스만
                        'span[role="checkbox"]',  # role만
                        '.recaptcha-checkbox.goog-inline-block',  # 여러 클래스
                        'div.recaptcha-checkbox',
                        'div[role="checkbox"]',
                        '.recaptcha-checkbox-border',  # 체크박스 내부 요소
                        'div[class*="recaptcha-checkbox"]',
                    ]
                    
                    checkbox = None
                    for selector in checkbox_selectors:
                        try:
                            # WebDriverWait를 사용하여 요소가 나타날 때까지 대기
                            from selenium.webdriver.support.ui import WebDriverWait
                            from selenium.webdriver.support import expected_conditions as EC
                            
                            wait = WebDriverWait(driver, 3)
                            elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector)))
                            
                            for elem in elements:
                                try:
                                    if elem.is_displayed():
                                        # 요소가 실제로 클릭 가능한지 확인
                                        try:
                                            elem.get_attribute('role')  # 요소 접근 가능한지 확인
                                            checkbox = elem
                                            print(f"[INFO] 체크박스 발견: {selector}")
                                            break
                                        except:
                                            continue
                                except:
                                    continue
                            
                            if checkbox:
                                break
                        except:
                            continue
                    
                    # 체크박스를 찾지 못한 경우
                    if not checkbox:
                        print(f"[WARNING] 체크박스를 찾을 수 없습니다. iframe에서 나갑니다...")
                        driver.switch_to.default_content()
                        continue  # 다음 iframe 시도
                    
                    checkbox_found = True
                    
                    # 체크박스가 이미 체크되어 있는지 확인
                    try:
                        # aria-checked 속성 확인
                        aria_checked = checkbox.get_attribute('aria-checked')
                        if aria_checked == 'true':
                            print("[INFO] reCAPTCHA가 이미 체크되어 있습니다.")
                            driver.switch_to.default_content()
                            return True
                        
                        # 클래스에 checked가 있는지 확인
                        checkbox_class = checkbox.get_attribute('class') or ''
                        if 'checked' in checkbox_class.lower() and 'unchecked' not in checkbox_class.lower():
                            print("[INFO] reCAPTCHA가 이미 체크되어 있습니다.")
                            driver.switch_to.default_content()
                            return True
                    except Exception as e:
                        print(f"[WARNING] 체크박스 상태 확인 실패: {e}")
                    
                    # 체크박스 클릭
                    print("[INFO] reCAPTCHA 체크박스 클릭 시도 중...")
                    
                    # 여러 방법으로 클릭 시도
                    click_success = False
                    
                    # 방법 1: ActionChains를 사용하여 자연스러운 클릭
                    try:
                        # 체크박스가 보이도록 스크롤
                        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", checkbox)
                        time.sleep(random.uniform(0.3, 0.7))
                        
                        # 마우스를 체크박스로 이동
                        actions = ActionChains(driver)
                        actions.move_to_element(checkbox).pause(random.uniform(0.2, 0.5)).click().perform()
                        click_success = True
                        print("[INFO] ActionChains 클릭 성공")
                    except Exception as e:
                        print(f"[WARNING] ActionChains 클릭 실패: {e}")
                    
                    # 방법 2: 일반 클릭으로 대체
                    if not click_success:
                        try:
                            checkbox.click()
                            click_success = True
                            print("[INFO] 일반 클릭 성공")
                        except Exception as e:
                            print(f"[WARNING] 일반 클릭 실패: {e}")
                    
                    # 방법 3: JavaScript 클릭으로 대체
                    if not click_success:
                        try:
                            driver.execute_script("arguments[0].click();", checkbox)
                            click_success = True
                            print("[INFO] JavaScript 클릭 성공")
                        except Exception as e:
                            print(f"[WARNING] JavaScript 클릭 실패: {e}")
                    
                    # 방법 4: JavaScript로 직접 클릭 이벤트 발생
                    if not click_success:
                        try:
                            driver.execute_script("""
                                var checkbox = arguments[0];
                                var event = new MouseEvent('click', {
                                    view: window,
                                    bubbles: true,
                                    cancelable: true
                                });
                                checkbox.dispatchEvent(event);
                            """, checkbox)
                            click_success = True
                            print("[INFO] JavaScript 이벤트 클릭 성공")
                        except Exception as e:
                            print(f"[WARNING] JavaScript 이벤트 클릭 실패: {e}")
                    
                    if not click_success:
                        print("[ERROR] 모든 클릭 방법 실패")
                        driver.switch_to.default_content()
                        break  # iframe 루프 종료, 재시도로
                    
                    # 클릭 후 대기 (체크박스가 체크될 때까지)
                    print("[INFO] 클릭 후 대기 중...")
                    time.sleep(random.uniform(2, 4))
                    
                    # 체크박스가 체크되었는지 확인 (여러 번 확인, 최대 5초 대기)
                    for check_attempt in range(5):
                        try:
                            # aria-checked 속성 확인
                            aria_checked = checkbox.get_attribute('aria-checked')
                            if aria_checked == 'true':
                                print("[SUCCESS] reCAPTCHA 체크박스가 자동으로 클릭되었습니다!")
                                driver.switch_to.default_content()
                                return True
                            
                            # 클래스에 checked가 있는지 확인
                            checkbox_class = checkbox.get_attribute('class') or ''
                            if 'checked' in checkbox_class.lower() and 'unchecked' not in checkbox_class.lower():
                                print("[SUCCESS] reCAPTCHA 체크박스가 자동으로 클릭되었습니다!")
                                driver.switch_to.default_content()
                                return True
                            
                            # recaptcha-checkbox-checked 클래스 확인
                            if 'recaptcha-checkbox-checked' in checkbox_class.lower():
                                print("[SUCCESS] reCAPTCHA 체크박스가 자동으로 클릭되었습니다!")
                                driver.switch_to.default_content()
                                return True
                        except Exception as e:
                            print(f"[WARNING] 체크 상태 확인 실패 (시도 {check_attempt + 1}/5): {e}")
                        
                        # 추가 대기 후 다시 확인
                        if check_attempt < 4:
                            time.sleep(random.uniform(1, 2))
                    
                    # iframe에서 나오기
                    driver.switch_to.default_content()
                    
                    # 체크박스 클릭 후 추가 대기 (서버 응답 대기)
                    time.sleep(random.uniform(2, 3))
                    
                    # 최종 확인: 캡차가 해결되었는지 확인
                    if not check_captcha(driver):
                        print("[SUCCESS] reCAPTCHA가 해결된 것으로 보입니다.")
                        return True
                    
                    # 성공하지 못했지만 체크박스를 찾았으므로 iframe 루프 종료
                    break
                    
                except Exception as e:
                    # iframe 전환 실패 시 기본 컨텍스트로 돌아가기
                    print(f"[WARNING] iframe 처리 중 오류: {e}")
                    try:
                        driver.switch_to.default_content()
                    except:
                        pass
                    continue  # 다음 iframe 시도
            
            # 체크박스를 찾지 못한 경우
            if not checkbox_found:
                print(f"[WARNING] 체크박스를 찾을 수 없습니다. (재시도 {retry + 1}/{max_retries})")
                # 이미지 선택 챌린지 확인
                if _check_image_challenge(driver):
                    return False
                # 재시도 가능하면 계속
                if retry < max_retries - 1:
                    continue
                return False
            
            # 이미지 선택 챌린지 확인 (체크박스를 찾았지만 실패한 경우)
            if _check_image_challenge(driver):
                return False
            
            # 재시도 가능하면 계속
            if retry < max_retries - 1:
                print(f"[INFO] 재시도 준비 중... (재시도 {retry + 1}/{max_retries - 1})")
                continue
            
        except Exception as e:
            # 재시도 루프 내부의 예외 처리
            print(f"[WARNING] reCAPTCHA 자동 해결 시도 중 오류 (재시도 {retry + 1}/{max_retries}): {e}")
            try:
                driver.switch_to.default_content()
            except:
                pass
            
            if retry < max_retries - 1:
                continue  # 다음 재시도로
            else:
                return False
    
    # 모든 재시도 실패 (루프를 모두 돌았지만 해결하지 못한 경우)
    print(f"[ERROR] reCAPTCHA 체크박스를 {max_retries}번 시도했지만 해결하지 못했습니다.")
    return False


def is_coupang_product_url(url: str) -> bool:
    """
    쿠팡 상품 URL인지 확인합니다.
    
    Args:
        url: 확인할 URL
        
    Returns:
        쿠팡 상품 URL이면 True, 아니면 False
    """
    if not url:
        return False
    
    # Google 검색 URL 제외
    if 'google.com' in url or 'google.co.kr' in url:
        return False
    
    # 쿠팡 상품 URL만 필터링 (정확히 https://www.coupang.com/vp/products/ 숫자 형태)
    # 예: https://www.coupang.com/vp/products/1339476692
    pattern = r'^https?://(www\.)?coupang\.com/vp/products/\d+'
    return bool(re.search(pattern, url))


def extract_products_from_page(driver, products: List[Dict[str, str]]) -> int:
    """
    현재 페이지에서 쿠팡 상품 정보를 추출합니다.
    제한 없이 모든 상품을 추출합니다.
    
    Args:
        driver: Selenium WebDriver
        products: 상품 정보 리스트 (추가될 리스트)
        
    Returns:
        이 페이지에서 추출한 상품 개수
    """
    page_products_count = 0
    
    try:
        # 검색 결과 요소 찾기
        search_results = driver.find_elements(By.CSS_SELECTOR, 'div.MjjYud, div.g')
        
        for result in search_results:
            try:
                # 링크 요소 찾기
                link_elem = result.find_element(By.CSS_SELECTOR, 'a[href*="coupang.com/vp/products/"]')
                if not link_elem:
                    continue
                
                # URL 추출
                href = link_elem.get_attribute('href')
                if not href:
                    continue
                
                # Google 리다이렉트 URL 처리
                if '/url?q=' in href:
                    url_part = href.split('/url?q=')[1].split('&')[0]
                    href = urllib.parse.unquote(url_part)
                
                # 쿠팡 상품 URL인지 확인
                if not is_coupang_product_url(href):
                    continue
                
                # URL 정규화
                clean_url = href.split('?')[0].split('&')[0]
                match = re.search(r'(https?://(www\.)?coupang\.com/vp/products/\d+)', clean_url)
                if not match:
                    continue
                
                product_url = match.group(1)
                
                # 이미 추가된 URL인지 확인 (중복 제거)
                if any(p['URL'] == product_url for p in products):
                    continue
                
                # 제목 추출 (h3 태그)
                title = ""
                try:
                    # h3.LC20lb 클래스가 Google 검색 결과의 제목입니다
                    title_elem = result.find_element(By.CSS_SELECTOR, 'h3.LC20lb, h3.MBeuO, h3.DKV0Md')
                    if title_elem:
                        title = title_elem.text.strip()
                except:
                    # h3 태그를 직접 찾기
                    try:
                        title_elem = result.find_element(By.TAG_NAME, 'h3')
                        if title_elem:
                            title = title_elem.text.strip()
                    except:
                        pass
                
                # 제목이 없거나 너무 짧으면 건너뛰기
                if not title or len(title) < 3:
                    # 제목이 없어도 URL은 추가 (나중에 제목 추출 가능)
                    title = "(제목 없음)"
                
                # 제목 정리 (줄임표 제거 등)
                title = title.replace('...', '').strip()
                
                # 상품평 개수 추출
                review_count = None
                try:
                    result_text = result.text
                    result_html = result.get_attribute('innerHTML') or ""
                    
                    # 패턴 1: "상품평 (4,745)" - 괄호 안의 숫자
                    review_match = re.search(r'상품평\s*\(([\d,]+)\)', result_text, re.IGNORECASE)
                    if not review_match:
                        review_match = re.search(r'상품평\s*\(([\d,]+)\)', result_html, re.IGNORECASE)
                    
                    # 패턴 2: ". 8,558 개 상품평" - 점 뒤 숫자
                    if not review_match:
                        review_match = re.search(r'\.\s*([\d,]+)\s*개\s*(?:<em>)?상품평(?:</em>)?', result_text, re.IGNORECASE)
                    if not review_match:
                        review_match = re.search(r'\.\s*([\d,]+)\s*개\s*(?:<em>)?상품평(?:</em>)?', result_html, re.IGNORECASE)
                    
                    # 패턴 3: "64 개 상품평" - 기본 패턴
                    if not review_match:
                        review_match = re.search(r'(\d+)\s*개\s*(?:<em>)?상품평(?:</em>)?', result_text, re.IGNORECASE)
                    if not review_match:
                        review_match = re.search(r'(\d+)\s*개\s*(?:<em>)?상품평(?:</em>)?', result_html, re.IGNORECASE)
                    
                    if review_match:
                        review_count = review_match.group(1).replace(',', '')  # 콤마 제거
                except:
                    pass
                
                # 카테고리 추출
                category = None
                try:
                    result_text = result.text
                    result_html = result.get_attribute('innerHTML') or ""
                    
                    # 패턴: "이 상품과 관련된 카테고리. 액체섬유유연제 · 회사소개..."
                    category_match = re.search(r'이\s*상품과\s*관련된\s*카테고리\.\s*([^·\n<]+)', result_text, re.IGNORECASE)
                    if not category_match:
                        category_match = re.search(r'이\s*상품과\s*관련된\s*카테고리\.\s*([^·\n<]+)', result_html, re.IGNORECASE)
                    
                    if category_match:
                        category = category_match.group(1).strip()
                        # 불필요한 문자 제거
                        category = re.sub(r'\s+', ' ', category)  # 여러 공백을 하나로
                        category = category.strip()
                except:
                    pass
                
                # productID 추출 (URL에서)
                product_id = None
                try:
                    product_id_match = re.search(r'/vp/products/(\d+)', product_url)
                    if product_id_match:
                        product_id = product_id_match.group(1)
                except:
                    pass
                
                # 상품 추가
                products.append({
                    'URL': product_url,
                    '제목': title,
                    '상품평': review_count,
                    '카테고리': category,
                    'productID': product_id
                })
                page_products_count += 1
                print(f"  [{len(products)}] {title}")
                print(f"      URL: {product_url}")
                if product_id:
                    print(f"      productID : {product_id}")
                if review_count:
                    print(f"      상품평 : {review_count} 개")
                else:
                    print(f"      상품평 : -")
                if category:
                    print(f"      카테고리 : {category}")
                else:
                    print(f"      카테고리 : -")
            
            except Exception as e:
                # 이 검색 결과에서 정보를 추출하지 못했지만 계속 진행
                continue
        
        # 방법 2: 페이지 소스에서 직접 추출 (방법 1이 실패한 경우)
        if page_products_count == 0:
            print("[INFO] 페이지 소스에서 직접 추출 시도...")
            try:
                page_source = driver.page_source
                soup = BeautifulSoup(page_source, 'lxml')
                
                # 검색 결과 컨테이너 찾기
                result_containers = soup.find_all('div', class_='MjjYud') or soup.find_all('div', class_='g')
                
                for container in result_containers:
                    try:
                        # 링크 찾기
                        link = container.find('a', href=re.compile(r'coupang\.com/vp/products/\d+'))
                        if not link:
                            continue
                        
                        href = link.get('href', '')
                        if not href:
                            continue
                        
                        # Google 리다이렉트 URL 처리
                        if '/url?q=' in href:
                            url_part = href.split('/url?q=')[1].split('&')[0]
                            href = urllib.parse.unquote(url_part)
                        
                        # 쿠팡 상품 URL인지 확인
                        if not is_coupang_product_url(href):
                            continue
                        
                        # URL 정규화
                        clean_url = href.split('?')[0].split('&')[0]
                        match = re.search(r'(https?://(www\.)?coupang\.com/vp/products/\d+)', clean_url)
                        if not match:
                            continue
                        
                        product_url = match.group(1)
                        
                        # 이미 추가된 URL인지 확인
                        if any(p['URL'] == product_url for p in products):
                            continue
                        
                        # 제목 추출
                        title = ""
                        title_elem = container.find('h3', class_=re.compile(r'LC20lb|MBeuO|DKV0Md'))
                        if not title_elem:
                            title_elem = container.find('h3')
                        
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                            title = title.replace('...', '').strip()
                        
                        if not title:
                            title = "(제목 없음)"
                        
                        # 상품평 개수 추출
                        review_count = None
                        try:
                            container_text = container.get_text()
                            container_html = str(container)
                            
                            # 패턴 1: "상품평 (4,745)" - 괄호 안의 숫자
                            review_match = re.search(r'상품평\s*\(([\d,]+)\)', container_text, re.IGNORECASE)
                            if not review_match:
                                review_match = re.search(r'상품평\s*\(([\d,]+)\)', container_html, re.IGNORECASE)
                            
                            # 패턴 2: ". 8,558 개 상품평" - 점 뒤 숫자
                            if not review_match:
                                review_match = re.search(r'\.\s*([\d,]+)\s*개\s*(?:<em>)?상품평(?:</em>)?', container_text, re.IGNORECASE)
                            if not review_match:
                                review_match = re.search(r'\.\s*([\d,]+)\s*개\s*(?:<em>)?상품평(?:</em>)?', container_html, re.IGNORECASE)
                            
                            # 패턴 3: "64 개 상품평" - 기본 패턴
                            if not review_match:
                                review_match = re.search(r'(\d+)\s*개\s*(?:<em>)?상품평(?:</em>)?', container_text, re.IGNORECASE)
                            if not review_match:
                                review_match = re.search(r'(\d+)\s*개\s*(?:<em>)?상품평(?:</em>)?', container_html, re.IGNORECASE)
                            
                            if review_match:
                                review_count = review_match.group(1).replace(',', '')  # 콤마 제거
                        except:
                            pass
                        
                        # 카테고리 추출
                        category = None
                        try:
                            container_text = container.get_text()
                            container_html = str(container)
                            
                            # 패턴: "이 상품과 관련된 카테고리. 액체섬유유연제 · 회사소개..."
                            category_match = re.search(r'이\s*상품과\s*관련된\s*카테고리\.\s*([^·\n<]+)', container_text, re.IGNORECASE)
                            if not category_match:
                                category_match = re.search(r'이\s*상품과\s*관련된\s*카테고리\.\s*([^·\n<]+)', container_html, re.IGNORECASE)
                            
                            if category_match:
                                category = category_match.group(1).strip()
                                # 불필요한 문자 제거
                                category = re.sub(r'\s+', ' ', category)  # 여러 공백을 하나로
                                category = category.strip()
                        except:
                            pass
                        
                        # productID 추출 (URL에서)
                        product_id = None
                        try:
                            product_id_match = re.search(r'/vp/products/(\d+)', product_url)
                            if product_id_match:
                                product_id = product_id_match.group(1)
                        except:
                            pass
                        
                        # 상품 추가
                        products.append({
                            'URL': product_url,
                            '제목': title,
                            '상품평': review_count,
                            '카테고리': category,
                            'productID': product_id
                        })
                        page_products_count += 1
                        print(f"  [{len(products)}] {title}")
                        print(f"      URL: {product_url}")
                        if product_id:
                            print(f"      productID : {product_id}")
                        if review_count:
                            print(f"      상품평 : {review_count} 개")
                        else:
                            print(f"      상품평 : -")
                        if category:
                            print(f"      카테고리 : {category}")
                        else:
                            print(f"      카테고리 : -")
                    except:
                        continue
            except Exception as e:
                print(f"[WARNING] 페이지 소스에서 추출 실패: {e}")
    
    except Exception as e:
        print(f"[ERROR] 페이지 추출 오류: {e}")
    
    return page_products_count


def extract_coupang_products_from_google_with_driver(driver, query: str, table_name: str = None, save_to_db: bool = False) -> List[Dict[str, str]]:
    """
    Google 검색 결과에서 쿠팡 상품 URL과 제목을 함께 추출합니다.
    기존 드라이버를 사용하여 검색을 수행합니다.
    1페이지부터 시작해서 다음 페이지 버튼을 클릭하며 마지막 페이지까지 모든 데이터를 수집합니다.
    
    Args:
        driver: 기존 WebDriver 인스턴스 (재사용)
        query: 검색 쿼리
        table_name: DB 테이블명 (선택적)
        save_to_db: DB에 저장할지 여부
        
    Returns:
        쿠팡 상품 정보 리스트 (URL과 제목 포함)
    """
    products = []
    
    try:
        # 검색 쿼리 인코딩
        encoded_query = urllib.parse.quote_plus(query)
        
        # 첫 페이지 URL
        search_url = f"https://www.google.com/search?q={encoded_query}&hl=ko"
        
        print(f"검색 중: {query}")
        print(f"목표: 마지막 페이지까지 모든 상품 수집")
        print()
        
        page_num = 1
        max_pages = 1000  # 충분히 큰 값으로 설정 (무한 루프 방지)
        
        # 첫 페이지 로드
        print(f"[페이지 {page_num}] 로드 중...")
        driver.get(search_url)
        
        # 페이지 로딩 대기 (사람처럼 자연스러운 시간)
        wait_time = human_like_wait(base_min=15.0, base_max=45.0)
        print(f"  페이지 로딩 대기 중... ({wait_time:.1f}초)")
        
        while page_num <= max_pages:
            # 페이지 로딩 대기 (사람처럼 자연스러운 시간)
            wait_time = human_like_wait(base_min=15.0, base_max=45.0)
            
            # 캡차 확인 (더 정확한 방법)
            is_captcha = check_captcha(driver)
            
            if is_captcha:
                print("[WARNING] ⚠️  Google이 봇을 감지했습니다!")
                print("[INFO] reCAPTCHA 자동 해결 시도 중...")
                print()
                
                # reCAPTCHA 자동 해결 시도
                auto_solved = try_auto_solve_recaptcha(driver)
                
                if auto_solved:
                    # 자동 해결 성공
                    print("[SUCCESS] reCAPTCHA가 자동으로 해결되었습니다!")
                    print("[INFO] 캡차 해결 확인 중...")
                    
                    # 캡차 해결 후 대기 (서버 응답 대기)
                    wait_time = random.uniform(3.0, 6.0)
                    print(f"  대기 중... ({wait_time:.1f}초)")
                    time.sleep(wait_time)
                    
                    # 페이지가 자동으로 새로고침되었는지 확인
                    # reCAPTCHA 체크 후 Google이 자동으로 검색 결과 페이지로 리다이렉트할 수 있음
                    current_url = driver.current_url
                    
                    # 여전히 캡차가 있는지 확인
                    is_captcha_still = check_captcha(driver)
                    
                    if is_captcha_still:
                        # 여전히 캡차가 있으면 이미지 선택 챌린지일 수 있음
                        print("[WARNING] 캡차가 아직 남아있습니다.")
                        print("[INFO] 이미지 선택 챌린지가 나타났을 수 있습니다.")
                        print("[INFO] 수동 해결이 필요합니다.")
                        
                        # 사용자가 캡차를 해결할 때까지 대기
                        input("  캡차를 해결한 후 Enter 키를 누르세요... ")
                        
                        # 캡차 해결 후 대기 (사람처럼 자연스러운 시간)
                        print("[INFO] 캡차 해결 확인 중...")
                        refresh_wait = human_like_wait(base_min=10.0, base_max=30.0)
                        
                        # 페이지 새로고침
                        try:
                            driver.refresh()
                            wait_time = human_like_wait(base_min=15.0, base_max=45.0)
                        except:
                            pass
                        
                        # 여전히 캡차가 있는지 확인
                        is_captcha_still = check_captcha(driver)
                        if is_captcha_still:
                            print("[ERROR] 캡차가 해결되지 않았습니다.")
                            print("[TIP] 다음을 시도해보세요:")
                            print("  1. 브라우저를 완전히 닫고 잠시 후 다시 실행")
                            print("  2. 다른 IP 주소에서 시도 (VPN 사용)")
                            print("  3. Chrome 사용자 프로필 디렉토리 삭제 후 다시 시도 (chrome_cookie 폴더)")
                            break
                        else:
                            print("[SUCCESS] 캡차가 해결되었습니다! 계속 진행합니다...")
                            print()
                    else:
                        # 캡차가 해결되었음
                        print("[SUCCESS] 캡차가 해결되었습니다! 계속 진행합니다...")
                        print()
                else:
                    # 자동 해결 실패 (이미지 선택 등이 필요한 경우)
                    print("[INFO] reCAPTCHA 자동 해결 실패 (이미지 선택 등이 필요할 수 있음)")
                    print("[INFO] 브라우저 창이 열려 있습니다.")
                    print("[INFO] 캡차를 수동으로 해결해주세요.")
                    print("[INFO] 캡차 해결 후 터미널에서 Enter 키를 누르면 계속 진행됩니다...")
                    print()
                    
                    # 사용자가 캡차를 해결할 때까지 대기
                    input("  캡차를 해결한 후 Enter 키를 누르세요... ")
                    
                    # 캡차 해결 후 대기 (사람처럼 자연스러운 시간)
                    print("[INFO] 캡차 해결 확인 중...")
                    refresh_wait = human_like_wait(base_min=10.0, base_max=30.0)
                    
                    # 페이지 새로고침
                    driver.refresh()
                    wait_time = human_like_wait(base_min=15.0, base_max=45.0)
                    
                    # 여전히 캡차가 있으면 종료
                    is_captcha_still = check_captcha(driver)
                    
                    if is_captcha_still:
                        print("[ERROR] 캡차가 해결되지 않았습니다.")
                        print("[TIP] 다음을 시도해보세요:")
                        print("  1. 브라우저를 완전히 닫고 잠시 후 다시 실행")
                        print("  2. 다른 IP 주소에서 시도 (VPN 사용)")
                        print("  3. Chrome 사용자 프로필 디렉토리 삭제 후 다시 시도 (chrome_cookie 폴더)")
                        break
                    else:
                        print("[SUCCESS] 캡차가 해결되었습니다! 계속 진행합니다...")
                        print()
            
            # 현재 페이지에서 상품 추출
            print(f"[페이지 {page_num}] 상품 추출 중...")
            before_count = len(products)
            
            # 사람처럼 자연스러운 마우스 움직임
            human_like_mouse_movement(driver)
            
            # 페이지 스크롤 (사람처럼 자연스럽게)
            human_like_scroll(driver)
            
            # 상품 추출 전 자연스러운 대기 (사람이 페이지를 읽는 시간)
            reading_wait = human_like_wait(base_min=10.0, base_max=30.0)
            print(f"  페이지 읽는 중... ({reading_wait:.1f}초)")
            
            # 상품 추출
            extract_products_from_page(driver, products)
            after_count = len(products)
            page_found = after_count - before_count
            
            print(f"  → {page_found}개 상품 발견 (누적 총 {len(products)}개)")
            
            # 페이지별 DB 저장
            if save_to_db and table_name and page_found > 0:
                print(f"  [DB] 테이블 확인 및 저장 시작: {table_name}")
                new_products = products[before_count:after_count]
                saved_count = save_records_to_db(new_products, table_name)
                if saved_count > 0:
                    print(f"  → DB 저장 완료: {saved_count}건")
                elif saved_count == 0:
                    print(f"  → DB 저장 건너뜀 (중복 또는 오류)")
            elif not save_to_db:
                print(f"  [DB] DB 저장 비활성화됨")
            elif not table_name:
                print(f"  [DB] 테이블명이 없어 DB 저장을 건너뜁니다")
            
            # 상품 추출 후 자연스러운 대기 (사람이 결과를 확인하는 시간)
            review_wait = human_like_wait(base_min=5.0, base_max=20.0)
            print(f"  결과 확인 중... ({review_wait:.1f}초)")
            
            # 다음 페이지 버튼 찾기
            next_button = None
            try:
                # 여러 방법으로 다음 페이지 버튼 찾기
                next_selectors = [
                    'a[aria-label="다음"]',
                    'a#pnnext',
                    'a[aria-label="Next"]',
                    'td[style*="text-align:left"] a',  # 다음 페이지 버튼
                    'a:contains("다음")',
                ]
                
                for selector in next_selectors:
                    try:
                        buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                        if buttons:
                            # 버튼이 보이고 클릭 가능한지 확인
                            for btn in buttons:
                                if btn.is_displayed() and btn.is_enabled():
                                    next_button = btn
                                    break
                            if next_button:
                                break
                    except:
                        continue
                
                # 페이지 하단의 다음 페이지 링크 찾기
                if not next_button:
                    try:
                        # 페이지 소스에서 다음 페이지 URL 찾기
                        page_source = driver.page_source
                        soup = BeautifulSoup(page_source, 'lxml')
                        
                        # "다음" 텍스트를 가진 링크 찾기
                        next_links = soup.find_all('a', string=re.compile(r'다음|Next'))
                        if not next_links:
                            # id가 pnnext인 링크 찾기
                            next_links = soup.find_all('a', id='pnnext')
                        
                        if next_links:
                            next_href = next_links[0].get('href', '')
                            if next_href:
                                if next_href.startswith('/'):
                                    next_url = f"https://www.google.com{next_href}"
                                else:
                                    next_url = next_href
                                print(f"[페이지 {page_num + 1}] 다음 페이지로 이동: {next_url}")
                                driver.get(next_url)
                                
                                # 페이지 로딩 대기 (사람처럼 자연스러운 시간)
                                wait_time = human_like_wait(base_min=15.0, base_max=45.0)
                                print(f"  페이지 로딩 대기 중... ({wait_time:.1f}초)")
                                
                                page_num += 1
                                continue
                    except Exception as e:
                        print(f"  [WARNING] 다음 페이지 URL 찾기 실패: {e}")
                
            except Exception as e:
                print(f"  [WARNING] 다음 페이지 버튼 찾기 실패: {e}")
            
            # 다음 페이지 버튼이 있으면 클릭
            if next_button:
                try:
                    print(f"  [페이지 {page_num}] → [페이지 {page_num + 1}] 다음 페이지로 이동 중...")
                    
                    # 사람처럼 자연스럽게 클릭
                    human_like_click(driver, next_button)
                    
                    # 다음 페이지 로딩 대기 (사람처럼 자연스러운 시간)
                    wait_time = human_like_wait(base_min=15.0, base_max=45.0)
                    print(f"  다음 페이지 로딩 대기 중... ({wait_time:.1f}초)")
                    
                    page_num += 1
                except Exception as e:
                    print(f"  [ERROR] 다음 페이지 버튼 클릭 실패: {e}")
                    # 클릭 실패 시 URL로 직접 이동 시도
                    try:
                        next_href = next_button.get_attribute('href')
                        if next_href:
                            if next_href.startswith('/'):
                                next_url = f"https://www.google.com{next_href}"
                            else:
                                next_url = next_href
                            print(f"[페이지 {page_num + 1}] 다음 페이지로 이동 (URL 직접 사용): {next_url}")
                            driver.get(next_url)
                            
                            # 페이지 로딩 대기 (사람처럼 자연스러운 시간)
                            wait_time = human_like_wait(base_min=15.0, base_max=45.0)
                            print(f"  페이지 로딩 대기 중... ({wait_time:.1f}초)")
                            
                            page_num += 1
                        else:
                            break
                    except:
                        break
            else:
                # 다음 페이지 버튼이 없으면 종료
                print(f"\n[INFO] 더 이상 검색 결과가 없습니다. (총 {page_num}페이지 검색 완료)")
                break
        
        if page_num > max_pages:
            print(f"\n[WARNING] 최대 페이지 수({max_pages}페이지)에 도달했습니다.")
        
        print(f"\n[INFO] 총 {len(products)}개의 쿠팡 상품 정보를 찾았습니다.")
        
    except Exception as e:
        print(f"[ERROR] 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        # 오류 발생 시에도 빈 리스트 반환 (다음 쿼리 계속 처리)
        return []
    
    return products


def extract_coupang_products_from_google(query: str, headless: bool = False) -> List[Dict[str, str]]:
    """
    Google 검색 결과에서 쿠팡 상품 URL과 제목을 함께 추출합니다.
    새로운 드라이버를 생성하여 검색을 수행합니다.
    1페이지부터 시작해서 다음 페이지 버튼을 클릭하며 마지막 페이지까지 모든 데이터를 수집합니다.
    
    Args:
        query: 검색 쿼리
        headless: 헤드리스 모드로 실행할지 여부
        
    Returns:
        쿠팡 상품 정보 리스트 (URL과 제목 포함)
    """
    driver = None
    products = []
    
    try:
        print("[INFO] Chrome 브라우저 시작 중...")
        driver = setup_chrome_driver(headless=headless, use_debugging_port=True, debug_port=9222)
        
        # 기존 드라이버를 사용하여 추출
        products = extract_coupang_products_from_google_with_driver(driver, query)
        
    except Exception as e:
        print(f"[ERROR] 오류 발생: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if driver:
            driver.quit()
            print("\n[INFO] 브라우저 종료됨")
    
    return products




def get_db_connection():
    """MySQL 연결을 생성합니다."""
    if not MYSQL_AVAILABLE:
        raise RuntimeError("pymysql 패키지를 사용할 수 없습니다. 'pip install pymysql'로 설치해주세요.")
    return pymysql.connect(**DB_CONFIG)


def prepare_database() -> bool:
    """DB 연결 가능 여부를 확인합니다."""
    if not MYSQL_AVAILABLE:
        print("[WARNING] pymysql이 설치되어 있지 않아 DB 저장을 건너뜁니다.")
        return False
    try:
        conn = get_db_connection()
        conn.close()
        print("[INFO] DB 연결 확인 완료.")
        return True
    except Exception as exc:
        print(f"[WARNING] DB 연결 실패: {exc}")
        return False


def build_table_name(num: int, date_tag: str) -> str:
    """DB 테이블명을 생성합니다."""
    safe_num = "".join(ch for ch in str(num) if ch.isdigit())
    safe_date = "".join(ch for ch in str(date_tag) if ch.isdigit())
    return f"coupang_products_{safe_num}_{safe_date}"


def ensure_table_exists(table_name: str):
    """테이블이 존재하도록 생성합니다."""
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # 트랜잭션 시작 전에 autocommit 비활성화
            conn.autocommit(False)
            
            # 테이블 존재 여부 확인
            cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
            table_exists = cursor.fetchone()
            
            if not table_exists:
                # 테이블이 없으면 생성
                cursor.execute(
                    f"""
                    CREATE TABLE `{table_name}` (
                        seq BIGINT DEFAULT NULL,
                        url VARCHAR(1024) DEFAULT NULL,
                        title VARCHAR(512) DEFAULT NULL,
                        review VARCHAR(255) DEFAULT NULL,
                        category VARCHAR(512) DEFAULT NULL,
                        star VARCHAR(50) DEFAULT NULL,
                        productID VARCHAR(100) DEFAULT NULL,
                        delivery VARCHAR(100) DEFAULT NULL,
                        price VARCHAR(100) DEFAULT NULL,
                        regidate DATETIME DEFAULT NULL
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
                    """
                )
                print(f"  [DB] 테이블 생성됨: {table_name}")
            
            # 명시적으로 commit
            conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()


def get_existing_product_ids(table_name: str) -> set:
    """테이블에 있는 기존 productID들을 가져옵니다."""
    existing_ids = set()
    conn = None
    try:
        conn = get_db_connection()
        # autocommit 모드로 설정하여 트랜잭션 충돌 방지
        conn.autocommit(True)
        
        with conn.cursor() as cursor:
            cursor.execute(f"SELECT DISTINCT productID FROM `{table_name}` WHERE productID IS NOT NULL")
            results = cursor.fetchall()
            if results:
                if isinstance(results[0], dict):
                    existing_ids = {str(row['productID']) for row in results if row.get('productID')}
                else:
                    existing_ids = {str(row[0]) for row in results if row[0]}
    except Exception as e:
        print(f"  [DB] 기존 productID 조회 중 오류: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if conn:
            conn.close()
    return existing_ids


def _fetch_scalar(row) -> int:
    """쿼리 결과에서 스칼라 값을 추출합니다."""
    if row is None:
        return 0
    if isinstance(row, dict):
        return next(iter(row.values()))
    return row[0]


def save_records_to_db(records: List[Dict[str, Any]], table_name: str) -> int:
    """상품 정보를 MySQL에 저장합니다."""
    if not records:
        print(f"  [DB] 저장할 레코드가 없습니다.")
        return 0
    if not MYSQL_AVAILABLE:
        print("[WARNING] pymysql이 없어 DB 저장을 건너뜁니다.")
        return 0
    try:
        print(f"  [DB] 테이블 확인 중: {table_name}")
        ensure_table_exists(table_name)
        print(f"  [DB] 테이블 확인 완료: {table_name}")
        
        # 테이블 생성 후 메타데이터 반영을 위한 짧은 대기
        import time
        time.sleep(0.1)
        
        conn = get_db_connection()
        
        # 기존 productID 가져오기 (중복 체크용)
        print(f"  [DB] 기존 productID 조회 중...")
        existing_ids = get_existing_product_ids(table_name)
        print(f"  [DB] 기존 productID 개수: {len(existing_ids)}개")
        
        # 중복이 아닌 레코드만 필터링
        new_records = []
        duplicate_count = 0
        for record in records:
            product_id = record.get('productID')
            if product_id and str(product_id) in existing_ids:
                duplicate_count += 1
                continue
            new_records.append(record)
            if product_id:
                existing_ids.add(str(product_id))
        
        if duplicate_count > 0:
            print(f"  [DB] 중복 상품: {duplicate_count}개 발견")
        
        if not new_records:
            conn.close()
            print(f"  [DB] 중복된 상품만 발견되어 DB 저장을 건너뜁니다.")
            return 0
        
        print(f"  [DB] 새로 저장할 레코드: {len(new_records)}개")
        
        try:
            with conn.cursor() as cursor:
                # autocommit 비활성화 (트랜잭션 사용)
                conn.autocommit(False)
                
                # 마지막 row 조회해서 seq와 regidate 확인
                print(f"  [DB] 마지막 row 조회 중...")
                cursor.execute(f"SELECT seq, regidate FROM `{table_name}` ORDER BY seq DESC LIMIT 1")
                last_row = cursor.fetchone()
                
                if last_row and last_row.get('seq') is not None:
                    # seq가 있으면 다음 번호로
                    start_seq = int(last_row.get('seq')) + 1
                    print(f"  [DB] 마지막 seq: {int(last_row.get('seq'))}, 새로 시작할 seq: {start_seq}")
                else:
                    # seq가 null이면 1부터 시작
                    start_seq = 1
                    print(f"  [DB] seq가 없어 1부터 시작합니다.")
                
                # 현재 날짜와 시간 (초시분초 포함)
                now_datetime = datetime.now()
                
                sql = f"""
                    INSERT INTO `{table_name}` (seq, url, title, review, category, star, productID, delivery, price, regidate)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                data_with_seq = [
                    (
                        start_seq + idx,
                        record.get('URL'),
                        record.get('제목'),
                        f"{record.get('상품평')} 개" if record.get('상품평') else None,  # review (형식: "4745 개" 또는 None)
                        record.get('카테고리') if record.get('카테고리') else None,  # category
                        None,  # star
                        record.get('productID'),
                        None,  # delivery
                        None,  # price
                        now_datetime,  # regidate (DATETIME: 초시분초 포함)
                    )
                    for idx, record in enumerate(new_records)
                ]
                cursor.executemany(sql, data_with_seq)
                
                # 명시적으로 commit
                conn.commit()
                print(f"  [DB] INSERT 완료, commit 완료")
                
                # commit 후 실제 저장된 개수 확인
                cursor.execute(f"SELECT COUNT(*) as cnt FROM `{table_name}`")
                total_count = cursor.fetchone()
                if total_count:
                    if isinstance(total_count, dict):
                        total_rows = total_count.get('cnt', 0)
                    else:
                        total_rows = total_count[0]
                    print(f"  [DB] 테이블 총 행 수: {total_rows}개 (방금 저장: {len(new_records)}개)")
        except Exception as e:
            # 오류 발생 시 rollback
            if conn:
                conn.rollback()
            print(f"  [DB] 트랜잭션 오류 발생, rollback 실행: {e}")
            import traceback
            traceback.print_exc()
            raise
        finally:
            # 연결 확실히 닫기
            if conn:
                conn.close()
                print(f"  [DB] DB 연결 종료")
        print(f"[INFO] DB에 {len(new_records)}개 행을 저장했습니다. (테이블: {table_name})")
        return len(new_records)
    except Exception as exc:
        print(f"[WARNING] DB 저장 중 오류: {exc}")
        import traceback
        traceback.print_exc()
        return 0


def get_search_queries():
    """
    검색할 쿼리 리스트를 생성합니다.
    100, 200, 300, ..., 1000 (100 단위)
    2000, 3000, ..., 10000 (1000 단위, 1만)
    20000, 30000, ..., 200000 (10000 단위, 2만~20만)
    
    Returns:
        검색 숫자 리스트
    """
    queries = []
    
    # 100부터 1000까지 (100 단위)
    # 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000
    for num in range(100, 1000 + 1, 100):
        queries.append(num)
    
    # 2000부터 10000까지 (1000 단위)
    # 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000 (1만)
    for num in range(2000, 10000 + 1, 1000):
        queries.append(num)
    
    # 20000부터 200000까지 (10000 단위)
    # 20000 (2만), 30000 (3만), 40000 (4만), 50000 (5만), 60000 (6만), ..., 200000 (20만)
    for num in range(20000, 200000 + 1, 10000):
        queries.append(num)
    
    return queries


def main():
    """메인 함수"""
    print("=" * 60)
    print("쿠팡 상품 URL 및 제목 추출 시작")
    print("=" * 60)
    print()
    
    # 전체 검색 쿼리 리스트 생성
    all_search_numbers = get_search_queries()
    print(f"[INFO] 전체 검색 가능 범위: {all_search_numbers[0]} ~ {all_search_numbers[-1]}")
    print(f"[INFO] 가능한 검색 숫자: {', '.join(map(str, all_search_numbers[:10]))}... (총 {len(all_search_numbers)}개)")
    print()
    
    # 시작 숫자 입력 받기
    while True:
        try:
            user_input = input("몇부터 검색할까요? (엔터만 누르면 처음부터 시작): ").strip()
            
            if not user_input:
                # 엔터만 누르면 처음부터 시작
                start_num = all_search_numbers[0]
                break
            
            start_num = int(user_input)
            
            # 입력한 숫자가 검색 가능한 리스트에 있는지 확인
            if start_num in all_search_numbers:
                break
            else:
                # 입력한 숫자보다 크거나 같은 첫 번째 숫자 찾기
                filtered = [num for num in all_search_numbers if num >= start_num]
                if filtered:
                    start_num = filtered[0]
                    print(f"[INFO] {user_input}은(는) 검색 가능한 숫자가 아닙니다.")
                    print(f"[INFO] {start_num}부터 시작합니다.")
                    break
                else:
                    print(f"[WARNING] {user_input}보다 크거나 같은 검색 가능한 숫자가 없습니다.")
                    print(f"[INFO] 가능한 범위: {all_search_numbers[0]} ~ {all_search_numbers[-1]}")
                    continue
                    
        except ValueError:
            print("[ERROR] 숫자만 입력해주세요.")
            continue
        except KeyboardInterrupt:
            print("\n[INFO] 사용자가 취소했습니다.")
            return
    
    # 시작 숫자부터 필터링
    search_numbers = [num for num in all_search_numbers if num >= start_num]
    
    print()
    print(f"[INFO] 검색 시작 숫자: {start_num}")
    print(f"[INFO] 검색할 쿼리 개수: {len(search_numbers)}개")
    if search_numbers:
        print(f"[INFO] 검색 범위: {search_numbers[0]} ~ {search_numbers[-1]}")
    print()
    
    # 헤드리스 모드 여부 (False면 브라우저가 보임)
    headless_mode = False
    
    # DB 연결 확인
    db_ready = prepare_database()
    if db_ready:
        print()
    
    # 오늘 날짜 태그
    today_tag = datetime.now().strftime("%Y%m%d")
    
    # 각 쿼리별로 처리
    total_processed = 0
    total_products = 0
    driver = None
    
    try:
        # 브라우저는 한 번만 시작 (모든 쿼리에서 재사용)
        print("[INFO] Chrome 브라우저 시작 중...")
        driver = setup_chrome_driver(headless=headless_mode, use_debugging_port=True, debug_port=9222)
        print()
        
        for idx, num in enumerate(search_numbers, 1):
            # 검색 쿼리 생성 (-원산지를 맨 뒤로)
            query = f'site:coupang.com/vp/products/ "한 달간 {num} 명 이상 구매했어요" "상품평" "카테고리" -원산지'
            table_name = build_table_name(num, today_tag) if db_ready else None
            
            print("=" * 60)
            print(f"[{idx}/{len(search_numbers)}] 쿼리 {num} 처리 시작")
            print("=" * 60)
            print(f"검색 쿼리: {query}")
            if table_name:
                print(f"DB 테이블: {table_name}")
            print()
            
            try:
                # Google 검색 결과에서 쿠팡 상품 URL과 제목을 함께 추출
                # 브라우저 재사용 (매번 새로 시작하지 않음), 페이지별 DB 저장
                products = extract_coupang_products_from_google_with_driver(
                    driver, 
                    query,
                    table_name=table_name,
                    save_to_db=db_ready
                )
                
                # 결과 확인
                if not products:
                    print(f"\n[WARNING] 쿠팡 상품 정보를 찾지 못했습니다. (쿼리: {num})")
                    print()
                    continue
                
                # 결과 요약
                print(f"\n[SUCCESS] 쿼리 {num} 완료: {len(products)}개 상품 발견")
                total_processed += 1
                total_products += len(products)
                
            except Exception as e:
                print(f"\n[ERROR] 쿼리 {num} 처리 중 오류 발생: {e}")
                import traceback
                traceback.print_exc()
                print()
                # 오류가 발생해도 다음 쿼리 계속 처리
                continue
            
            print()
            
    finally:
        # 모든 쿼리 처리 후 브라우저 종료
        if driver:
            try:
                driver.quit()
                print("\n[INFO] 브라우저 종료됨")
            except:
                pass
    
    # 전체 결과 요약
    print("=" * 60)
    print("전체 처리 결과")
    print("=" * 60)
    print(f"처리된 쿼리: {total_processed}개")
    print(f"총 상품 수: {total_products}개")
    print("=" * 60)


if __name__ == "__main__":
    main()