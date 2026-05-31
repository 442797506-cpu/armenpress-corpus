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
soup = BeautifulSoup(resp.text, 'html.parser')

article = soup.find('article')
if article:
    print('Article children tags:')
    for child in article.find_all(recursive=False):
        print(' ', child.name, child.get('class'))
    print('\n--- Article full text (first 800 chars) ---')
    print(article.get_text(separator='\n', strip=True)[:800])