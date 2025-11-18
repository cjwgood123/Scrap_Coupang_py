"""
쿠팡 상품 URL 추출 스크립트 (Selenium 버전)
Google 검색을 통해 쿠팡 상품 페이지 URL을 추출합니다.
Selenium을 사용하여 브라우저를 실행하므로 더 안정적으로 작동합니다.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import urllib.parse
import re
from typing import List, Set


def setup_chrome_driver(headless: bool = False):
    """
    Chrome 드라이버를 설정합니다.
    
    Args:
        headless: 헤드리스 모드로 실행할지 여부
        
    Returns:
        Chrome WebDriver 인스턴스
    """
    chrome_options = Options()
    
    if headless:
        chrome_options.add_argument('--headless')
    
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        # 봇 감지 방지
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            '''
        })
        return driver
    except Exception as e:
        print(f"[ERROR] Chrome 드라이버 설정 오류: {e}")
        print("[TIP] Chrome 브라우저가 설치되어 있는지 확인하세요.")
        print("[TIP] 또는 chromedriver가 PATH에 있는지 확인하세요.")
        raise


def extract_url_from_google_link(href: str) -> str:
    """
    Google 검색 결과 링크에서 실제 URL을 추출합니다.
    
    Args:
        href: Google 검색 결과의 href 속성 값
        
    Returns:
        실제 URL 또는 빈 문자열
    """
    if not href:
        return ""
    
    # Google 리다이렉트 URL 처리 (/url?q=...)
    if '/url?q=' in href:
        url_part = href.split('/url?q=')[1].split('&')[0]
        return urllib.parse.unquote(url_part)
    
    # 직접 URL인 경우
    if href.startswith('http'):
        return href
    
    return ""


def get_google_search_urls_selenium(query: str, num_results: int = 10, headless: bool = False) -> List[str]:
    """
    Selenium을 사용하여 Google 검색 결과에서 URL을 추출합니다.
    
    Args:
        query: 검색 쿼리
        num_results: 가져올 결과 개수
        headless: 헤드리스 모드로 실행할지 여부
        
    Returns:
        URL 리스트
    """
    driver = None
    urls: Set[str] = set()
    
    try:
        print("[INFO] Chrome 브라우저 시작 중...")
        driver = setup_chrome_driver(headless=headless)
        
        # 검색 쿼리 인코딩
        encoded_query = urllib.parse.quote_plus(query)
        search_url = f"https://www.google.com/search?q={encoded_query}&num={num_results}&hl=ko"
        
        print(f"검색 중: {query}")
        print(f"검색 URL: {search_url}\n")
        
        driver.get(search_url)
        time.sleep(3)  # 페이지 로딩 대기
        
        # 캡차 확인
        page_text = driver.page_source.lower()
        if 'captcha' in page_text or 'unusual traffic' in page_text:
            print("[WARNING] Google이 봇을 감지했습니다. 잠시 대기 후 다시 시도하세요.")
            time.sleep(5)
        
        # 검색 결과 요소 찾기
        # Google 검색 결과는 여러 가지 선택자로 찾을 수 있습니다
        wait = WebDriverWait(driver, 10)
        
        # 방법 1: 검색 결과 링크 직접 찾기
        try:
            # Google 검색 결과의 링크는 보통 <a> 태그 안에 있습니다
            links = driver.find_elements(By.CSS_SELECTOR, 'a[href*="coupang.com/vp/products/"]')
            
            for link in links:
                href = link.get_attribute('href')
                if href:
                    actual_url = extract_url_from_google_link(href)
                    if actual_url and 'coupang.com/vp/products/' in actual_url:
                        clean_url = actual_url.split('&sa=')[0].split('?utm_')[0]
                        urls.add(clean_url)
                        print(f"  발견: {clean_url}")
        except Exception as e:
            print(f"방법 1 실패: {e}")
        
        # 방법 2: 모든 링크에서 쿠팡 URL 찾기
        if not urls:
            print("방법 1 실패, 방법 2 시도 중...")
            try:
                all_links = driver.find_elements(By.TAG_NAME, 'a')
                for link in all_links:
                    href = link.get_attribute('href')
                    if href and 'coupang.com/vp/products/' in href:
                        actual_url = extract_url_from_google_link(href)
                        if actual_url:
                            clean_url = actual_url.split('&sa=')[0].split('?utm_')[0]
                            urls.add(clean_url)
                            print(f"  발견: {clean_url}")
            except Exception as e:
                print(f"방법 2 실패: {e}")
        
        # 방법 3: 페이지 소스에서 정규표현식으로 찾기
        if not urls:
            print("방법 2 실패, 방법 3 시도 중...")
            try:
                page_source = driver.page_source
                pattern = r'https?://[^\s"<>]+coupang\.com/vp/products/[^\s"<>]+'
                found_urls = re.findall(pattern, page_source)
                for url in found_urls:
                    clean_url = url.split('&')[0].split('"')[0].split("'")[0]
                    if 'coupang.com/vp/products/' in clean_url:
                        urls.add(clean_url)
                        print(f"  발견: {clean_url}")
            except Exception as e:
                print(f"방법 3 실패: {e}")
        
        time.sleep(2)  # 서버 부하를 줄이기 위한 대기
        
    except Exception as e:
        print(f"[ERROR] 오류 발생: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if driver:
            driver.quit()
            print("\n[INFO] 브라우저 종료됨")
    
    return list(urls)


def main():
    """메인 함수"""
    # 검색 쿼리 설정
    query = 'site:coupang.com/vp/products/ "한 달간 100 명 이상 구매했어요"'
    
    print("=" * 60)
    print("쿠팡 상품 URL 추출 시작 (Selenium 버전)")
    print("=" * 60)
    
    # 헤드리스 모드 여부 (False면 브라우저가 보임, True면 백그라운드 실행)
    headless_mode = False  # 디버깅을 위해 False로 설정
    
    # Google 검색 결과에서 URL 추출
    urls = get_google_search_urls_selenium(query, num_results=10, headless=headless_mode)
    
    print("\n" + "=" * 60)
    print(f"총 {len(urls)}개의 URL을 찾았습니다.")
    print("=" * 60)
    
    if urls:
        print("\n추출된 URL 목록:")
        for i, url in enumerate(urls, 1):
            print(f"{i}. {url}")
        
        # URL을 파일에 저장
        with open('coupang_urls.txt', 'w', encoding='utf-8') as f:
            for url in urls:
                f.write(url + '\n')
        print(f"\n[SUCCESS] URL 목록이 'coupang_urls.txt' 파일에 저장되었습니다.")
    else:
        print("\n[WARNING] URL을 찾지 못했습니다.")
        print("[TIP] 검색 결과가 없거나, Google이 접근을 차단했을 수 있습니다.")


if __name__ == "__main__":
    main()

