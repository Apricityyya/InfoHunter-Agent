"""
InfoHunter - 向量存储模块
功能：把文章存入 ChromaDB，支持语义搜索
"""
import chromadb
from openai import OpenAI
from config import DASHSCOPE_API_KEY, DASHSCOPE_BASE_URL


class ArticleStore:

    def __init__(self, db_path="./chroma_db", collection_name="articles"):
        """
        初始化：创建 Embedding 客户端 + ChromaDB 连接

        参数:
            db_path: ChromaDB 数据存储路径
            collection_name: 集合名称
        """
        # AI 客户端（用来调 Embedding API）
        self.client = OpenAI(
            api_key=DASHSCOPE_API_KEY,
            base_url=DASHSCOPE_BASE_URL,
        )

        # ChromaDB 客户端 + 集合
        self.chroma = chromadb.PersistentClient(path=db_path)
        self.collection = self.chroma.get_or_create_collection(name=collection_name)

    def get_embedding(self, text):
        """
        把一段文字变成向量

        参数:
            text: 字符串
        返回:
            一个列表，包含 1024 个浮点数
        """
        # TODO: 调用 self.client.embeddings.create(...)
        # 提示: 跟你刚才 test_embedding.py 里的写法一样
        #       model 用 "text-embedding-v3"
        #       input 用 [text]（注意要包在列表里）
        #       返回 response.data[0].embedding
        response = self.client.embeddings.create(
            model = "text-embedding-v3",
            input = [text],
        )
        return response.data[0].embedding

    def add_article(self, article_id, title, content, source="", date="",link=""):
        """
        把一篇文章存入向量数据库

        参数:
            article_id: 唯一标识（字符串）
            title: 文章标题
            content: 文章内容（用来生成向量的文本）
            source: 来源
            date: 日期
        """
        # TODO:
        # 第1步: 把 title + content 拼成一段文字，调用 self.get_embedding 获取向量
        # 第2步: 调用 self.collection.add(...) 存入 ChromaDB
        #   - ids: [article_id]
        #   - documents: [拼接的文字]
        #   - embeddings: [向量]
        #   - metadatas: [{"title": title, "source": source, "date": date}]
        text = f"{title} {content}"
        vector = self.get_embedding(text)
        self.collection.add(
            ids = [article_id],
            documents = [text],
            embeddings = [vector],
            metadatas = [{"title":title,"source":source,"date":date,"link":link}],
        )

    def search(self, query, n_results=5):
        """
        语义搜索：输入问题，返回最相关的文章

        参数:
            query: 用户的问题（字符串）
            n_results: 返回几条结果

        返回:
            搜索结果（ChromaDB 返回的字典）
        """
        # TODO:
        # 第1步: 把 query 变成向量
        # 第2步: 调用 self.collection.query(query_embeddings=[向量], n_results=n_results)
        # 第3步: return 结果
        query_vector = self.get_embedding(query)
        results = self.collection.query(
            query_embeddings=[query_vector],
            n_results = n_results,
        )
        return results

    def get_count(self):
        """返回数据库中的文章总数"""
        return self.collection.count()
    

    def chunk_by_length(self,text,chunk_size=200):
        """
        固定长度分块，默认是200

        参数：
            text: 原始文本
            chunk_size: 每块的字符数

        返回：
            字符串列表，每个元素是一个chunk
        
        逻辑：
            从头开始，每chunk_size个字符切一块
            最后不足chunk_size的部分也保留

        提示：用切片 text[start:end]来截取
        """
        chunks = []
        for i in range(0,len(text),chunk_size): # range(起点, 终点, 步长)
            chunks.append(text[i:i+chunk_size]) # 切片自动处理最后不足一块的情况
        return chunks
    

    def chunk_by_paragraph(self,text):
        """
        按段落分块

        参数：
            text: 原始文本

        返回：
            字符串列表，每个元素是一个段落

        逻辑：
            按换行符切分，过滤掉空行

        提示：
            - text.split("\n")按换行符切分
            - 过滤掉空字符串和纯空格的行
        """
        chunks = [line.strip() for line in text.split("\n") if line.strip()]
        return chunks
        


# ============================================
# 测试代码
# ============================================
if __name__ == "__main__":
    print("=" * 50)
    print("InfoHunter - 向量存储测试")
    print("=" * 50)

    store = ArticleStore()

    # 存入测试文章
    test_articles = [
        ("1", "AI Agent 自动化工作流", "本文介绍了如何构建 AI Agent 实现自动化工作流，包括工具调用和任务规划", "Hacker News", "2026-04-20"),
        ("2", "大模型 RAG 检索优化", "RAG 系统中检索质量直接影响回答质量，本文对比了多种分块策略", "AI Blog", "2026-04-19"),
        ("3", "Python 3.14 新特性", "Python 3.14 引入了多项性能优化和语法改进", "TechCrunch", "2026-04-18"),
        ("4", "LangChain Agent 详解", "LangChain 框架中 Agent 的核心概念包括工具定义和 ReAct 循环", "Hacker News", "2026-04-17"),
        ("5", "前端框架趋势", "React 和 Vue 在 2026 年的竞争格局分析", "Medium", "2026-04-16"),
    ]

    print("\n--- 存入文章 ---")
    for aid, title, content, source, date in test_articles:
        store.add_article(aid, title, content, source, date)
        print(f"  已存入: {title}")

    print(f"\n数据库文章总数: {store.get_count()}")

    # 语义搜索测试
    print("\n--- 语义搜索测试 ---")
    queries = [
        "AI Agent 怎么开发？",
        "如何提升检索效果？",
        "前端用什么框架好？",
    ]

    for q in queries:
        print(f"\n问题: {q}")
        results = store.search(q, n_results=2)
        for i, (doc, meta) in enumerate(zip(results["documents"][0], results["metadatas"][0])):
            print(f"  {i+1}. [{meta['source']}] {meta['title']}")
            print(f"     内容片段: {doc[:80]}...")