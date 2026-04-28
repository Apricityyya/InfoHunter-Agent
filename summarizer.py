"""
InfoHunter - AI摘要提炼模块
功能：用AI对文章进行摘要、打标签、分类
"""

import json
from openai import OpenAI
from config import DASHSCOPE_API_KEY,DASHSCOPE_BASE_URL,MODEL_NAME

client = OpenAI(
    api_key=DASHSCOPE_API_KEY,
    base_url=DASHSCOPE_BASE_URL,
)

# 摘要提炼的Prompt模板
# 这是整个模块最核心的部分——prompt写的好不好，直接决定摘要质量
SUMMARIZE_PROMPT = """你是一个专业的信息分析助手。请对以下文章进行分析，返回JSON格式结果。

要求：
1.summary：用中文写3-5句话概括文章核心内容，要求信息密度高，不要废话
2.tags：提取3-5个关键标签，用于分类检索
3.category：从以下类别中选一个最匹配的：AI技术、行业新闻、招聘信息、技术教程、学术论文、其他
4.importance：评估重要程度，1-5分，5分最重要

严格按照以下JSON格式返回，不要返回任何其他内容：
{{
    "summary": "中文摘要内容",
    "tags": ["标签1", "标签2", "标签3"],
    "category": "类别",
    "importance": 3
}} 

文章标题：{title}

文章内容：
{content}
"""


def summarize_article(title,content,max_content_length=3000):
    """
    用AI对文章进行摘要提炼

    参数：
        title:文章标题
        content:文章正文
        max_content_length:正文最大长度（截断以控制token消耗，可根据实际配置）
    
    返回：
        字典，包含summary,tags,category,importance
    """

    # 阶段过长的正文，控制API费用
    if len(content)>max_content_length:
        content=content[:max_content_length] + "...（正文已截断）"

    # 填充prompt模板
    prompt = SUMMARIZE_PROMPT.format(title=title,content=content)
        # f-string是先给出变量，再放入字符串
        # .format是先有了模板，再给出变量定义填入，注意它会把json格式的{xxx}当作占位符，所以要想保留就要再套一层{}来转义

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role":"user","content":prompt}
            ],
            # qwen3系列默认开启thinking模式，会额外消耗token
            # 摘要任务不需要深度思考，关闭以节省费用
            extra_body={"enable_thinking":False},
        )

        reply = response.choices[0].message.content.strip()

        # 解析JSON (LLM有时会在JSON外面包一层```json```，需要清理)
        if reply.startswith("```"):
            # 去掉首尾的```json````
            reply = reply.split("```")[1]
            if reply.startswith("json"):
                reply = reply[4:]
        reply = reply.strip()

        result = json.loads(reply)

        # 确保返回的字段完整
        return {
            "summary":result.get("summary","摘要生成失败"),
            "tags":result.get("tags",[]),
            "category":result.get("category","其他"),
            "importance":result.get("importance",3),
        }
    
    except json.JSONDecodeError:
        print(f"  ⚠ JSON解析失败，原始回复：{reply[:200]}")
        return {
            "summary": reply[:200] if reply else "摘要生成失败",
            "tags": [],
            "category": "其他",
            "importance": 3,
        }
    except Exception as e:
        print(f"  ✗ AI摘要失败：{e}")
        return {
            "summary": f"错误：{str(e)}",
            "tags": [],
            "category": "其他",
            "importance": 0,
        }
    

# =============================测试=========================
if __name__ == "__main__":
    # 用之前extractor抓一篇文章来测试
    from extractor import extract_article_content

    test_url = "https://www.technologyreview.com/2026/04/10/1135618/the-download-jeff-vandermeer-short-story-and-ai-models-too-danger-to-release/"

    print("=" * 50)
    print("InfoHunter - AI摘要测试")
    print("=" * 50)

    print("\n第1步：提取文章正文...")
    article = extract_article_content(test_url)
    print(f"  标题：{article['title']}")
    print(f"  正文长度：{article['content_length']} 字符")

    print("\n第2步：AI摘要分析中（需要几秒钟）...")
    result = summarize_article(article["title"], article["content"])

    print(f"\n{'=' * 50}")
    print("AI分析结果：")
    print(f"{'=' * 50}")
    print(f"摘要：{result['summary']}")
    print(f"标签：{', '.join(result['tags'])}")
    print(f"分类：{result['category']}")
    print(f"重要性：{'⭐' * result['importance']}")