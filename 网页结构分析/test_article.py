
import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'https://armenpress.am/hy/articles/armenia',
}

url = 'https://armenpress.am/hy/article/1251455'
resp = requests.get(url, headers=headers, timeout=30)
print('Status:', resp.status_code)

if resp.status_code == 200:
    soup = BeautifulSoup(resp.text, 'html.parser')
    # 尝试各种常见选择器找标题
    print('=== Title candidates ===')
    for sel in ['h1', '.article-title', '.news-title', '.title', 'article h1']:
        el = soup.select_one(sel)
        if el:
            print(sel, ':', el.get_text(strip=True)[:100])

    print('\n=== Date candidates ===')
    for sel in ['time', '.date', '.published', '.article-date', '[datetime]']:
        els = soup.select(sel)[:2]
        for el in els:
            print(sel, ':', el.get_text(strip=True)[:50], 'datetime=', el.get('datetime'))

    print('\n=== Content candidates ===')
    for sel in ['article', '.article-body', '.news-content', '.content', '.text', '[itemprop="articleBody"]']:
        el = soup.select_one(sel)
        if el:
            text = el.get_text(separator='\n', strip=True)
            print(sel, 'length:', len(text))
            print(text[:300])
            print('---')