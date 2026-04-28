"""
InfoHunter - 手动导入模块
功能：支持两种导入方式
    1.粘贴URL -> 自动提取正文
    2.直接粘贴文本内容
"""

from extractor import extract_article_content

def import_from_url(url):
    """
    通过URL导入：自动提取网页正文

    参数：
        url:文章链接

    返回：
        标准化的文章字典
    """
    result = extract_article_content(url)

    article = {
        "title":result["title"],
        "linl":url,
        "published":"手动导入",
        "summary":result["content"][:200] + "..." if len(result["content"])>200 else result["content"],
        "source":"手动导入-URL",
    }

    return article


def import_from_text(text,title="手动导入的内容"):
    """
    直接粘贴文本导入

    参数：
        text:用户粘贴的文本内容
        title:可选标题，默认为“手动导入的内容”

    返回：
        标准化的文章字典
    """
    article = {
        "title": title,
        "link": "",
        "published": "手动导入",
        "summary": text[:200] + "..." if len(text) > 200 else text,
        "content": text,
        "source": "手动导入-文本",
    }

    return article


# =====================================交互式测试==========================
# if __name__ =="__main__":
#     print("=" * 50)
#     print("InfoHunter - 手动导入测试")
#     print("=" * 50)

#     print("\n请选择导入方式：")
#     print("  1. 粘贴URL")
#     print("  2. 直接输入文本")

#     choice=input("\n请输入 1 或者 2 :").strip()

#     if choice == "1":
#         url = input("请粘贴URL：").strip()
#         article = import_from_url(url)
#     elif choice =="2":
#         print("请输入文本（输入完按回车）：")
#         text = input().strip()
#         title = input("给它起个标题（直接回车跳过）：").strip()
#         if title:
#             article = import_from_text(text, title)
#         else:
#             article = import_from_text(text)
#     else:
#         print("无效选择")
#         exit()

#     print(f"\n{'=' * 50}")
#     print("导入成功！")
#     print(f"{'=' * 50}")
#     print(f"标题：{article['title']}")
#     print(f"来源：{article['source']}")
#     print(f"摘要：{article['summary']}")

def smart_import(user_input, title="手动导入的内容"):
    """
    智能导入：自动判断用户输入是URL还是纯文本

    判断逻辑：如果输入以 http:// 或 https:// 开头，当作URL处理；
    否则当作纯文本处理。

    参数：
        user_input: 用户粘贴的内容
        title: 纯文本时的可选标题

    返回：
        标准化的文章字典
    """
    text = user_input.strip()# strip是一种字符串方法，去掉首尾空格和换行符

    if text.startswith("http://") or text.startswith("https://"):
        print("  → 检测到URL，正在提取网页正文...")
        return import_from_url(text)
    else:
        print("  → 检测到文本内容，直接导入...")
        return import_from_text(text, title)


# ============ 交互式测试 ============
if __name__ == "__main__":
    print("=" * 50)
    print("InfoHunter - 手动导入测试")
    print("=" * 50)

    print("\n请直接粘贴内容（URL或文本均可）：")
    user_input = input().strip()

    article = smart_import(user_input)

    print(f"\n{'=' * 50}")
    print("导入成功！")
    print(f"{'=' * 50}")
    print(f"标题：{article['title']}")
    print(f"来源：{article['source']}")
    print(f"摘要：{article['summary']}")