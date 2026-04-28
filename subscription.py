"""
InfoHunter - 关键词订阅管理模块
功能：
    1.管理用户关注的话题和关键词
    2.两层过滤：关键词粗筛 + AI精筛
"""

import json
import os
from openai import OpenAI
from config import DASHSCOPE_API_KEY,DASHSCOPE_BASE_URL,MODEL_NAME

client = OpenAI(
    api_key=DASHSCOPE_API_KEY,
    base_url=DASHSCOPE_BASE_URL,
)

# 订阅配置文件路径
SUBSCRIPTION_FILE = "subscriptions.json"

# 默认订阅配置
DEFAULT_SUBSCRIPTIONS = {
    "topics":[
        {
            "name":"AI Agent开发",
            "keywords":["AI Agent","LLM","大模型","langchain","RAG","Langchain"]
        },
        {
            "name":"实习招聘",
            "keywords":["intern","实习","招聘","校招","hiring","内推"]
        },
    ]
}



def load_subscriptions():
    """加载订阅配置，如果文件不存在则创建默认配置"""
    if os.path.exists(SUBSCRIPTION_FILE):
        with open(SUBSCRIPTION_FILE,"r",encoding="utf-8") as f:
            return json.load(f)
    else:
        save_subscriptions(DEFAULT_SUBSCRIPTIONS)
        return DEFAULT_SUBSCRIPTIONS
    

def save_subscriptions(subs):
    """保存订阅配置到文件"""
    with open(SUBSCRIPTION_FILE,"w",encoding="utf-8") as f:
        json.dump(subs,f,ensure_ascii=False,indent=2)


def add_topic(name,keywords):
    """
    添加一个新的关注话题
    
    参数：
        name:话题名称：如"AI Agent开发"
        keywords:关键词列表，如["agent","LLM"]
    """
    subs = load_subscriptions()
    subs["topics"].append({"name":name,"keywords":keywords})
    save_subscriptions(subs)
    print(f"  ✓ 已添加话题：{name}，关键词：{keywords}")



def remove_topic(name):
    """删除一个关注话题"""
    subs = load_subscriptions()
    subs["topics"]=[t for t in subs["topics"] if t["name"] != name]
    # 列表推导式 [要保留的东西  for  变量  in  列表  if  条件]
    save_subscriptions(subs)
    print(f"  ✓ 已删除话题：{name}")


def show_topics():
    """显示当前所有关注话题"""
    subs=load_subscriptions()
    print("\n当前关注话题：")
    for i, topic in enumerate(subs["topics"], 1):
        print(f"  {i}. {topic['name']}")
        print(f"     关键词：{', '.join(topic['keywords'])}")
    return subs["topics"]



# ============ 第一层：关键词粗筛（免费、快速） ============

def keyword_filter(article,topics):
    """
    用关键词匹配做粗筛

    逻辑：文章的标题或摘要用包含任何一个关注话题的关键词，就保留

    参数：
        article：文章字典，需要有title和summary字段
        topics：话题列表

    返回：
        匹配到的话题名称列表，空列表表示不匹配
    """

    text = (article.get("title","") + " " + article.get("summary","")).lower()

    matched_topics = []
    for topic in topics:
        for keyword in topic["keywords"]:
            if keyword.lower() in text:
                matched_topics.append(topic["name"])
                break # 一个话题匹配到一个关键词就够了

    return matched_topics


# ============ 第二层：AI精筛（更准确，消耗少量token） ============

RELEVANCE_PROMPT = """判断以下文章是否与用户关注的话题相关。

用户关注的话题：{topics}

文章标题：{title}
文章摘要：{summary}

请只返回JSON格式，不要返回其他内容：
{{
    "is_relevant":true或false,
    "matched_topic":"最匹配的话题名称，不相关则填空字符串",
    "reson":"这篇文章与XX话题相关，因为它讨论了XX内容"
}}"""



def ai_relevance_check(article,topics):
    """
    用AI判断文章与关注话题的相关性（精筛）

    参数：
        article:文章字典
        topics:话题列表

    返回：
        字典，包含 is_relevant,matched_topic,reason
    """

    topic_names = [t["name"] for t in topics]

    prompt = RELEVANCE_PROMPT.format(
        topics="、".join(topic_names),
        title = article.get("title",""),
        summary = article.get("summary","")[:300],
    )


    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role":"user","content":prompt}],
            extra_body={"enable_thinking":False},
        )

        reply = response.choices[0].message.content.strip()

        if reply.startswith("```"):
            reply = reply.split("```")[1]
            if reply.startswith("json"):
                reply = reply[4:]
        reply = reply.strip()

        return json.loads(reply)

    except Exception as e:
        print(f"  ⚠ AI判断失败：{e}")
        return {"is_relevant": True, "matched_topic": "", "reason": "AI判断失败，默认保留"}
    


# ============ 完整的两层过滤流程 ============


def filter_articles(articles):
    """
    对文章列表进行两层过滤

    流程：
        1.关键词粗筛（块、免费）
        2.AI精筛（准、花费少）

    参数：
        articles：文章列表

    返回：
        过滤后的文章列表，每篇文章会被添加matched_topics字段
    """

    topics = load_subscriptions()["topics"]

    if not topics:
        print("  ⚠ 没有设置关注话题，返回所有文章")
        return articles
    
    # 第一层：关键词粗筛
    print(f"\n第一层过滤：关键词粗筛...")
    keyword_passed = []
    for article in articles:
        matched = keyword_filter(article,topics)
        if matched:
            article["matched_topics"] = matched
            keyword_passed.append(article)

    print(f"  {len(articles)} 篇 → 关键词匹配 {len(keyword_passed)} 篇")  

    if not keyword_passed:
        print("  关键词未匹配任何文章，跳过AI精筛")
        return []
    
    # 第二层：AI精筛
    print(f"\n第二次过滤：AI精筛...")
    ai_passed = []
    for article in keyword_passed:
        result = ai_relevance_check(article,topics)
        if result.get("is_relevant",False):
            article["ai_reason"] = result.get("reason","")
            ai_passed.append(article)
            print(f"  ✓ 保留：{article['title'][:40]}... | {result.get('reason', '')}")
        else:
            print(f"  ✗ 过滤：{article['title'][:40]}... | {result.get('reason', '')}")

    print(f"\n  最终保留 {len(ai_passed)}/{len(articles)} 篇文章")
    return ai_passed



# ============ 测试 ============
if __name__ == "__main__":
    from collector import fetch_all_rss

    print("=" * 50)
    print("InfoHunter - 订阅过滤测试")
    print("=" * 50)

    # 显示当前订阅
    show_topics()

    # 抓取文章
    print("\n正在抓取文章...")
    articles = fetch_all_rss()

    # 过滤
    filtered = filter_articles(articles)

    # 展示结果
    print(f"\n{'=' * 50}")
    print("过滤后的文章：")
    print(f"{'=' * 50}")
    for i, article in enumerate(filtered, 1):
        print(f"\n【{i}】{article['title']}")
        print(f"    匹配话题：{', '.join(article.get('matched_topics', []))}")
        print(f"    AI判断：{article.get('ai_reason', '')}")