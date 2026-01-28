"""
한국은행 보도자료 스크래퍼 (Playwright 사용)
JavaScript 렌더링이 필요한 페이지용
"""

from playwright.sync_api import sync_playwright
from datetime import datetime
import json
import re


def fetch_bok_news(config: dict) -> list:
    """한국은행 보도자료 스크래핑"""
    url = config.get('url', 'https://www.bok.or.kr/portal/singl/newsData/list.do?menuNo=201263&pageUnit=20')

    articles = []

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=30000)
            page.wait_for_timeout(3000)  # JS 렌더링 대기

            # 뉴스 링크들 찾기
            links = page.query_selector_all('a[href*="view.do"], a[href*="nttId"]')

            seen_titles = set()
            for link in links:
                try:
                    title = link.inner_text().strip()
                    href = link.get_attribute('href')

                    # 유효한 제목인지 확인
                    if not title or len(title) < 5:
                        continue
                    # 중복 제거
                    if title in seen_titles:
                        continue
                    # 메뉴/네비게이션 링크 제외
                    if any(x in title.lower() for x in ['rss', '바로가기', '새창', '홈페이지']):
                        continue

                    seen_titles.add(title)

                    # 링크 완성
                    if href and not href.startswith('http'):
                        href = f"https://www.bok.or.kr{href}"

                    articles.append({
                        "title": title,
                        "link": href or "",
                        "date": "",  # 상세 페이지에서 가져와야 함
                        "summary": "",
                        "source": config.get('name', '한국은행 보도자료'),
                        "icon": config.get('icon', '🏦'),
                        "fetched_at": datetime.now().isoformat()
                    })

                    if len(articles) >= 20:
                        break

                except Exception:
                    continue

            browser.close()

        print(f"  ✅ Playwright [한국은행]: {len(articles)}건")
        return articles

    except Exception as e:
        print(f"  ❌ Playwright [한국은행] 오류: {e}")
        return []


if __name__ == "__main__":
    # 테스트
    config = {
        "name": "한국은행 보도자료",
        "url": "https://www.bok.or.kr/portal/singl/newsData/list.do?menuNo=201263&pageUnit=20",
        "icon": "🏦"
    }
    articles = fetch_bok_news(config)
    for a in articles[:5]:
        print(f"- {a['title']}")
