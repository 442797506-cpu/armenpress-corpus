

import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'https://www.google.com/',
}

url = 'https://armenpress.am/hy/articles/armenia?page=1'
resp = requests.get(url, headers=headers, timeout=30)
print('Status:', resp.status_code)
print('Encoding:', resp.encoding)
print('First 500 chars:', resp.text[:500])

if resp.status_code == 200:
    soup = BeautifulSoup(resp.text, 'html.parser')
    # 尝试找文章列表
    links = soup.find_all('a', href=lambda x: x and '/hy/article/' in x)
    print('Found article links:', len(links))
    for link in links[:5]:
        print(link.get('href'), link.get_text(strip=True)[:50])