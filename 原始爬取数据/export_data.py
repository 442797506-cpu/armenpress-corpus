import json
import csv

INPUT_FILE = 'armenpress_articles.json'
CSV_FILE = 'armenpress_articles.csv'
TXT_FILE = 'armenpress_articles.txt'


def export_csv(data):
    with open(CSV_FILE, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['url', 'title', 'publish_time', 'content'])
        writer.writeheader()
        for item in data:
            writer.writerow(item)
    print(f'[CSV] 已导出 {len(data)} 条到 {CSV_FILE}')


def export_txt(data):
    with open(TXT_FILE, 'w', encoding='utf-8') as f:
        for idx, item in enumerate(data, 1):
            f.write(f"{'=' * 60}\n")
            f.write(f"[新闻 {idx}]\n")
            f.write(f"标题: {item['title']}\n")
            f.write(f"时间: {item['publish_time']}\n")
            f.write(f"链接: {item['url']}\n")
            f.write(f"{'-' * 60}\n")
            f.write(f"{item['content']}\n")
            f.write("\n\n")
    print(f'[TXT] 已导出 {len(data)} 条到 {TXT_FILE}')


def main():
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    export_csv(data)
    export_txt(data)


if __name__ == '__main__':
    main()