# 📡 실시간 뉴스 피드 알림 시스템

RSS 피드 + 웹 스크래핑을 지원하는 **완전 무료** 뉴스 알림 시스템입니다.

## ✨ 기능

- ⏰ **30분마다 자동 수집** (GitHub Actions)
- 📧 **새 글 이메일 알림** (Gmail)
- 🌐 **실시간 웹페이지** (GitHub Pages)
  - 📋 **통합 보기**: 모든 기관 업데이트를 최신순으로 한눈에
  - 📁 **피드별 보기**: 기관별로 분류해서 보기
  - 📄 **페이지네이션**: 오래된 글은 다음 페이지로
- 🔄 **RSS + 스크래핑 모두 지원**
- 💰 **완전 무료**

---

## 📋 현재 활성화된 피드

| 피드 | 타입 | 아이콘 |
|------|------|--------|
| 한국은행 보도자료 | scrape | 🏦 |
| 통계청 보도자료 | rss | 📊 |
| 통계청 언론보도 설명 | rss | 📈 |

---

## 📋 지원 피드 타입

| 타입 | 설명 | 예시 |
|------|------|------|
| `rss` | RSS/Atom 피드가 있는 사이트 | 통계청, Medium, YouTube |
| `scrape` | RSS가 없어서 스크래핑 필요 | 한국은행 |

---

## 🚀 설정 방법

### 1단계: GitHub 저장소 생성

1. GitHub에서 **New repository**
2. 이름: `news-feed-alert` (원하는 이름)
3. **Public** 선택
4. **Create repository**

### 2단계: 파일 업로드

모든 파일을 GitHub 저장소에 업로드

### 3단계: 피드 설정 (`config.json`)

원하는 피드의 `enabled`를 `true`로 변경:

```json
{
  "feeds": [
    {
      "name": "한국은행 보도자료",
      "type": "scrape",
      "url": "https://www.bok.or.kr/portal/bbs/P0000559/list.do?menuNo=200690",
      "icon": "🏦",
      "enabled": true
    },
    {
      "name": "통계청 보도자료",
      "type": "rss",
      "url": "http://mods.go.kr/menu.es?mid=a10301010000&act=rss",
      "icon": "📊",
      "enabled": true
    }
  ]
}
```

### 4단계: Gmail 앱 비밀번호 생성

1. https://myaccount.google.com/security 접속
2. **2단계 인증** 활성화
3. **앱 비밀번호** 생성 (https://myaccount.google.com/apppasswords)
4. 앱: 메일, 기기: 기타 → "GitHub"
5. **16자리 비밀번호 복사**

### 5단계: GitHub Secrets 설정

저장소 → **Settings** → **Secrets and variables** → **Actions**

| Name | Value |
|------|-------|
| `SENDER_EMAIL` | your@gmail.com |
| `SENDER_PASSWORD` | 16자리 앱 비밀번호 |
| `RECIPIENT_EMAIL` | 받을 이메일 |

### 6단계: GitHub Pages 활성화

Settings → Pages → Source: **GitHub Actions**

### 7단계: 실행

Actions → **뉴스 피드 수집기** → **Run workflow**

---

## 🌐 웹페이지 접속

```
https://YOUR_USERNAME.github.io/REPO_NAME/
```

### 웹페이지 기능

- **통합 보기**: 모든 기관의 업데이트를 최신순으로 정렬
- **피드별 보기**: 기관별로 분류해서 보기
- **필터**: 특정 기관만 필터링
- **페이지네이션**: 페이지당 15개씩, 오래된 글은 다음 페이지로

---

## 📁 파일 구조

```
├── .github/workflows/
│   └── scraper.yml       # 자동 실행 설정
├── scripts/
│   └── scraper.py        # 수집 + 알림
├── docs/
│   ├── index.html        # 웹페이지
│   └── data.json         # 데이터
├── config.json           # 피드 설정 ⭐
├── requirements.txt
└── README.md
```

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

### 스크래핑 피드 추가

```json
{
  "name": "피드 이름",
  "type": "scrape",
  "url": "https://example.com/news",
  "icon": "🔍",
  "enabled": true
}
```

---

## 📰 주요 RSS 피드 모음

### 정부/공공기관
| 사이트 | RSS URL |
|--------|---------|
| 통계청 보도자료 | `http://mods.go.kr/menu.es?mid=a10301010000&act=rss` |
| 통계청 언론보도 설명 | `http://mods.go.kr/menu.es?mid=a10304010000&act=rss` |
| 금융위원회 | `https://www.fsc.go.kr/rss/P0000016` |

### 한국 뉴스
| 사이트 | RSS URL |
|--------|---------|
| 한겨레 | `http://www.hani.co.kr/rss/` |
| 경향신문 | `http://khan.co.kr/rss/rssdata/total_news.xml` |

### 테크/IT
| 사이트 | RSS URL |
|--------|---------|
| TechCrunch | `https://techcrunch.com/feed/` |
| Hacker News | `https://news.ycombinator.com/rss` |
| The Verge | `https://www.theverge.com/rss/index.xml` |

### Medium
```
https://medium.com/feed/@사용자이름
https://medium.com/feed/퍼블리케이션
https://medium.com/feed/topic/artificial-intelligence
```

### YouTube
```
https://www.youtube.com/feeds/videos.xml?channel_id=채널ID
```

---

## 🔧 스크래핑 주기 변경

`.github/workflows/scraper.yml`:

```yaml
schedule:
  - cron: '*/30 * * * *'   # 30분마다 (기본)
  - cron: '0 * * * *'      # 1시간마다
  - cron: '0 */6 * * *'    # 6시간마다
```

---

## 💰 비용

| 서비스 | 비용 |
|--------|------|
| GitHub Actions | 무료 (월 2,000분) |
| GitHub Pages | 무료 |
| Gmail SMTP | 무료 |
| **총** | **0원** |

---

## 📝 라이선스

MIT License
