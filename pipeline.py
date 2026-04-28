"""
InfoHunter - 核心Pipeline
功能：串联 “采集 → 过滤 → 提取正文 → AI摘要 → 存入向量库” 的完整流程
"""

from collector import fetch_all_rss
from extractor import extract_article_content
from summarizer import summarize_article
from subscription import filter_articles


def run_pipeline():
    """
    运行完整的信息处理流程：
    1. 从RSS源抓取文章
    2. 用关键词+AI过滤出相关文章
    3. 提取正文并生成AI摘要
    """
    print("=" * 50)
    print("InfoHunter - 完整Pipeline运行")
    print("=" * 50)

    # 第1步：抓取
    print("\n【第1步】抓取文章...")
    articles = fetch_all_rss()

    if not articles:
        print("没有抓取到任何文章，流程结束")
        return []

    # 第2步：过滤
    print("\n【第2步】过滤文章...")
    filtered = filter_articles(articles)

    if not filtered:
        print("过滤后没有相关文章，流程结束")
        return []

    # 第3步：提取正文 + AI摘要
    print(f"\n【第3步】对 {len(filtered)} 篇文章提取正文并生成AI摘要...")
    results = []

    for i, article in enumerate(filtered, 1):
        print(f"\n  处理第 {i}/{len(filtered)} 篇：{article['title'][:50]}...")

        # 提取正文（如果有链接的话）
        content = article.get("summary", "")
        if article.get("link"):
            print(f"    提取正文中...")
            extracted = extract_article_content(article["link"])
            if extracted["content_length"] > 0:
                content = extracted["content"]
                print(f"    正文长度：{extracted['content_length']} 字符")
            else:
                print(f"    正文提取失败，使用RSS摘要")

        # AI摘要
        print(f"    AI摘要生成中...")
        ai_result = summarize_article(article["title"], content)

        # 合并所有信息
        article["ai_summary"] = ai_result["summary"]
        article["tags"] = ai_result["tags"]
        article["category"] = ai_result["category"]
        article["importance"] = ai_result["importance"]
        results.append(article)

    # 展示最终结果
    print(f"\n{'=' * 50}")
    print(f"Pipeline完成！共处理 {len(results)} 篇文章")
    print(f"{'=' * 50}")

    for i, article in enumerate(results, 1):
        print(f"\n{'─' * 40}")
        print(f"【{i}】{article['title']}")
        print(f"  来源：{article['source']}")
        print(f"  话题：{', '.join(article.get('matched_topics', []))}")
        print(f"  分类：{article['category']}")
        print(f"  重要性：{'⭐' * article['importance']}")
        print(f"  AI摘要：{article['ai_summary']}")
        print(f"  标签：{', '.join(article['tags'])}")
        print(f"  AI筛选理由：{article.get('ai_reason', '无')}")
        print(f"  链接：{article.get('link', '无')}")

    return results


if __name__ == "__main__":
    run_pipeline()