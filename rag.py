"""
InfoHunter - RAG 问答模块
功能：基于向量检索结果，用 LLM 生成有依据的回答
"""
from openai import OpenAI
from config import DASHSCOPE_API_KEY, DASHSCOPE_BASE_URL, MODEL_NAME
from storage import ArticleStore

# RAG 的 prompt 模板
# 注意用 .format()，因为变量在调用时才传入
RAG_PROMPT = """你是一个专业的信息分析助手。请根据以下参考资料回答用户的问题。

要求：
1. 只基于提供的参考资料回答，不要编造信息
2. 如果参考资料中没有相关内容，请如实说明
3. 回答时注明信息来源（如"根据[来源名]的报道..."）
4. 回答时使用与用户相同的语言，简洁清晰

参考资料：
{context}

用户问题：{question}
"""


class RAGEngine:

    def __init__(self):
        """初始化：创建 LLM 客户端 + 文章存储"""
        self.llm_client = OpenAI(
            api_key=DASHSCOPE_API_KEY,
            base_url=DASHSCOPE_BASE_URL,
        )
        self.store = ArticleStore()

    # 任务1: build_context
    # 功能: 把搜索结果拼成一段"参考资料"文本
    # 输入: search_results（ChromaDB 返回的结果）
    # 返回: 一个字符串，格式如下：
    #
    #   [1] 来源: Hacker News
    #   标题: AI Agent 工具调用机制详解
    #   内容: Agent 通过 Function Calling 机制...
    #
    #   [2] 来源: AI Blog
    #   标题: ...
    #   内容: ...
    #
    # 提示:
    #   - search_results["documents"][0] 是文档列表
    #   - search_results["metadatas"][0] 是元数据列表
    #   - 用 zip() 同时遍历两个列表
    #   - 用 enumerate 加序号
    def build_context(self, search_results):
        context = ""
        documents = search_results["documents"][0]
        metadatas = search_results["metadatas"][0]
        for i,(doc,meta) in enumerate(zip(documents,metadatas)):
            context += f"[{i+1}] 来源: {meta.get('source','')}\n"
            context += f"标题: {meta.get('title','')}\n"
            context += f"内容: {doc}\n\n"
        return context
 
    # 任务2: ask
    # 功能: 完整的 RAG 问答流程
    # 输入: question（用户问题），n_results（检索几篇，默认3）
    # 返回: LLM 的回答字符串
    #
    # 步骤:
    #   1. 调用 self.store.search(question, n_results) 检索相关文章
    #   2. 调用 self.build_context(results) 构建参考资料
    #   3. 用 RAG_PROMPT.format(context=..., question=...) 填充模板
    #   4. 调用 self.llm_client.chat.completions.create(...) 发给 LLM
    #   5. 返回 LLM 的回复
    #
    # 提示: LLM 调用方式跟 test_llm.py 里一样
    #       记得加 extra_body={"enable_thinking": False}
    def ask(self, question, n_results=3):
        # 1. 让 store 去数据库里搜相关文章
        relevant_article = self.store.search(question,n_results)

        # 2. 把搜到的文章拼成"参考资料"文字
        context = self.build_context(relevant_article)

        # 3. 把参考资料 + 用户问题填入 prompt 模板
        prompt = RAG_PROMPT.format(context=context,question=question)
        
        # 4. 把 prompt 发给通义千问
        response = self.llm_client.chat.completions.create(
            model = MODEL_NAME,
            messages = [
                {"role":"user","content":prompt}
            ],
            extra_body={"enable_thinking":False},
        )

        # 5. 取出 AI 的回复并返回
        return response.choices[0].message.content


# ============================================
# 测试代码
# ============================================
if __name__ == "__main__":
    print("=" * 50)
    print("InfoHunter - RAG 问答测试")
    print("=" * 50)

    rag = RAGEngine()

    questions = [
        "AI Agent 是怎么调用外部工具的？",
        "RAG 系统中哪种分块策略效果最好？",
        "ChromaDB 和 Milvus 应该怎么选？",
    ]

    for q in questions:
        print(f"\n{'─' * 40}")
        print(f"问题: {q}")
        print(f"{'─' * 40}")
        answer = rag.ask(q)
        print(f"\n回答:\n{answer}")