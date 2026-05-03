"""测试哪些 RSS 源在你的网络环境下能用"""
import feedparser

sources = [
    ("CSDN","https://blog.csdn.net/m0_64363449/rss/list"),
    ("豆瓣小组","https://rsshub.app/douban/group/729914/elite")
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