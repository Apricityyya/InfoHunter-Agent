"""
LangGraph 入门 Demo
流程: 输入文字 → 打招呼 Node → 加感叹号 Node → 输出
"""
from typing import TypedDict
from langgraph.graph import StateGraph, START, END


# ============ Step 1: 定义 State（共享单据） ============
class State(TypedDict):  #带类型约束的字典TypeDict，告诉python“这个字典必须有一个叫text的字段，类型是str”
    text: str   # 流转的文字内容


# ============ Step 2: 定义 Node（每个角色做的事） ============
def greeting_node(state: State):
    """打招呼 Node：在文字前加 'Hello, '"""
    print(f"[greeting_node] 收到 state: {state}")
    new_text = "Hello, " + state["text"]
    print(f"[greeting_node] 处理后: {new_text}")
    return {"text": new_text}    # 返回要更新的字段。！注意只return包含要更新字段的字典，不是完整State
    #LangGraph自动把这个返回值“合并”到全局State里


def exclaim_node(state: State):
    """加感叹号 Node"""
    print(f"[exclaim_node] 收到 state: {state}")
    new_text = state["text"] + "!"
    print(f"[exclaim_node] 处理后: {new_text}")
    return {"text": new_text}


# ============ Step 3: 组装 Graph（画流程图） ============
graph_builder = StateGraph(State)

# 添加 Node
graph_builder.add_node("greeting", greeting_node)
graph_builder.add_node("exclaim", exclaim_node)

# 添加 Edge（流转路径）
graph_builder.add_edge(START, "greeting")       # 入口 → greeting
graph_builder.add_edge("greeting", "exclaim")   # greeting → exclaim
graph_builder.add_edge("exclaim", END)          # exclaim → 出口

# 编译图
graph = graph_builder.compile()


# ============ Step 4: 运行 ============
if __name__ == "__main__":
    print("=" * 50)
    print("LangGraph Demo")
    print("=" * 50)

    initial_state = {"text": "friend"}
    final_state = graph.invoke(initial_state) #注意用的invoke执行

    print("\n" + "=" * 50)
    print(f"最终结果: {final_state}")
    print("=" * 50)