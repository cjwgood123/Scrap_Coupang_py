"""
쿠팡 상품 URL 추출 스크립트
Google 검색을 통해 쿠팡 상품 페이지 URL을 추출합니다.
"""

import requests
from bs4 import BeautifulSoup
import time
import urllib.parse
import re
from typing import List, Set


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
    if href.startswith('/url?q='):
        # /url?q= 뒤의 실제 URL 추출
        url_part = href.split('/url?q=')[1].split('&')[0]
        return urllib.parse.unquote(url_part)
    
    # 직접 URL인 경우
    if href.startswith('http'):
        return href
    
    return ""


def get_google_search_urls(query: str, num_results: int = 10) -> List[str]:
    """
    Google 검색 결과에서 URL을 추출합니다.
    
    Args:
        query: 검색 쿼리
        num_results: 가져올 결과 개수
        
    Returns:
        URL 리스트
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Referer': 'https://www.google.com/',
    }
    
    # 검색 쿼리 인코딩
    encoded_query = urllib.parse.quote_plus(query)
    search_url = f"https://www.google.com/search?q={encoded_query}&num={num_results}&hl=ko"
    
    urls: Set[str] = set()
    
    try:
        print(f"검색 중: {query}")
        print(f"검색 URL: {search_url}\n")
        
        session = requests.Session()
        response = session.get(search_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # 응답 내용 확인 (디버깅용)
        if 'Our systems have detected unusual traffic' in response.text or 'captcha' in response.text.lower():
            print("[WARNING] Google이 봇을 감지했습니다. Selenium 버전을 사용하세요.")
            return list(urls)
        
        soup = BeautifulSoup(response.text, 'lxml')
        
        # 방법 1: 검색 결과 컨테이너에서 링크 추출
        # Google 검색 결과는 보통 div.g 또는 div[data-hveid] 등의 클래스를 가집니다
        search_results = soup.find_all('div', class_=re.compile(r'^g\s|^yuRUbf'))
        
        for result in search_results:
            link_elem = result.find('a', href=True)
            if link_elem:
                href = link_elem.get('href', '')
                actual_url = extract_url_from_google_link(href)
                
                if actual_url and 'coupang.com/vp/products/' in actual_url:
                    # URL 정규화 (쿼리 파라미터 제거 또는 유지)
                    clean_url = actual_url.split('&sa=')[0].split('?utm_')[0]
                    urls.add(clean_url)
                    print(f"  발견: {clean_url}")
        
        # 방법 2: 모든 링크를 확인 (방법 1이 실패한 경우)
        if not urls:
            print("방법 1 실패, 방법 2 시도 중...")
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                actual_url = extract_url_from_google_link(href)
                
                if actual_url and 'coupang.com/vp/products/' in actual_url:
                    clean_url = actual_url.split('&sa=')[0].split('?utm_')[0]
                    if clean_url not in urls:
                        urls.add(clean_url)
                        print(f"  발견: {clean_url}")
        
        # 방법 3: 정규표현식으로 URL 직접 추출
        if not urls:
            print("방법 2 실패, 방법 3 시도 중...")
            pattern = r'https?://[^\s"<>]+coupang\.com/vp/products/[^\s"<>]+'
            found_urls = re.findall(pattern, response.text)
            for url in found_urls:
                clean_url = url.split('&')[0].split('"')[0].split("'")[0]
                if 'coupang.com/vp/products/' in clean_url:
                    urls.add(clean_url)
                    print(f"  발견: {clean_url}")
        
        time.sleep(2)  # 서버 부하를 줄이기 위한 대기
        
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] 요청 오류: {e}")
    except Exception as e:
        print(f"[ERROR] 오류 발생: {e}")
        import traceback
        traceback.print_exc()
    
    return list(urls)


def main():
    """메인 함수"""
    # 검색 쿼리 설정
    query = 'site:coupang.com/vp/products/ "한 달간 100 명 이상 구매했어요"'
    
    print("=" * 60)
    print("쿠팡 상품 URL 추출 시작")
    print("=" * 60)
    
    # Google 검색 결과에서 URL 추출 (최대 10개)
    urls = get_google_search_urls(query, num_results=10)
    
    print("\n" + "=" * 60)
    print(f"총 {len(urls)}개의 URL을 찾았습니다.")
    print("=" * 60)
    
    if urls:
        print("\n추출된 URL 목록:")
        for i, url in enumerate(urls, 1):
            print(f"{i}. {url}")
        
        # URL을 파일에 저장 (선택사항)
        with open('coupang_urls.txt', 'w', encoding='utf-8') as f:
            for url in urls:
                f.write(url + '\n')
        print(f"\nURL 목록이 'coupang_urls.txt' 파일에 저장되었습니다.")
    else:
        print("\nURL을 찾지 못했습니다.")
        print("참고: Google은 봇 접근을 차단할 수 있습니다.")
        print("      Selenium을 사용하는 방법을 고려해보세요.")


if __name__ == "__main__":
    main()

