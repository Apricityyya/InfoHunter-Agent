"""
InfoHunter - 网页正文提取模块
功能：给定一个URL，提取网页的正文文本
"""

import requests # http请求库
from bs4 import BeautifulSoup # html解析库


def extract_article_content(url,timeout=10):
    """
    从URL提取网页正文

    参数：
        url:文章链接
        timeout:请求超时时间（秒）

    返回：
        字典，包含title（网页标题）和content（正文文本）
    """
    try:
        # 1.发送HTTP请求获取网页HTML
        #   headers模拟浏览器，有些网站会拒绝没有User-Agent的请求
        headers = {
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Wind64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url,headers=headers,timeout=timeout)# 请求网页，拿到html
        response.raise_for_status() #如果状态码不是200，抛出异常

        # 2.用BeautifulSoup解析HTML
        soup = BeautifulSoup(response.text,"html.parser")# 解析HTML

        # 3.提取标题
        title = soup.title.string if soup.title else "无标题"

        # 4.移除不需要的标签（脚本、样式、导航栏等）
        for tag in soup(["script","style","nav","header","footer","aside"]):
            tag.decompose()

        # 5.提取正文
        #   有线找<article>标签，就找<body>里的所有<p>标签
        paragraphs = soup.find_all("p")
        text = "\n".join(p.get_text(strip=True) for p in paragraphs)

        # 6.清理：去掉多余空行
        text_lines = [line.strip()for line in text.split("\n") if line.strip()]
        clean_text = "\n".join(text_lines)

        return{
            "title":title.strip(),
            "content":clean_text,
            "content_length":len(clean_text),
        }
    
    except Exception as e:
        return{
            "title":"提取失败",
            "content":f"错误：{str(e)}",
            "content_length":0,
        }
    
# =========================测试==============================
if __name__ == "__main__":
    # 用一篇刚才抓到的MIT Technology Review文章测试
    test_url = "https://www.technologyreview.com/2026/04/13/1135707/the-download-how-humans-make-decisions-and-modernas-vaccine-word-games/"

    print("=" * 50)
    print("InfoHunter - 正文提取测试")
    print("=" * 50)
    print(f"\n正在提取：{test_url}\n")

    result = extract_article_content(test_url)
    print(f"标题：{result['title']}")
    print(f"正文长度：{result['content_length']} 字符")
    print(f"\n--- 正文前500字 ---")
    print(result["content"][:500])