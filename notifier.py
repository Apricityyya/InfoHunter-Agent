"""
InfoHunter - 微信推送模块
功能：通过 Server酱 把消息推送到微信
"""

import requests
from config import SERVER_CHAN_KEY

def push_to_wechat(title,content=""):
    """
    推送消息到微信

    参数：
        title：消息标题(微信通知栏显示的内容，最多32字)
        content：消息正文(支持Markdown格式)
    
    返回：
        True(成功) 或 False(失败)
    """
    # 任务: 
    # 1. 如果 SERVER_CHAN_KEY 为空，打印提示并返回 False
    # 2. 拼接 URL: f"https://sctapi.ftqq.com/{SERVER_CHAN_KEY}.send"
    # 3. 用 requests.post(url, data={"title": title, "desp": content}) 发送
    # 4. 用 try/except 包裹，失败时打印错误并返回 False
    # 5. 成功时返回 True
    if not SERVER_CHAN_KEY:
        print(f"Server酱未开通")
        return False
    url = f"https://sctapi.ftqq.com/{SERVER_CHAN_KEY}.send"
    try:
        requests.post(url,data={"title":title,"desp":content})
        return True
    except Exception as e:
        print(f"推送失败：{e}")
        return False


def push_daily_brief(articles):
    """
    把文章列表格式化成每日简报，推送到微信

    参数:
        articles: 文章列表（每篇是字典，包含 title, source, matched_topics）
    """
    if not articles:
        push_to_wechat("📢 InfoHunter 今日无相关文章")
        return

    # 任务:
    # 拼接简报内容（Markdown 格式），然后调用 push_to_wechat 推送
    # 
    # 格式示例:
    #   ## 📢 InfoHunter 每日简报
    #   共发现 X 篇相关文章
    #   
    #   ### AI Agent开发
    #   - 文章标题1 (来源)
    #   - 文章标题2 (来源)
    #   
    #   ### 行业动态
    #   - 文章标题3 (来源)
    #
    # 提示:
    #   - 先按 matched_topics 分组（哪些文章属于哪个话题）
    #   - 一篇文章可能匹配多个话题，放到第一个匹配的话题下就行
    #   - 用 Markdown 的 ### 做话题标题，- 做列表项
    # TODO: 你来写
    brief_report = "## 📢 InfoHunter 每日简报\n"
    brief_report += f"共发现 {len(articles)} 篇相关文章\n\n"
    
    # 按话题分组
    groups = {}
    for article in articles:
        topic = article.get("matched_topics",["其它"])[0]
        if topic not in groups:
            groups[topic] = []
        groups[topic].append(article)
    
    # 拼接每个话题的文章列表
    for topic_name, article_list in groups.items():
        brief_report += f"### {topic_name}\n"
        for article in article_list:
            brief_report += f"- {article.get('title', '')} ({article.get('source', '')})\n"
        brief_report += "\n"

# ============================================
# 测试
# ============================================
if __name__ == "__main__":
    print("测试 Server酱 推送...")
    
    # 测试1: 简单推送
    result = push_to_wechat(
        "🔍 InfoHunter 测试",
        "如果你在微信收到这条消息，说明推送配置成功！"
    )
    print(f"推送结果: {'成功' if result else '失败'}")

