"""测试分块功能"""
from storage import ArticleStore

store = ArticleStore()

test_text = """AI Agent 是一种能够自主决策的人工智能系统。
它通过感知环境、制定计划、执行行动来完成复杂任务。
Agent 的核心能力包括工具调用和推理规划。

RAG 是检索增强生成的缩写。
它通过从知识库中检索相关内容来增强 LLM 的回答能力。
RAG 系统的关键组件包括向量数据库和 Embedding 模型。

Prompt Engineering 是设计有效提示词的技术。
好的 prompt 能显著提升 LLM 的输出质量。"""

print("=== 固定长度分块 (100字) ===")
chunks1 = store.chunk_by_length(test_text, chunk_size=100)
for i, c in enumerate(chunks1):
    print(f"\nChunk {i+1} ({len(c)}字):")
    print(c)

print("\n=== 按段落分块 ===")
chunks2 = store.chunk_by_paragraph(test_text)
for i, c in enumerate(chunks2):
    print(f"\nChunk {i+1} ({len(c)}字):")
    print(c)