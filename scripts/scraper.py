"""
통합 뉴스 피드 수집기
- RSS 피드 지원
- 웹 스크래핑 지원 (RSS 없는 사이트)
- 새 글 이메일 알림
"""

import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import json
import os
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re

# 설정
CONFIG_FILE = "config.json"
DATA_FILE = "docs/data.json"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


def load_config():
    """설정 파일 로드"""
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def fetch_rss_feed(feed_config):
    """RSS 피드 가져오기"""
    try:
        response = requests.get(feed_config['url'], headers=HEADERS, timeout=30)
        response.raise_for_status()
        
        # XML 파싱
        root = ET.fromstring(response.content)
        articles = []
        
        # RSS 2.0 형식
        for item in root.findall('.//item')[:20]:
            title = item.find('title')
            link = item.find('link')
            pub_date = item.find('pubDate')
            description = item.find('description')
            
            if title is not None and link is not None:
                articles.append({
                    "title": title.text.strip() if title.text else "",
                    "link": link.text.strip() if link.text else "",
                    "date": pub_date.text.strip() if pub_date is not None and pub_date.text else "",
                    "summary": description.text[:200] if description is not None and description.text else "",
                    "source": feed_config['name'],
                    "icon": feed_config.get('icon', '📰'),
                    "fetched_at": datetime.now().isoformat()
                })
        
        # Atom 형식 (RSS가 비어있을 때)
        if not articles:
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            for entry in root.findall('.//atom:entry', ns)[:20]:
                title = entry.find('atom:title', ns)
                link = entry.find('atom:link', ns)
                published = entry.find('atom:published', ns)
                
                if title is not None:
                    link_href = link.get('href') if link is not None else ""
                    articles.append({
                        "title": title.text.strip() if title.text else "",
                        "link": link_href,
                        "date": published.text[:10] if published is not None and published.text else "",
                        "summary": "",
                        "source": feed_config['name'],
                        "icon": feed_config.get('icon', '📰'),
                        "fetched_at": datetime.now().isoformat()
                    })
        
        # YouTube Atom 형식
        if not articles:
            for entry in root.findall('.//{http://www.w3.org/2005/Atom}entry')[:20]:
                title = entry.find('{http://www.w3.org/2005/Atom}title')
                link = entry.find('{http://www.w3.org/2005/Atom}link')
                published = entry.find('{http://www.w3.org/2005/Atom}published')
                
                if title is not None:
                    link_href = link.get('href') if link is not None else ""
                    articles.append({
                        "title": title.text.strip() if title.text else "",
                        "link": link_href,
                        "date": published.text[:10] if published is not None and published.text else "",
                        "summary": "",
                        "source": feed_config['name'],
                        "icon": feed_config.get('icon', '📺'),
                        "fetched_at": datetime.now().isoformat()
                    })
        
        print(f"  ✅ RSS [{feed_config['name']}]: {len(articles)}건")
        return articles
        
    except Exception as e:
        print(f"  ❌ RSS [{feed_config['name']}] 오류: {e}")
        return []


def fetch_scrape_feed(feed_config):
    """웹 스크래핑으로 피드 가져오기"""
    try:
        response = requests.get(feed_config['url'], headers=HEADERS, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        articles = []
        
        # 한국은행 보도자료 전용 파싱
        if 'bok.or.kr' in feed_config['url']:
            # 방법 1: 테이블 기반
            rows = soup.select('table.boardList tbody tr, table tbody tr')
            
            for row in rows[:20]:
                try:
                    link_elem = row.select_one('a[href*="view.do"], a[href*="nttId"]')
                    if not link_elem:
                        continue
                    
                    title = link_elem.get_text(strip=True)
                    href = link_elem.get('href', '')
                    
                    if href and not href.startswith('http'):
                        href = f"https://www.bok.or.kr{href}"
                    
                    # 날짜 찾기 (보통 4번째 td)
                    date_cells = row.select('td')
                    date_str = ""
                    for cell in date_cells:
                        text = cell.get_text(strip=True)
                        if re.match(r'\d{4}[.\-/]\d{2}[.\-/]\d{2}', text):
                            date_str = text
                            break
                    
                    if title and len(title) > 3:
                        articles.append({
                            "title": title,
                            "link": href,
                            "date": date_str,
                            "summary": "",
                            "source": feed_config['name'],
                            "icon": feed_config.get('icon', '🏦'),
                            "fetched_at": datetime.now().isoformat()
                        })
                except:
                    continue
            
            # 방법 2: 리스트 기반 (테이블이 없을 때)
            if not articles:
                items = soup.select('.boardList li, .list-wrap li, [class*="list"] > li')
                for item in items[:20]:
                    link_elem = item.select_one('a[href]')
                    if link_elem:
                        title = link_elem.get_text(strip=True)
                        href = link_elem.get('href', '')
                        if href and not href.startswith('http'):
                            href = f"https://www.bok.or.kr{href}"
                        
                        if title and len(title) > 3:
                            articles.append({
                                "title": title,
                                "link": href,
                                "date": "",
                                "summary": "",
                                "source": feed_config['name'],
                                "icon": feed_config.get('icon', '🏦'),
                                "fetched_at": datetime.now().isoformat()
                            })
        
        # 일반 사이트 파싱
        else:
            # 공통 선택자로 시도
            selectors = [
                'article a[href]',
                '.list-item a[href]',
                '.post-title a[href]',
                'h2 a[href]',
                'h3 a[href]',
                '.entry-title a[href]'
            ]
            
            for selector in selectors:
                links = soup.select(selector)[:20]
                if links:
                    for link in links:
                        title = link.get_text(strip=True)
                        href = link.get('href', '')
                        
                        if title and len(title) > 3:
                            articles.append({
                                "title": title,
                                "link": href,
                                "date": "",
                                "summary": "",
                                "source": feed_config['name'],
                                "icon": feed_config.get('icon', '📄'),
                                "fetched_at": datetime.now().isoformat()
                            })
                    break
        
        print(f"  ✅ Scrape [{feed_config['name']}]: {len(articles)}건")
        return articles
        
    except Exception as e:
        print(f"  ❌ Scrape [{feed_config['name']}] 오류: {e}")
        return []


def fetch_feed(feed_config):
    """피드 타입에 따라 적절한 방법으로 가져오기"""
    if feed_config['type'] == 'rss':
        return fetch_rss_feed(feed_config)
    elif feed_config['type'] == 'scrape':
        return fetch_scrape_feed(feed_config)
    else:
        print(f"  ⚠️ 알 수 없는 타입: {feed_config['type']}")
        return []


def load_existing_data():
    """기존 데이터 로드"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"feeds": {}, "last_updated": None}


def save_data(data):
    """데이터 저장"""
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def find_new_articles(new_articles, existing_articles):
    """새로운 글 찾기"""
    existing_titles = {a['title'] for a in existing_articles}
    return [a for a in new_articles if a['title'] not in existing_titles]


def send_email_notification(new_articles_by_feed):
    """이메일 알림 발송"""
    smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.environ.get('SMTP_PORT', 587))
    sender_email = os.environ.get('SENDER_EMAIL')
    sender_password = os.environ.get('SENDER_PASSWORD')
    recipient_email = os.environ.get('RECIPIENT_EMAIL')
    
    if not all([sender_email, sender_password, recipient_email]):
        print("⚠️ 이메일 설정이 없습니다. 알림을 건너뜁니다.")
        return False
    
    # 총 새 글 수
    total_new = sum(len(articles) for articles in new_articles_by_feed.values())
    if total_new == 0:
        return False
    
    subject = f"📡 새 소식 {total_new}건이 도착했습니다!"
    
    html_content = """
    <html>
    <head>
        <style>
            body { font-family: -apple-system, Arial, sans-serif; line-height: 1.6; background: #f5f5f5; padding: 20px; }
            .container { max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; overflow: hidden; }
            .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }
            .header h1 { margin: 0; font-size: 24px; }
            .feed-section { padding: 20px; border-bottom: 1px solid #eee; }
            .feed-title { font-size: 18px; font-weight: bold; color: #333; margin-bottom: 15px; }
            .article { margin-bottom: 15px; padding: 15px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #667eea; }
            .article-title { font-size: 15px; font-weight: 500; color: #333; margin-bottom: 5px; }
            .article-date { color: #888; font-size: 13px; }
            .article a { color: #667eea; text-decoration: none; }
            .article a:hover { text-decoration: underline; }
            .footer { padding: 20px; text-align: center; color: #888; font-size: 12px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📡 새 소식이 도착했습니다!</h1>
                <p style="margin: 10px 0 0 0; opacity: 0.9;">총 """ + str(total_new) + """건의 새 글</p>
            </div>
    """
    
    for feed_name, articles in new_articles_by_feed.items():
        if not articles:
            continue
            
        icon = articles[0].get('icon', '📰') if articles else '📰'
        html_content += f"""
            <div class="feed-section">
                <div class="feed-title">{icon} {feed_name}</div>
        """
        
        for article in articles[:5]:  # 피드당 최대 5개만
            html_content += f"""
                <div class="article">
                    <div class="article-title">
                        <a href="{article['link']}">{article['title']}</a>
                    </div>
                    <div class="article-date">📅 {article.get('date', '')}</div>
                </div>
            """
        
        if len(articles) > 5:
            html_content += f'<p style="color: #888; font-size: 13px;">...외 {len(articles) - 5}건 더 있음</p>'
        
        html_content += "</div>"
    
    html_content += """
            <div class="footer">
                <p>이 알림은 GitHub Actions에서 자동으로 발송되었습니다.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg.attach(MIMEText(html_content, 'html'))
        
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
        
        print(f"✅ 이메일 발송 완료: {total_new}건의 새 글")
        return True
    
    except Exception as e:
        print(f"❌ 이메일 발송 실패: {e}")
        return False


def main():
    print("=" * 60)
    print(f"📡 통합 뉴스 피드 수집 시작: {datetime.now()}")
    print("=" * 60)
    
    # 1. 설정 로드
    config = load_config()
    enabled_feeds = [f for f in config['feeds'] if f.get('enabled', False)]
    print(f"\n📋 활성화된 피드: {len(enabled_feeds)}개")
    
    if not enabled_feeds:
        print("⚠️ 활성화된 피드가 없습니다. config.json에서 enabled를 true로 설정하세요.")
        return
    
    # 2. 기존 데이터 로드
    existing_data = load_existing_data()
    
    # 3. 각 피드 수집
    all_articles = {}
    new_articles_by_feed = {}
    
    print("\n🔍 피드 수집 중...")
    for feed_config in enabled_feeds:
        feed_name = feed_config['name']
        
        # 피드 가져오기
        articles = fetch_feed(feed_config)
        all_articles[feed_name] = articles
        
        # 새 글 확인
        existing_articles = existing_data.get('feeds', {}).get(feed_name, [])
        new_articles = find_new_articles(articles, existing_articles)
        
        if new_articles:
            new_articles_by_feed[feed_name] = new_articles
            print(f"    🆕 새 글 {len(new_articles)}건 발견!")
    
    # 4. 데이터 저장
    updated_data = {
        "feeds": all_articles,
        "last_updated": datetime.now().isoformat(),
        "feed_count": len(enabled_feeds),
        "total_articles": sum(len(a) for a in all_articles.values())
    }
    save_data(updated_data)
    print(f"\n💾 데이터 저장 완료 (총 {updated_data['total_articles']}건)")
    
    # 5. 새 글이 있으면 이메일 알림
    total_new = sum(len(a) for a in new_articles_by_feed.values())
    if total_new > 0 and config.get('settings', {}).get('email_on_new', True):
        print(f"\n📧 이메일 알림 발송 중... (새 글 {total_new}건)")
        send_email_notification(new_articles_by_feed)
    else:
        print("\n📭 새로운 글이 없습니다.")
    
    print("\n" + "=" * 60)
    print("✅ 완료!")
    print("=" * 60)


if __name__ == "__main__":
    main()
