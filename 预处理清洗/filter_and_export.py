import json
import csv
import re

INPUT_JSON = '/Users/wangweichen/PycharmProjects/PythonProject3/armenpress_articles_processed.json'
OUTPUT_CSV = '/Users/wangweichen/PycharmProjects/PythonProject3/预处理最终结果.csv'

# 亚美尼亚语字母范围 (含大小写及附加符号)
ARMENIAN_PATTERN = re.compile(r'^[԰-֏]+$')


def is_armenian_word(word):
    """判断是否纯亚美尼亚语单词"""
    if not word or len(word) == 0:
        return False
    return bool(ARMENIAN_PATTERN.match(word))


def filter_words(lemmas, pos_tags):
    """过滤掉标点、英文、数字、URL，只保留亚美尼亚语词汇"""
    filtered = []
    for lemma, pos in zip(lemmas, pos_tags):
        # 1. 去除标点符号
        if pos == 'PUNCT':
            continue
        # 2. 去除纯数字
        if lemma.isdigit():
            continue
        # 3. 去除英文单词 (只包含ASCII字母)
        if re.match(r'^[a-zA-Z]+$', lemma):
            continue
        # 4. 去除URL残留
        if 'http' in lemma or 'www' in lemma:
            continue
        # 5. 去除非亚美尼亚语字符的杂项
        if not is_armenian_word(lemma):
            continue
        filtered.append(lemma)
    return filtered


def main():
    print("[读取] 正在加载JSON文件...")
    with open(INPUT_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"[读取] 共加载 {len(data)} 条新闻")

    results = []
    for idx, item in enumerate(data, 1):
        title_filtered = filter_words(item['title_lemmas'], item['title_pos'])
        content_filtered = filter_words(item['content_lemmas'], item['content_pos'])

        results.append({
            'url': item['url'],
            'publish_time': item['publish_time'],
            'title_filtered': ' '.join(title_filtered),
            'content_filtered': ' '.join(content_filtered),
            'title_word_count': len(title_filtered),
            'content_word_count': len(content_filtered),
        })

        if idx % 50 == 0:
            print(f"[处理] 已完成 {idx}/{len(data)} 条")

    # 导出CSV
    with open(OUTPUT_CSV, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'url', 'publish_time', 'title_filtered', 'content_filtered',
            'title_word_count', 'content_word_count'
        ])
        writer.writeheader()
        writer.writerows(results)

    print(f"[完成] 已导出到 {OUTPUT_CSV}")
    print(f"[统计] 总条数: {len(results)}")

    # 展示第一条样本
    first = results[0]
    print(f"\n[样本] 第一条:")
    print(f"  标题词数: {first['title_word_count']}")
    print(f"  标题: {first['title_filtered']}")
    print(f"  正文词数: {first['content_word_count']}")
    print(f"  正文前200字: {first['content_filtered'][:200]}...")


if __name__ == '__main__':
    main()