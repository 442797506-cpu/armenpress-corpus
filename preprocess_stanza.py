import pandas as pd
import re
import stanza
import os
import json

INPUT_CSV = 'armenpress_articles.csv'
OUTPUT_CSV = 'armenpress_articles_cleaned.csv'
OUTPUT_JSON = 'armenpress_articles_processed.json'


def clean_text(text):
    """清洗文本：去除URL、HTML标签、多余空白、保留亚美尼亚语及常用标点"""
    if not isinstance(text, str):
        return ""

    # 1. 去除URL链接
    text = re.sub(r'https?://\S+|www\.\S+', '', text)

    # 2. 去除HTML标签
    text = re.sub(r'<[^>]+>', '', text)

    # 3. 去除邮箱地址
    text = re.sub(r'\S+@\S+', '', text)

    # 4. 去除多余空白（保留段落换行）
    text = re.sub(r'[ \t]+', ' ', text)  # 多个空格/制表符合并为一个空格
    text = re.sub(r'\n\s*\n+', '\n\n', text)  # 多个空行合并为两个换行
    text = text.strip()

    return text


def build_nlp_pipeline():
    """构建stanza NLP pipeline（亚美尼亚语）"""
    print("[Stanza] 正在加载亚美尼亚语模型...")
    nlp = stanza.Pipeline(
        lang='hy',
        processors='tokenize,pos,lemma',
        use_gpu=False,
        verbose=False
    )
    print("[Stanza] 模型加载完成")
    return nlp


def process_with_stanza(text, nlp):
    """使用stanza对单条文本进行NLP处理"""
    doc = nlp(text)
    sentences = []
    all_tokens = []
    all_lemmas = []
    all_pos = []

    for sent in doc.sentences:
        sent_tokens = []
        sent_lemmas = []
        sent_pos = []
        for word in sent.words:
            sent_tokens.append(word.text)
            sent_lemmas.append(word.lemma)
            sent_pos.append(word.upos)
        sentences.append({
            'text': sent.text,
            'tokens': sent_tokens,
            'lemmas': sent_lemmas,
            'pos': sent_pos
        })
        all_tokens.extend(sent_tokens)
        all_lemmas.extend(sent_lemmas)
        all_pos.extend(sent_pos)

    return {
        'sentences': sentences,
        'tokens': all_tokens,
        'lemmas': all_lemmas,
        'pos_tags': all_pos,
        'token_count': len(all_tokens),
        'sentence_count': len(sentences)
    }


def main():
    print("[读取] 正在加载CSV文件...")
    df = pd.read_csv(INPUT_CSV, encoding='utf-8-sig')
    print(f"[读取] 共加载 {len(df)} 条新闻")

    # 清洗文本
    print("[清洗] 正在去除URL、HTML标签、多余空白...")
    df['content_cleaned'] = df['content'].apply(clean_text)
    df['title_cleaned'] = df['title'].apply(clean_text)

    # 统计清洗效果
    removed_chars = df['content'].apply(lambda x: len(str(x))) - df['content_cleaned'].apply(lambda x: len(str(x)))
    print(f"[清洗] 共去除 {removed_chars.sum()} 个冗余字符")

    # Stanza NLP 处理
    nlp = build_nlp_pipeline()

    processed_results = []
    for idx, row in df.iterrows():
        print(f"[处理] ({idx + 1}/{len(df)}) 正在处理: {row['title_cleaned'][:40]}...")

        content_result = process_with_stanza(row['content_cleaned'], nlp)
        title_result = process_with_stanza(row['title_cleaned'], nlp)

        processed_results.append({
            'url': row['url'],
            'title': row['title_cleaned'],
            'title_tokens': title_result['tokens'],
            'title_lemmas': title_result['lemmas'],
            'title_pos': title_result['pos_tags'],
            'publish_time': row['publish_time'],
            'content_cleaned': row['content_cleaned'],
            'content_tokens': content_result['tokens'],
            'content_lemmas': content_result['lemmas'],
            'content_pos': content_result['pos_tags'],
            'sentence_count': content_result['sentence_count'],
            'token_count': content_result['token_count'],
            'sentences': content_result['sentences']
        })

    # 保存清洗后的CSV（保留原结构+清洗后正文）
    df_output = df[['url', 'title_cleaned', 'publish_time', 'content_cleaned']].copy()
    df_output.columns = ['url', 'title', 'publish_time', 'content']
    df_output.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig')
    print(f"[保存] 清洗后CSV已保存: {OUTPUT_CSV}")

    # 保存完整处理结果的JSON
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(processed_results, f, ensure_ascii=False, indent=2)
    print(f"[保存] 完整处理结果JSON已保存: {OUTPUT_JSON}")

    # 输出统计信息
    total_tokens = sum(r['token_count'] for r in processed_results)
    total_sentences = sum(r['sentence_count'] for r in processed_results)
    print(f"\n[统计] 处理完成!")
    print(f"  - 新闻总数: {len(processed_results)}")
    print(f"  - 总句数: {total_sentences}")
    print(f"  - 总词数(tokens): {total_tokens}")
    print(f"  - 平均每条新闻词数: {total_tokens // len(processed_results)}")


if __name__ == '__main__':
    main()