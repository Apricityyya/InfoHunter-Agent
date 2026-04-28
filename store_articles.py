"""
InfoHunter - 把文章批量导入向量数据库
"""
from storage import ArticleStore


def store_articles(articles, store):
    """
    把文章列表批量存入向量数据库

    参数:
        articles: 文章列表（每篇是字典，包含 title, summary/content, source, published）
        store: ArticleStore 实例
    """
    # 任务: 遍历 articles，逐篇存入
    #
    # 提示:
    #   - article_id 可以用 str(i) 或者用文章的 link 做唯一标识
    #   - 存入的文本建议用 title + summary（摘要通常比正文更精炼）
    #   - 用 try/except 包裹，某篇存失败不影响其他篇
    #   - 用 enumerate 获取序号
    #
    # 注意: 先检查数据库里已有多少条数据
    #       article_id 不能重复！如果数据库里已有 5 条，新的 id 应该从 6 开始
    #       用 store.get_count() 获取当前数量，作为起始编号

    existing_count = store.get_count()
    print(f"数据库已有 {existing_count} 条记录")

    # TODO: 你来写循环存入的逻辑
    for i,article in enumerate(articles):
        article_id = str(existing_count + i + 1)
        title = article.get("title","无标题")
        content = article.get("summary","")
        source = article.get("source","")
        date = article.get("published","")
        link = article.get("link","")
        try:
            store.add_article(article_id,title,content,source,date,link)
        except Exception as e:
            print(f"{article['title']}存储失败，失败原因：{e}")
    print(f"总计新存入 {store.get_count()- existing_count} 篇文章")


if __name__ == "__main__":
    print("=" * 50)
    print("InfoHunter - 文章导入向量数据库")
    print("=" * 50)

    store = ArticleStore()

    # 用假数据测试（模拟 pipeline 处理完的结果）
    test_articles = [
        {
            "title": "AI Agent 工具调用机制详解",
            "summary": "Agent 通过 Function Calling 机制调用外部工具，实现搜索、计算等功能。ReAct 模式让 Agent 能够交替进行推理和行动。",
            "source": "Hacker News",
            "published": "2026-04-20",
            "link": "https://example.com/1",
        },
        {
            "title": "RAG 系统中的分块策略对比",
            "summary": "对比了固定长度分块、按段落分块、语义分块三种策略。实验表明语义分块在问答场景下检索准确率最高，但实现复杂度也最高。",
            "source": "AI Blog",
            "published": "2026-04-19",
            "link": "https://example.com/2",
        },
        {
            "title": "Prompt Engineering 最佳实践",
            "summary": "好的 prompt 应该包含角色设定、任务描述、输出格式要求和示例。Chain-of-Thought 提示能显著提升推理任务的准确率。",
            "source": "AI Blog",
            "published": "2026-04-18",
            "link": "https://example.com/3",
        },
        {
            "title": "向量数据库选型指南",
            "summary": "对比了 ChromaDB、FAISS、Milvus、Pinecone 四种方案。ChromaDB 适合小型项目快速原型，Milvus 适合大规模生产环境。",
            "source": "TechCrunch",
            "published": "2026-04-17",
            "link": "https://example.com/4",
        },
        {
            "title": "LangChain 与 LlamaIndex 框架对比",
            "summary": "LangChain 更适合构建 Agent 和复杂工作流，LlamaIndex 更专注于 RAG 和数据索引。两者可以结合使用。",
            "source": "Hacker News",
            "published": "2026-04-16",
            "link": "https://example.com/5",
        },
    ]

    store_articles(test_articles, store)

    # 验证：搜索测试
    print(f"\n{'=' * 50}")
    print("导入后搜索测试")
    print("=" * 50)

    queries = ["Agent 怎么调用工具？", "哪种分块方式效果最好？", "ChromaDB 和 Milvus 哪个好？"]

    for q in queries:
        print(f"\n问题: {q}")
        results = store.search(q, n_results=2)
        for i, (doc, meta) in enumerate(zip(results["documents"][0], results["metadatas"][0])):
            print(f"  {i+1}. [{meta['source']}] {meta['title']}")