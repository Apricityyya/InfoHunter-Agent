"""
测试通义千问 Function Calling
"""
import json
from openai import OpenAI
from config import DASHSCOPE_API_KEY, DASHSCOPE_BASE_URL, MODEL_NAME

client = OpenAI(
    api_key=DASHSCOPE_API_KEY,
    base_url=DASHSCOPE_BASE_URL,
)

# 定义工具（函数的"说明书"）
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_articles",
            "description": "搜索文章库中的相关内容，当用户想查找信息或提问专业问题时使用",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索关键词"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "count_articles",
            "description": "查看文章库中的文章总数，当用户询问数据量或统计信息时使用",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
]

# 测试不同的用户输入
test_inputs = [
    "帮我查一下关于 AI Agent 的信息",
    "数据库里有多少篇文章？",
    "你好，你是谁？",
]

for user_input in test_inputs:
    print(f"\n用户: {user_input}")
    
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": user_input}],
        tools=tools,
        extra_body={"enable_thinking": False},
    )

    message = response.choices[0].message

    if message.tool_calls:
        # LLM 决定调用工具
        tool_call = message.tool_calls[0]
        print(f"  → 调用工具: {tool_call.function.name}")
        print(f"  → 参数: {tool_call.function.arguments}")
    else:
        # LLM 决定直接回复
        print(f"  → 直接回复: {message.content[:100]}")