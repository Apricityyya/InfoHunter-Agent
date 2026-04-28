"""
InfoHunter - 简易Agent
功能：根据用户意图，自动选择工具并回答
"""
import json
from openai import OpenAI
from config import DASHSCOPE_API_KEY,DASHSCOPE_BASE_URL,MODEL_NAME
from rag import RAGEngine

# 路由 prompt：让LLM判断用户意图
ROUTER_PROMPT = """你是一个意图识别助手。根据用户的输入，判断应该使用哪个工具。

可用工具：
1.search_articles - 搜索文章库中的相关内容(当用户想查找信息、提问专业问题时使用)
2.count_articles - 查看文章库中的文章总数(当用户询问数据量、统计信息时使用)
3.direct_chat - 直接对话(当用户打招呼、闲聊、问与文章无关的问题时使用)

请只返回JSON格式，不要返回其它内容：
{{"tool":"工具名称","query":"传给工具的参数(如果是搜索就填搜索词，其它工具填空字符串)"}}

用户输入: {user_input}"""


class Agent:
    def __init__(self):
        """初始化Agent"""
        self.llm_client = OpenAI(
            api_key=DASHSCOPE_API_KEY,
            base_url=DASHSCOPE_BASE_URL,
        )
        self.rag = RAGEngine()

    def route(self,user_input):
        """
        意图路由：让LLM判断该用哪个工具
        
        参数：user_input(用户输入的文字)
        返回：字典，如{"tool":"search_articles","query":"AI Agent"}
        """
        # 任务1: 
        # 1. 用 ROUTER_PROMPT.format(...) 填入 user_input
        # 2. 调用 LLM API（跟之前一样的方式）
        # 3. 解析返回的 JSON
        # 4. 返回解析后的字典
        #
        # 提示: LLM 有时会在 JSON 外面包 ```json```，需要清理
        #       你的 summarizer.py 里有清理代码可以参考
        prompt = ROUTER_PROMPT.format(user_input=user_input)
        response = self.llm_client.chat.completions.create(
            model = MODEL_NAME,
            messages = [
                {"role":"user","content":prompt}
            ],
            extra_body={"enable_thinking":False},
        )
        reply = response.choices[0].message.content.strip()

        if reply.startswith("```"):
            reply = reply.split("```")[1]
            if reply.startswith("json"):
                reply = reply[4:]
        reply = reply.strip()

        result = json.loads(reply)

        return {
            "tool":result.get("tool",""),
            "query":result.get("query",""),
        }
    

    def run(self,user_input):
        """
        Agent主流程：路由 → 执行工具 → 返回结果

        参数：user_input(用户输入)
        返回：最终回答字符串
        """

        print(f"\n[Agent] 正在分析意图...")

        # 第1步：路由
        # 任务2: 调用 self.route(user_input) 获取工具选择
        # 用 try/except 包裹，如果路由失败就默认用 direct_chat
        try:
            decision = self.route(user_input)  
        except Exception as e:
            print(f"路由失败，失败原因:{e}")
            decision = {"tool": "direct_chat", "query": user_input}  # 默认直接聊天
        
        tool = decision.get("tool", "direct_chat")
        query = decision.get("query", user_input)
        print(f"[Agent] 选择工具: {tool}")

        # 第2步：执行工具
        # 任务3: 根据 tool 的值，调用不同的方法
        if tool == "search_articles":
            # 调用 self.rag.ask(query) 获取 RAG 回答
            # TODO
            return self.rag.ask(query)
        elif tool == "count_articles":
            # 调用 self.rag.store.get_count() 获取文章数量
            # 拼一句话返回，如 "数据库中共有 X 篇文章"
            # TODO
            count = self.rag.store.get_count()
            result = f"数据库中共有 {count} 篇文章"
            return result
        else:
            # direct_chat: 直接调用 LLM 回答（不检索文章）
            # 调用 self.llm_client.chat.completions.create(...)
            # TODO
            response = self.llm_client.chat.completions.create(
                model = MODEL_NAME,
                messages = [
                    {"role":"user","content":user_input}
                ],
                extra_body={"enable_thinking":False},
            )
            return response.choices[0].message.content
        




# ============================================
# 测试代码
# ============================================
if __name__ == "__main__":
    print("=" * 50)
    print("InfoHunter - Agent 测试")
    print("=" * 50)

    agent = Agent()

    # 测试不同类型的输入
    test_inputs = [
        "你好，你是谁？",
        "帮我查一下关于 AI Agent 的信息",
        "数据库里现在有多少篇文章？",
        "RAG 系统的分块策略有哪些？",
    ]

    for user_input in test_inputs:
        print(f"\n{'=' * 40}")
        print(f"用户: {user_input}")
        print(f"{'=' * 40}")
        answer = agent.run(user_input)
        print(f"\nAgent: {answer}")