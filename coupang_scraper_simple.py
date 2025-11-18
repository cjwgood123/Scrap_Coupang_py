"""
쿠팡 상품 URL 추출 스크립트 (간단한 버전)
googlesearch-python 라이브러리를 사용합니다.
"""

from googlesearch import search
import time
from typing import List


def get_coupang_urls_from_google(query: str, num_results: int = 10) -> List[str]:
    """
    Google 검색을 통해 쿠팡 상품 URL을 추출합니다.
    
    Args:
        query: 검색 쿼리
        num_results: 가져올 결과 개수
        
    Returns:
        쿠팡 상품 URL 리스트
    """
    urls = []

    try:
        print(f"검색 중: {query}")
        print(f"최대 {num_results}개의 결과를 가져옵니다...\n")

        # Google 검색 실행
        search_results = search(query, num_results=num_results, lang='ko')

        for url in search_results:
            # 쿠팡 상품 URL만 필터링
            if 'coupang.com/vp/products/' in url:
                urls.append(url)
                print(f"  발견: {url}")

                # 원하는 개수만큼 찾으면 중단
                if len(urls) >= num_results:
                    break

    except Exception as e:
        print(f"[ERROR] 오류 발생: {e}")
        print("[TIP] Google이 접근을 차단했을 수 있습니다.")
        print("[TIP] 잠시 후 다시 시도하거나 Selenium 버전을 사용하세요.")
        import traceback
        traceback.print_exc()

    return urls


def main():
    """메인 함수"""
    # 검색 쿼리 설정
    query = 'site:coupang.com/vp/products/ "한 달간 100 명 이상 구매했어요"'

    print("=" * 60)
    print("쿠팡 상품 URL 추출 시작 (간단한 버전)")
    print("=" * 60)
    print()

    # Google 검색 결과에서 URL 추출
    urls = get_coupang_urls_from_google(query, num_results=10)

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
        print("[TIP] Google이 접근을 차단했을 수 있습니다.")
        print("[TIP] Selenium 버전을 사용해보세요: python coupang_scraper_selenium.py")


if __name__ == "__main__":
    main()