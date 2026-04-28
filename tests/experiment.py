"""
InfoHunter - 分块策略对比实验
"""
from storage import ArticleStore


# 3 篇测试文章（模拟较长的内容）
TEST_ARTICLES = [
    {
        "id": "1",
        "title": "AI Agent 开发完全指南",
        "content": """AI Agent 是一种能够自主决策的人工智能系统。它通过感知环境、制定计划、执行行动来完成复杂任务。
Agent 的核心能力包括工具调用（Tool Calling）和推理规划。通过 Function Calling 机制，Agent 可以调用搜索引擎、计算器、数据库等外部工具。
ReAct 是目前最流行的 Agent 框架模式。它让 Agent 交替进行推理（Reasoning）和行动（Acting），每一步都基于上一步的观察结果来决定下一步操作。
LangChain 和 LlamaIndex 是两个主流的 Agent 开发框架。LangChain 更适合构建复杂工作流，LlamaIndex 更专注于数据索引和检索。""",
        "source": "Hacker News",
    },
    {
        "id": "2",
        "title": "RAG 系统最佳实践",
        "content": """RAG（Retrieval-Augmented Generation）是检索增强生成的缩写。它通过从知识库中检索相关内容来增强 LLM 的回答能力。
RAG 系统的关键组件包括向量数据库和 Embedding 模型。Embedding 模型将文本转化为高维向量，向量数据库负责存储和检索这些向量。
分块策略是 RAG 系统中最重要的工程决策之一。固定长度分块简单但可能切断语义，按段落分块保持语义完整但长度不均匀。
检索时使用 Top-K 策略，返回与查询最相似的 K 个文档片段。K 值过小可能遗漏关键信息，过大会引入噪声干扰 LLM 的回答。""",
        "source": "AI Blog",
    },
    {
        "id": "3",
        "title": "Prompt Engineering 实战技巧",
        "content": """Prompt Engineering 是设计有效提示词的技术。好的 prompt 能显著提升 LLM 的输出质量和准确性。
基本原则包括：角色设定（让 LLM 扮演专家）、任务描述（清晰说明要做什么）、输出格式（指定 JSON 等结构化格式）、示例（提供 few-shot 样例）。
Chain-of-Thought（CoT）是一种重要的提示技巧。它要求 LLM 逐步推理而不是直接给答案，在数学和逻辑任务中效果显著。
Zero-shot CoT 只需在 prompt 末尾加上"请一步步思考"就能激活 LLM 的推理能力，无需提供示例。""",
        "source": "AI Blog",
    },
]

# 5 个测试问题 + 期望找到的文章编号
TEST_QUERIES = [
    {"question": "Agent 怎么调用外部工具？", "expected": "1"},
    {"question": "RAG 的分块策略有哪些？", "expected": "2"},
    {"question": "什么是 Chain-of-Thought？", "expected": "3"},
    {"question": "ReAct 模式是什么？", "expected": "1"},
    {"question": "Embedding 模型有什么用？", "expected": "2"},
]


def run_experiment(chunk_method, collection_name):
    """
    用指定的分块策略存入文章并测试检索效果

    参数:
        chunk_method: "length" 或 "paragraph"
        collection_name: ChromaDB 集合名称

    返回:
        正确检索的数量
    """
    store = ArticleStore(collection_name=collection_name)

    # 第1步：分块并存入
    print(f"\n--- 存入文章（{chunk_method} 分块）---")
    chunk_count = 0

    for article in TEST_ARTICLES:
        # 任务: 根据 chunk_method 选择分块方式
        #   如果是 "length" → 调用 store.chunk_by_length(article["content"])
        #   如果是 "paragraph" → 调用 store.chunk_by_paragraph(article["content"])
        #
        # 然后遍历 chunks，逐个存入:
        #   article_id 用 "文章id_chunk序号"，如 "1_0", "1_1", "1_2"
        #   title 用原文章标题
        #   content 用当前 chunk 的内容
        #   source 用原文章 source
        #
        # TODO: 你来写
        if chunk_method == "length":
            chunks = store.chunk_by_length(article["content"])
        elif chunk_method == "paragraph":
            chunks = store.chunk_by_paragraph(article["content"])
        for i,chunk in enumerate(chunks):
            store.add_article(f"{article['id']}_{i}",article["title"],chunk,article["source"])
            chunk_count += 1

    print(f"  共存入 {chunk_count} 个 chunks")

    # 第2步：检索测试
    print(f"\n--- 检索测试（{chunk_method}）---")
    correct = 0

    for q in TEST_QUERIES:
        results = store.search(q["question"], n_results=1)
        # 取返回结果的第一个 chunk 的 id，提取文章编号
        # id 格式是 "1_0"，用 split("_")[0] 取文章编号
        top_id = results["ids"][0][0].split("_")[0]

        is_correct = top_id == q["expected"]
        if is_correct:
            correct += 1

        status = "✅" if is_correct else "❌"
        top_title = results["metadatas"][0][0]["title"]
        print(f"  {status} 问: {q['question']}")
        print(f"     找到: {top_title} (id={top_id}, 期望={q['expected']})")

    return correct


# ============================================
# 运行实验
# ============================================
if __name__ == "__main__":
    print("=" * 50)
    print("分块策略对比实验")
    print("=" * 50)

    # 实验1：固定长度分块
    score1 = run_experiment("length", "exp_length")

    # 实验2：按段落分块
    score2 = run_experiment("paragraph", "exp_paragraph")

    # 结果对比
    print(f"\n{'=' * 50}")
    print("实验结果")
    print(f"{'=' * 50}")
    print(f"固定长度分块: {score1}/{len(TEST_QUERIES)} 正确")
    print(f"按段落分块:   {score2}/{len(TEST_QUERIES)} 正确")

    if score2 > score1:
        print("\n结论: 按段落分块在本实验中检索准确率更高")
    elif score1 > score2:
        print("\n结论: 固定长度分块在本实验中检索准确率更高")
    else:
        print("\n结论: 两种策略在本实验中表现相当")