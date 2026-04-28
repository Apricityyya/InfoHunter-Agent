"""
InfoHunter - 信息采集模块
功能：从RSS源抓取文章列表
"""
import feedparser

# =====================配置：你想监控的RSS源 =====================
# 每个源有一个名字和一个RSS地址
RSS_SOURCES = [
    # ============== 技术趋势 =================
    {
        "name":"Hacker News (科技新闻)",
        "url":"https://hnrss.org/newest?count=10&q=AI+OR+LLM+OR+agent" #count=10表示只取最新10条，测试用

    },

    {
        "name": "CSDN博客-程序员小橙",
        "url": "https://blog.csdn.net/m0_64363449/rss/list"
    },

    {
        "name":"arXiv AI论文",
        "url":"https://rss.arxiv.org/rss/cs.AI"
    },

    {
        "name":"36kr 快讯",
        "url":"https://36kr.com/feed"
    },
    {
        "name":"MIT Technology Review",
        "url":"https://www.technologyreview.com/feed"
    },
    {
        "name":"开源中国",
        "url":"https://www.oschina.net/news/rss"
    },
    {
        "name":"V2EX 最热",
        "url":"https://www.v2ex.com/index.xml"
    }
]

def fetch_rss(source):
    """
    从一个RSS源抓取文章列表
    
    参数：
        source: 字典，包含name(源名称)和url(RSS地址)
        
    返回：
        文章列表，每篇文章是一个字典，包含title,link,published,summary,source
    """
    print(f"\n正在抓取：{source['name']}...")

    # feedparser.parse()会自动请求URL并解析XML，返回结构化数据
    feed = feedparser.parse(source["url"])

    articles=[]
    for entry in feed.entries[:10]: #[:10]表示只要前10篇文章就好，具体数值可以根据实际修改，也可以去掉此限制
        article = {
            "title":entry.get("title","无标题"),
            "link":entry.get("link",""),
            "published":entry.get("published","未知时间"),
            "summary":entry.get("summary","无摘要"),
            "source":source["name"],
        }
        articles.append(article)
    
    print(f"  √抓取到{len(articles)}篇文章")
    return articles

def fetch_all_rss():
    """
    遍历所有RSS源，抓取全部文章
    
    返回：
        所有文章的列表
    """
    all_articles=[]

    for source in RSS_SOURCES:
        try:
            articles = fetch_rss(source)
            all_articles.extend(articles) # 注意这里用的extend方法而不是append，二者区别在于：append把整体当一个元素加入，而extend把列表的元素逐个加进去
        except Exception as e:
            #某个源抓取失败不影响其它源
            print(f" ×抓取失败：{e}")
    return all_articles

# ==============运行入口==============
if __name__ == "__main__":
    print("="*50)
    print("InfoHunter - 信息采集测试")
    print("="*50)

    articles=fetch_all_rss()

    print(f"\n{'='*50}")
    print(f"共抓取到{len(articles)}篇文章：")
    print("="*50)

    for i,article in enumerate(articles,1):
        print(f"\n【{i}】{article['title']}")
        print(f"    来源：{article['source']}")
        print(f"    时间：{article['published']}")
        print(f"    链接：{article['link']}")
        # 摘要可能很长，先只显示前100个字符
        summary_preview=article["summary"][:100]+"..." if len(article["summary"])>100 else article["summary"]
        print(f"    摘要：{summary_preview}")
        