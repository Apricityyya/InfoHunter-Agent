"""
LangGraph Demo 3: 用 LLM 做意图识别
"""

import json
from typing import TypedDict
from langgraph.graph import StateGraph,START,END
from openai import OpenAI
from config import DASHSCOPE_API_KEY,DASHSCOPE_BASE_URL,MODEL_NAME

# ============ State ============
class State(TypedDict):
    user_input:str
    route:str
    answer:str

# ============ LLM 客户端 ============
client = OpenAI(
    api_key=DASHSCOPE_API_KEY,
    base_url=DASHSCOPE_BASE_URL,
)

# ============ 路由 Prompt ============
ROUTER_PROMPT = """你是一个意图识别助手。根据用户的输入，判断该走哪条路。

可用路由：
- news : 用户想了解新闻、资讯、行业动态
- eval: 用户想评估简历、判断岗位匹配度
- chat: 用户在闲聊、打招呼或询问其他无关问题

请只返回JSON格式，不要返回其它内容:
{{"route":"上述三个之一"}}

用户输入 : {user_input}"""



# ============ Nodes ============
def router_node(state: State):
    """用 LLM 做意图识别"""
    user_input = state["user_input"]
    print(f"\n[router] 收到: {user_input}")

    # TODO: 调用 LLM 判断意图
    # 1. 用 ROUTER_PROMPT.format(user_input=user_input) 填充模板
    # 2. 调用 client.chat.completions.create(...)
    # 3. 解析 JSON，提取 route 字段
    # 4. 用 try/except 包裹，失败时默认 route = "chat"
    prompt = ROUTER_PROMPT.format(user_input=user_input)

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role":"user","content":prompt}],
            extra_body={"enable_thinking":False}
        )
        reply = response.choices[0].message.content
        route = json.loads(reply)["route"]  #json.load(文件对象) 和 json.loads(字符串)要注意区分
    except Exception as e:
        print(f"[router] 路由失败: {e}, 默认走 chat")
        route = "chat"
    print(f"[router] 决策 : {route}")
    return {"route":route}


def news_node(state: State):
    print(f"[news_node] 处理新闻请求")
    return {"answer": "这是最新的新闻内容..."}


def eval_node(state: State):
    print(f"[eval_node] 处理评估请求")
    return {"answer": "这是简历评估结果..."}


def chat_node(state: State):
    print(f"[chat_node] 直接对话")
    return {"answer": "你好，我是求职助手"}


def route_decision(state: State):
    return state["route"]

# ============ 组装 Graph ============
graph_builder = StateGraph(State)

graph_builder.add_node("router",router_node)
graph_builder.add_node("news",news_node)
graph_builder.add_node("eval",eval_node)
graph_builder.add_node("chat",chat_node)

graph_builder.add_edge(START,"router")

graph_builder.add_conditional_edges(
    "router",
    route_decision,
    {
        "news":"news",
        "eval":"eval",
        "chat":"chat",
    }
)

graph_builder.add_edge("news",END)
graph_builder.add_edge("eval",END)
graph_builder.add_edge("chat",END)

graph = graph_builder.compile()


# ============ 测试 ============
if __name__ == "__main__":
    test_inputs = [
        "最近 AI 圈有啥动静",          # 应走 news（不含"新闻"二字，看 LLM 能不能识别）
        "我想知道我能不能进字节",       # 应走 eval
        "今晚吃啥",                    # 应走 chat
    ]
    
    for user_input in test_inputs:
        print("\n" + "=" * 50)
        print(f"用户: {user_input}")
        print("=" * 50)
        
        result = graph.invoke({
            "user_input": user_input,
            "route": "",
            "answer": "",
        })
        
        print(f"\n[路由结果] {result['route']}")
        print(f"[最终回答] {result['answer']}")