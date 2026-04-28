"""测试哪些 RSS 源在你的网络环境下能用"""
import feedparser

sources = [
    ("InfoQ 中文", "https://feed.infoq.com/cn"),
    ("机器之心", "https://www.jiqizhixin.com/rss"),
    ("36kr", "https://36kr.com/feed"),
    ("开源中国", "https://www.oschina.net/news/rss"),
    ("V2EX 最热", "https://www.v2ex.com/index.xml"),
    ("知乎每日精选", "https://www.zhihu.com/rss"),
    ("Hacker News AI", "https://hnrss.org/newest?count=5&q=AI+OR+LLM"),
    ("GitHub Trending", "https://rsshub.app/github/trending/daily/python"),
    ("少数派", "https://sspai.com/feed"),
    ("MIT Tech Review", "https://www.technologyreview.com/feed"),
]

for name, url in sources:
    try:
        feed = feedparser.parse(url)
        count = len(feed.entries)
        if count > 0:
            print(f"✅ {name}: 抓到 {count} 篇")
            print(f"   示例: {feed.entries[0].get('title', '无标题')[:50]}")
        else:
            print(f"❌ {name}: 能访问但没有内容")
    except Exception as e:
        print(f"❌ {name}: 失败 - {e}")