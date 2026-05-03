"""
LangGraph Demo 2: 带条件路由
流程: 输入消息 → 路由 Node → 根据内容决定走 A 还是 B → END
"""

from typing import TypedDict
from langgraph.graph import StateGraph,START,END


#====================== State ==================
class State(TypedDict):
    user_input:str    # 用户输入
    route:str         # 路由决策("news" 或 "eval")
    answer:str        # 最终答案




# ============ Nodes ============
def router_node(state:State):
    """路由 Node：根据用户输入决定走哪条路"""
    user_input = state["user_input"]
    print(f"\n[router] 收到: {user_input}")

    # 简单关键词判断（真实项目里会用 LLM）
    if "新闻" in user_input or "资讯" in user_input:
        route = "news"
    elif "简历" in user_input or "评估" in user_input:
        route = "eval"
    elif "投诉" in user_input or "举报" in user_input:
        route = "report"
    else:
        route = "unknown"
    
    print(f"[router] 决策: {route}")
    return {"route":route}

def news_node(state:State):
    """新闻 Node"""
    print(f"[news_node] 处理新闻请求")
    return {"answer":"这是最新的新闻内容..."}

def eval_node(state: State):
    """评估 Node"""
    print(f"[eval_node] 处理评估请求")
    return {"answer": "这是简历评估结果..."}

def report_node(state: State):
    """投诉 Node"""
    print(f"[report_node] 处理投诉请求")
    return {"answer": "这是投诉处理结果..."}

def fallback_node(state:State):
    """兜底 Node"""
    print(f"[fallback_node] 不认识的请求")
    return {"answer": "抱歉，我不太理解你的意思"}

# ============ 条件路由函数 ============
def route_decision(state:State):
    """读取 state['route'], 返回下一个要走的 Node 名字"""
    return state["route"]


# ============ 组装 Graph ============
graph_builder = StateGraph(State)

# 添加 Node
graph_builder.add_node("router",router_node)
graph_builder.add_node("news",news_node)
graph_builder.add_node("eval",eval_node)
graph_builder.add_node("report",report_node)
graph_builder.add_node("fallback",fallback_node)

# 入口 -> router
graph_builder.add_edge(START,"router")

# 关键：router 之后是条件分叉
graph_builder.add_conditional_edges(
    "router",                                   # 从 router 节点出发
    route_decision,                             # 用这个函数决定走哪条
    {
        "news":"news",                          # 如果返回 "news"，走 news 节点
        "eval":"eval",                          # 如果返回 "eval"，走 eval 节点
        "report":"report",
        "unknown":"fallback",                   # 如果返回 "unknown"，走 fallback 节点
    }
)

# 三个 Node 都通向 END
graph_builder.add_edge("news",END)
graph_builder.add_edge("eval",END)
graph_builder.add_edge("report",END)
graph_builder.add_edge("fallback",END)

graph = graph_builder.compile()


# ============ 测试 ============
if __name__ == "__main__":
    test_inputs = [
        "今天有什么新闻？",
        "帮我评估一下我的简历",
        "我要投诉这个公司",
        "你好啊",
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
        
        print(f"\n最终回答: {result['answer']}")