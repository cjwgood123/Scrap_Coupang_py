"""
쿠팡 상품 URL 추출기 - 통합 실행 스크립트
여러 방법을 순차적으로 시도합니다.
"""

import sys
import subprocess
import os


def try_method_1():
    """방법 1: googlesearch-python 라이브러리 사용"""
    print("=" * 60)
    print("방법 1: googlesearch-python 라이브러리 시도")
    print("=" * 60)
    try:
        from googlesearch import search

        query = 'site:coupang.com/vp/products/ "한 달간 100 명 이상 구매했어요"'
        urls = []

        for url in search(query, num_results=10, lang='ko'):
            if 'coupang.com/vp/products/' in url:
                urls.append(url)
                print(f"  발견: {url}")
                if len(urls) >= 10:
                    break

        if urls:
            save_urls(urls)
            return True
    except Exception as e:
        print(f"[ERROR] 방법 1 실패: {e}")
    return False


def try_method_2():
    """방법 2: requests + BeautifulSoup 사용"""
    print("\n" + "=" * 60)
    print("방법 2: requests + BeautifulSoup 시도")
    print("=" * 60)
    try:
        import coupang_scraper
        urls = coupang_scraper.get_google_search_urls(
            'site:coupang.com/vp/products/ "한 달간 100 명 이상 구매했어요"',
            num_results=10
        )

        if urls:
            save_urls(urls)
            return True
    except Exception as e:
        print(f"[ERROR] 방법 2 실패: {e}")
    return False


def try_method_3():
    """방법 3: Selenium 사용 (권장)"""
    print("\n" + "=" * 60)
    print("방법 3: Selenium 사용 (권장)")
    print("=" * 60)
    print("[INFO] Chrome 브라우저를 실행합니다...")
    print("[INFO] 브라우저가 자동으로 열립니다.")
    try:
        import coupang_scraper_selenium
        urls = coupang_scraper_selenium.get_google_search_urls_selenium(
            'site:coupang.com/vp/products/ "한 달간 100 명 이상 구매했어요"',
            num_results=10,
            headless=False
        )

        if urls:
            save_urls(urls)
            return True
    except Exception as e:
        print(f"[ERROR] 방법 3 실패: {e}")
        print("[TIP] Chrome 브라우저가 설치되어 있는지 확인하세요.")
    return False


def save_urls(urls):
    """URL을 파일에 저장"""
    with open('coupang_urls.txt', 'w', encoding='utf-8') as f:
        for url in urls:
            f.write(url + '\n')
    print(f"\n[SUCCESS] {len(urls)}개의 URL이 'coupang_urls.txt' 파일에 저장되었습니다.")


def main():
    """메인 함수"""
    print("쿠팡 상품 URL 추출기")
    print("=" * 60)
    print()

    # 방법 1 시도
    if try_method_1():
        print("\n[SUCCESS] 방법 1로 URL을 성공적으로 추출했습니다.")
        return

    # 방법 2 시도
    if try_method_2():
        print("\n[SUCCESS] 방법 2로 URL을 성공적으로 추출했습니다.")
        return

    # 방법 3 시도 (가장 확실한 방법)
    print("\n[INFO] 방법 1과 2가 실패했습니다. 방법 3 (Selenium)을 시도합니다...")
    if try_method_3():
        print("\n[SUCCESS] 방법 3으로 URL을 성공적으로 추출했습니다.")
        return

    # 모든 방법 실패
    print("\n" + "=" * 60)
    print("[WARNING] 모든 방법이 실패했습니다.")
    print("=" * 60)
    print("\n가능한 해결 방법:")
    print("1. Chrome 브라우저가 설치되어 있는지 확인")
    print("2. 인터넷 연결 확인")
    print("3. 잠시 후 다시 시도")
    print("4. 수동으로 브라우저에서 검색 후 결과를 복사")


if __name__ == "__main__":
    main()