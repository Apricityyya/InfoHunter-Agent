"""
InfoHunter - 一键抓取并推送简报
用法: python auto_brief.py
"""
from collector import fetch_all_rss
from subscription import load_subscriptions, keyword_filter
from store_articles import store_articles
from storage import ArticleStore
from notifier import push_to_wechat


def run():
    print("=" * 50)
    print("InfoHunter - 自动抓取并推送")
    print("=" * 50)

    # 第1步：抓取
    print("\n【第1步】抓取文章...")
    articles = fetch_all_rss()

    if not articles:
        print("没有抓取到文章")
        push_to_wechat("📢 InfoHunter", "今日未抓取到任何文章")
        return

    # 第2步：关键词过滤
    print("\n【第2步】过滤...")
    topics = load_subscriptions()["topics"]
    filtered = []
    for article in articles:
        matched = keyword_filter(article, topics)
        if matched:
            article["matched_topics"] = matched
            filtered.append(article)

    print(f"  {len(articles)} 篇 → 过滤后 {len(filtered)} 篇")

    # 第3步：存入向量库
    print("\n【第3步】存入向量库...")
    store = ArticleStore()
    store_articles(filtered, store)

    # 第4步：拼接简报并推送
    print("\n【第4步】推送到微信...")
    if not filtered:
        push_to_wechat("📢 InfoHunter", "今日无相关文章")
    else:
        content = f"共 {len(filtered)} 篇相关文章\n\n"
        for article in filtered:
            title = article.get("title", "")
            source = article.get("source", "")
            link = article.get("link", "")
            topics_str = ", ".join(article.get("matched_topics", []))
            content += f"- [{title}]({link})\n  来源: {source} | 话题: {topics_str}\n\n"
        push_to_wechat("📢 InfoHunter 每日简报", content)

    print("\n完成！")


if __name__ == "__main__":
    run()