"""
InfoHunter - Function Calling 版Agent
"""

import json
from openai import OpenAI
from config import DASHSCOPE_API_KEY,DASHSCOPE_BASE_URL,MODEL_NAME
from rag import RAGEngine

# 工具定义
TOOLS = [
    {
        "type":"function",
        "function":{
            "name":"search_articles",
            "description":"搜索文章库中的相关内容，当用户想查找信息或提问专业问题时使用",
            "parameters":{
                "type":"object",
                "properties":{
                    "query":{
                        "type":"string",
                        "description":"搜索关键词"
                    }
                },
                "required":["query"]
            }
        }
    },
    {
        "type":"function",
        "function":{
            "name":"count_articles",
            "description":"查看文章库中的文章总数，当用户询问数据量或统计信息时使用",
            "parameters":{
                "type":"object",
                "properties":{}
            }
        }
    },
]

class FCAgent:
    """Function Calling 版 Agent"""

    def __init__(self):
        self.llm_client = OpenAI(
            api_key=DASHSCOPE_API_KEY,
            base_url=DASHSCOPE_BASE_URL,
        )
        self.rag = RAGEngine()
        # 修改1: 加一个对话历史列表
        self.memory = []


    def run(self,user_input):
        """
        Agent 主流程

        步骤：
        1.把用户输入 + 工具定义一起发给LLM
        2.检查LLM返回的是tool calls还是普通文本
        3.如果是 tool calls -> 根据函数名调用对应方法
        4.如果是普通文本 -> 直接返回
        """

        print(f"\n[FCAgent] 正在分析意图...")

        # 修改2: 把用户输入追加到 memory，然后把整个 memory 传给 API
        self.memory.append({"role":"user","content":user_input})

        # 任务1: 调用 LLM API（带 tools 参数）
        # 提示: 跟 test_fc.py 里一样，加上 tools=TOOLS
        # 用 try/except 包裹
        # TODO

        try:
            response = self.llm_client.chat.completions.create(
                model = MODEL_NAME,
                messages=self.memory,
                tools=TOOLS,
                extra_body={"enable_thinking":False},
            )
        except Exception as e:
            print(f"API 调用失败：{e}")

        message = response.choices[0].message


        # 任务2: 判断是工具调用还是直接回复
        if message.tool_calls:
            tool_call = message.tool_calls[0]
            function_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            print(f"[FCAgent] 调用工具: {function_name}, 参数: {arguments}")

            # 任务3: 根据 function_name 执行对应操作
            # search_articles → 调用 self.rag.ask(arguments["query"])
            # count_articles → 返回文章数量
            # 其他情况 → 返回 "未知工具"
            # TODO
            if function_name=="search_articles":
                answer = self.rag.ask(arguments["query"])
            elif function_name=="count_articles":
                count = self.rag.store.get_count()
                answer = f"数据库中共有 {count} 篇文章"
            else:
                answer = "未知工具"
            
            self.memory.append({"role":"assistant","content":answer})

        else:
            # 直接回复（闲聊）
            print(f"[FCAgent] 直接回复")
            answer = message.content
            self.memory.append({"role":"assistant","content":answer})
        
        return answer


# ============================================
# 测试代码
# ============================================
if __name__ == "__main__":
    print("=" * 50)
    print("InfoHunter - Function Calling Agent 测试")
    print("=" * 50)

    agent = FCAgent()

    # test_inputs = [
    #     "你好，你是谁？",
    #     "帮我查一下关于 AI Agent 的信息",
    #     "数据库里现在有多少篇文章？",
    #     "RAG 系统的分块策略有哪些？",
    # ]
    test_inputs = [
        "帮我搜索关于 RAG 的信息",
        "它的分块策略有哪些？",          # "它"指 RAG，需要记忆
        "刚才你说的那些策略，哪种最好？",  # 依赖前两轮的上下文
        "数据库里有多少篇文章？",
    ]

    for user_input in test_inputs:
        print(f"\n{'=' * 40}")
        print(f"用户: {user_input}")
        print(f"{'=' * 40}")
        answer = agent.run(user_input)
        print(f"\nFCAgent: {answer}")