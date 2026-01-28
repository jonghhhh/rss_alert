# 📡 실시간 뉴스 피드 알림 시스템

정부기관 보도자료 및 뉴스를 **자동 수집**하여 웹페이지에 표시하고, 새 글이 있으면 이메일로 알림을 보내는 시스템입니다.

**완전 무료** (GitHub Actions + GitHub Pages)

## 🎯 프로젝트 취지

- 한국은행, 통계청 등 정부기관 보도자료를 실시간으로 모니터링
- 여러 사이트를 일일이 방문하지 않고 한 곳에서 확인
- 새 글이 올라오면 이메일로 알림 받기
- 무료 인프라(GitHub)만 사용하여 유지비용 0원

---

## ✨ 주요 기능

| 기능 | 설명 |
|------|------|
| ⏰ **자동 수집** | 30분마다 GitHub Actions로 자동 실행 |
| 🌐 **실시간 웹페이지** | GitHub Pages에서 수집된 뉴스 확인 |
| 📧 **이메일 알림** | 새 글 발견 시 Gmail로 알림 (선택) |
| 🔄 **다중 수집 방식** | RSS, Playwright 스크래핑 모두 지원 |
| 📱 **반응형 디자인** | PC, 모바일 모두 지원 |

### 웹페이지 기능
- **통합 보기**: 모든 기관의 업데이트를 최신순으로
- **피드별 보기**: 기관별로 분류해서 보기
- **필터**: 특정 기관만 필터링
- **페이지네이션**: 페이지당 15개씩
- **자동 새로고침**: 60초마다 최신 데이터 로드

---

## 📋 현재 활성화된 피드

| 피드 | 타입 | 아이콘 | 상태 |
|------|------|--------|------|
| 한국은행 보도자료 | playwright | 🏦 | ✅ 활성 |
| 통계청 보도자료 | rss | 📊 | ✅ 활성 |
| 통계청 언론보도 설명 | rss | 📈 | ✅ 활성 |
| Hacker News | rss | 🔶 | ✅ 활성 |
| 금융위원회 | rss | 🏢 | ⏸️ 비활성 |
| TechCrunch | rss | 💻 | ⏸️ 비활성 |

---

## 🛠️ 기술 스택 및 구조

### 수집 방식

| 타입 | 설명 | 사용 사례 |
|------|------|----------|
| `rss` | RSS/Atom 피드 파싱 (feedparser) | 통계청, Hacker News 등 RSS 제공 사이트 |
| `playwright` | 헤드리스 브라우저 스크래핑 | 한국은행 등 JavaScript 렌더링 사이트 |
| `scrape` | 단순 HTML 스크래핑 (BeautifulSoup) | 정적 HTML 사이트 |

### 파일 구조

```
rss_alert/
├── .github/workflows/
│   └── scraper.yml          # GitHub Actions 워크플로우
├── scripts/
│   ├── scraper.py           # 메인 스크래퍼 (RSS + 연동)
│   └── scraper_bok.py       # 한국은행 전용 (Playwright)
├── docs/
│   ├── index.html           # 웹페이지 (GitHub Pages)
│   └── data.json            # 수집된 데이터
├── config.json              # 피드 설정 ⭐
├── requirements.txt         # Python 의존성
└── README.md
```

### 작동 흐름

```
1. GitHub Actions (30분마다 또는 수동 실행)
   ↓
2. scraper.py 실행
   ├── RSS 피드 → feedparser로 파싱
   └── Playwright 피드 → scraper_bok.py 등 호출
   ↓
3. docs/data.json에 데이터 저장
   ↓
4. GitHub Pages로 자동 배포
   ↓
5. 웹페이지에서 data.json 로드하여 표시
```

---

## 🚀 설정 방법

### 1단계: 저장소 Fork 또는 Clone

```bash
git clone https://github.com/jonghhhh/rss_alert.git
cd rss_alert
```

### 2단계: 피드 설정 (`config.json`)

원하는 피드의 `enabled`를 `true`로 변경:

```json
{
  "feeds": [
    {
      "name": "한국은행 보도자료",
      "type": "playwright",
      "scraper": "bok",
      "url": "https://www.bok.or.kr/portal/singl/newsData/list.do?menuNo=201263&pageUnit=20",
      "icon": "🏦",
      "enabled": true
    },
    {
      "name": "통계청 보도자료",
      "type": "rss",
      "url": "https://kostat.go.kr/board.es?mid=a10301010000&bid=210&act=rss",
      "icon": "📊",
      "enabled": true
    }
  ]
}
```

### 3단계: GitHub에 Push

```bash
git add .
git commit -m "Update config"
git push origin main
```

### 4단계: GitHub Pages 활성화

1. GitHub 저장소 → **Settings** → **Pages**
2. **Source**: `Deploy from a branch`
3. **Branch**: `gh-pages` / `/ (root)` 선택 → **Save**

> ⚠️ 첫 번째 워크플로우 실행 후 `gh-pages` 브랜치가 생성됩니다.

### 5단계: Actions 확인

1. **Actions** 탭에서 "뉴스 피드 수집기" 워크플로우 확인
2. main 브랜치 push 시 자동 실행됨
3. 수동 실행: **Run workflow** 버튼 클릭

### 6단계: 웹페이지 접속

```
https://YOUR_USERNAME.github.io/rss_alert/
```

---

## 📧 이메일 알림 설정 (선택)

### Gmail 앱 비밀번호 생성

1. https://myaccount.google.com/security 접속
2. **2단계 인증** 활성화
3. **앱 비밀번호** 생성: https://myaccount.google.com/apppasswords
4. 앱: 메일, 기기: 기타 → "GitHub"
5. **16자리 비밀번호 복사**

### GitHub Secrets 설정

저장소 → **Settings** → **Secrets and variables** → **Actions**

| Name | Value |
|------|-------|
| `SENDER_EMAIL` | your@gmail.com |
| `SENDER_PASSWORD` | 16자리 앱 비밀번호 |
| `RECIPIENT_EMAIL` | 받을 이메일 주소 |

> 이메일 설정이 없으면 알림 없이 웹페이지만 업데이트됩니다.

---

## ⚙️ 피드 추가하기

### RSS 피드 추가

```json
{
  "name": "피드 이름",
  "type": "rss",
  "url": "https://example.com/rss.xml",
  "icon": "📰",
  "enabled": true
}
```

### Playwright 스크래퍼 추가 (새 기관)

JavaScript 렌더링이 필요한 사이트는 별도 스크래퍼 모듈이 필요합니다.

#### 1. 스크래퍼 파일 생성

`scripts/scraper_기관명.py`:

```python
"""
기관명 보도자료 스크래퍼 (Playwright 사용)
"""
from playwright.sync_api import sync_playwright
from datetime import datetime


def fetch_기관명_news(config: dict) -> list:
    """기관명 보도자료 스크래핑"""
    url = config.get('url')
    articles = []

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=30000)
            page.wait_for_timeout(3000)  # JS 렌더링 대기

            # 여기에 스크래핑 로직 작성
            links = page.query_selector_all('a.news-link')

            for link in links[:20]:
                title = link.inner_text().strip()
                href = link.get_attribute('href')

                articles.append({
                    "title": title,
                    "link": href,
                    "date": "",
                    "summary": "",
                    "source": config.get('name'),
                    "icon": config.get('icon', '📰'),
                    "fetched_at": datetime.now().isoformat()
                })

            browser.close()

        print(f"  ✅ Playwright [{config['name']}]: {len(articles)}건")
        return articles

    except Exception as e:
        print(f"  ❌ Playwright [{config['name']}] 오류: {e}")
        return []
```

#### 2. 메인 스크래퍼에 등록

`scripts/scraper.py`의 `fetch_playwright_feed()` 함수에 추가:

```python
def fetch_playwright_feed(feed_config):
    scraper_name = feed_config.get('scraper', '')

    if scraper_name == 'bok':
        from scraper_bok import fetch_bok_news
        return fetch_bok_news(feed_config)
    elif scraper_name == '기관명':
        from scraper_기관명 import fetch_기관명_news
        return fetch_기관명_news(feed_config)
    # ...
```

#### 3. config.json에 추가

```json
{
  "name": "기관명 보도자료",
  "type": "playwright",
  "scraper": "기관명",
  "url": "https://example.go.kr/news",
  "icon": "🏛️",
  "enabled": true
}
```

---

## 📰 주요 RSS 피드 모음

### 정부/공공기관

| 사이트 | RSS URL |
|--------|---------|
| 통계청 보도자료 | `https://kostat.go.kr/board.es?mid=a10301010000&bid=210&act=rss` |
| 통계청 언론보도 설명 | `https://kostat.go.kr/board.es?mid=a10304010000&bid=210&act=rss` |
| 금융위원회 | `https://www.fsc.go.kr/rss/P0000016` |

### 테크/IT

| 사이트 | RSS URL |
|--------|---------|
| Hacker News | `https://news.ycombinator.com/rss` |
| TechCrunch | `https://techcrunch.com/feed/` |
| The Verge | `https://www.theverge.com/rss/index.xml` |

### Medium / YouTube

```
# Medium
https://medium.com/feed/@사용자이름
https://medium.com/feed/topic/artificial-intelligence

# YouTube
https://www.youtube.com/feeds/videos.xml?channel_id=채널ID
```

---

## 🔧 설정 변경

### 수집 주기 변경

`.github/workflows/scraper.yml`:

```yaml
schedule:
  - cron: '*/30 * * * *'   # 30분마다 (기본)
  - cron: '0 * * * *'      # 1시간마다
  - cron: '0 */6 * * *'    # 6시간마다
```

### 웹페이지 자동 새로고침 주기

`docs/index.html`에서 `countdown` 값 변경 (기본: 60초)

---

## 🐛 트러블슈팅

### 워크플로우가 Actions 탭에 안 보임

- `.github/workflows/scraper.yml` 파일이 GitHub에 푸시되었는지 확인
- Personal Access Token에 `workflow` 권한이 있는지 확인

### RSS 파싱 오류

- `feedparser` 라이브러리는 대부분의 잘못된 XML도 처리 가능
- URL이 리다이렉트되는 경우 최종 URL 사용

### Playwright 스크래핑 실패

- `page.wait_for_timeout()`으로 JS 렌더링 대기 시간 조정
- 선택자(selector)가 페이지 구조와 맞는지 확인

### gh-pages 브랜치가 없음

- 워크플로우가 한 번 이상 성공적으로 실행되어야 생성됨
- Actions 탭에서 워크플로우를 수동으로 실행

---

## 💰 비용

| 서비스 | 비용 |
|--------|------|
| GitHub Actions | 무료 (월 2,000분) |
| GitHub Pages | 무료 |
| Gmail SMTP | 무료 |
| **총** | **0원** |

---

## 📝 개발 이력

### v2.0 (2026-01-28)
- Playwright 기반 스크래퍼 추가 (한국은행 지원)
- feedparser로 RSS 파싱 개선
- 통계청 RSS URL 업데이트 (kostat.go.kr)
- 모듈화된 스크래퍼 구조 (`scraper_bok.py`)

### v1.0
- 기본 RSS 수집 기능
- GitHub Pages 웹페이지
- 이메일 알림 기능

---

## 📄 라이선스

MIT License
