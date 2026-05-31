import requests
from bs4 import BeautifulSoup
import json
import time
import os
from urllib.parse import urljoin

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'https://armenpress.am/hy/articles/armenia',
}

BASE_URL = 'https://armenpress.am'
LIST_URL_TEMPLATE = 'https://armenpress.am/hy/articles/armenia?page={}'


def fetch_list_page(page_num):
    url = LIST_URL_TEMPLATE.format(page_num)
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        print(f'[错误] 获取列表页第 {page_num} 页失败: {e}')
        return None


def parse_article_links(html):
    soup = BeautifulSoup(html, 'html.parser')
    links = set()
    for a in soup.find_all('a', href=True):
        href = a['href']
        if '/hy/article/' in href and href.count('/') >= 3:
            full_url = urljoin(BASE_URL, href)
            # 去除可能的尾部参数，保留干净链接
            links.add(full_url.split('?')[0].split('#')[0])
    return list(links)


def fetch_article(url):
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        print(f'[错误] 获取文章失败 {url}: {e}')
        return None


def parse_article(html, url):
    soup = BeautifulSoup(html, 'html.parser')

    title = ''
    h1 = soup.find('h1')
    if h1:
        title = h1.get_text(strip=True)

    pub_time = ''
    time_tag = soup.find('time')
    if time_tag:
        pub_time = time_tag.get('datetime', '') or time_tag.get_text(strip=True)

    content = ''
    article = soup.find('article')
    if article:
        prose = article.find('div', class_='prose')
        if prose:
            paragraphs = prose.find_all(['p', 'h2', 'h3', 'li'])
            content = '\n\n'.join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
        else:
            # fallback: 用 article 的全部文本，去掉前面非正文部分
            full_text = article.get_text(separator='\n', strip=True)
            lines = full_text.split('\n')
            # 跳过前面的分类、时间、标题、阅读时间等元信息
            skip_keywords = ['րոպեի ընթերցում', 'լուսանկարը']
            filtered = []
            started = False
            for line in lines:
                if not started:
                    # 找到正文开始的位置：通常标题后的第一段较长
                    if line == title or any(kw in line for kw in skip_keywords):
                        continue
                    if len(line) > 30:
                        started = True
                        filtered.append(line)
                else:
                    if line == title:
                        continue
                    filtered.append(line)
            content = '\n\n'.join(filtered)
    else:
        # 如果没找到 article 标签，直接取 body 里最长的 div 文本
        body = soup.find('body')
        if body:
            divs = body.find_all('div')
            longest = ''
            for div in divs:
                text = div.get_text(strip=True)
                if len(text) > len(longest):
                    longest = text
            content = longest

    return {
        'url': url,
        'title': title,
        'publish_time': pub_time,
        'content': content,
    }


def main():
    target_count = 300
    all_articles = []
    seen_urls = set()
    page = 1

    output_file = 'armenpress_articles.json'

    # 如果之前有爬到一半的数据，继续
    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            all_articles = json.load(f)
        seen_urls = {a['url'] for a in all_articles}
        print(f'[恢复] 已存在 {len(all_articles)} 条记录，继续爬取...')

    try:
        while len(all_articles) < target_count:
            print(f'[列表] 正在获取第 {page} 页...')
            html = fetch_list_page(page)
            if not html:
                break

            links = parse_article_links(html)
            print(f'[列表] 第 {page} 页发现 {len(links)} 个文章链接')

            if not links:
                print('[列表] 没有更多文章，结束爬取')
                break

            new_links = [u for u in links if u not in seen_urls]
            print(f'[列表] 其中新文章 {len(new_links)} 条')

            for idx, url in enumerate(new_links, 1):
                print(f'[文章] ({len(all_articles)+1}/{target_count}) 正在爬取: {url}')
                article_html = fetch_article(url)
                if not article_html:
                    continue
                article = parse_article(article_html, url)
                if not article['title'] or not article['content']:
                    print('[文章] 解析失败，跳过')
                    continue
                all_articles.append(article)
                seen_urls.add(url)

                # 每爬10条保存一次，防止中断丢失进度
                if len(all_articles) % 10 == 0:
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(all_articles, f, ensure_ascii=False, indent=2)
                    print('[保存] 已保存进度')

                if len(all_articles) >= target_count:
                    break

                time.sleep(0.8)  # 礼貌延迟，避免被封

            page += 1
            time.sleep(1)

    except KeyboardInterrupt:
        print('\n[中断] 用户手动停止')
    finally:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_articles, f, ensure_ascii=False, indent=2)
        print(f'[完成] 共爬取 {len(all_articles)} 条新闻，已保存到 {output_file}')


if __name__ == '__main__':
    main()