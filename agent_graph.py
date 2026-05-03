"""
LangGraph 主图：组装所有 Agent
"""
from langgraph.graph import StateGraph,START,END
from agents_state import AgentState
from agent_orchestrator import orchestrator_node
from agent_info import info_agent_node
from agent_eval import eval_agent_node
from llm_utils import call_llm

# ============ Chat Node（处理闲聊） ============
def chat_node(state:AgentState):
    """简单闲聊兜底Node"""
    print(f"\n[ChatNode] 处理闲聊")
    return {
        "final_answer":"你好！我是你的求职助手。我可以帮你：\n"
                       "1. 检索最新的行业资讯（直接问我'最近有什么 AI 新闻'）\n"
                       "2. 评估简历与岗位的匹配度（提供你的简历和 JD）"
    }

# ============ Clarify Node（当意图不明时反问） ============
CLARIFY_PROMPT = """你是一个友好的求职助手。用户刚才说了一句意图不太明确的话，你需要用一个简短、友好的反问澄清用户真正想要什么。

可用的功能(你能帮用户做什么)：
1.检索行业资讯、AI新闻、技术动态
2.评估用户简历与岗位的匹配度，给出改进建议
3.闲聊或回答与求职无关的问题

要求：
- 反问内容控制在 50 字以内
- 用第二人称("你")
- 给出 2-3 个具体选项让用户选择

用户的原话: {user_input}

请直接输出反问内容，不要加任何前缀或解释。"""

def clarify_node(state:AgentState):
    """澄清节点：当 Orchestrator 置信度低时，生成反问"""
    user_input = state["user_input"]
    print(f"\n[Clarify] 置信度过低 ({state['confidence']:.2f}), 生成反问")
    prompt = CLARIFY_PROMPT.format(user_input=user_input)
    try:
        question = call_llm(prompt)
    except Exception as e:
        #兜底反问
        question = "抱歉我不太理解你的意思。你是想：(1) 了解最新资讯 (2) 评估简历 还是(3)闲聊？"
    print(f"[Clarify] 反问：{question}")

    return {
        "clarify_question":question,
        "is_clarifying":True,
        "final_answer":question,
    }
    

# ============ 条件路由函数 ============
# 置信度阈值
CONFIDENCE_THRESHOLD = 0.7

def route_decision(state:AgentState):
    """
    从 state['route'] 读取调度决策
    逻辑：
    - 置信度 >= 阈值: 按 route 路由
    - 置信度 < 阈值: 走 clarify
    """
    confidence = state["confidence"]
    if confidence < CONFIDENCE_THRESHOLD:
        print(f"[Router] 置信度 {confidence:.2f} < {CONFIDENCE_THRESHOLD}, 走 clarify" )
        return "clarify"
    print(f"[Router] 置信度 {confidence:.2f} >= {CONFIDENCE_THRESHOLD}, 走 {state['route']}")
    return state["route"]


# ============ 组装 Graph ============
def build_graph():
    """构建 LangGraph 求职助手主图"""
    builder = StateGraph(AgentState)

    # 注册所有 Node
    builder.add_node("orchestrator",orchestrator_node)
    builder.add_node("info",info_agent_node)
    builder.add_node("eval",eval_agent_node)
    builder.add_node("chat",chat_node)
    builder.add_node("clarify",clarify_node)

    # 入口 -> orchestrator
    builder.add_edge(START,"orchestrator")

    # orchestrator 分叉路由
    builder.add_conditional_edges(
        "orchestrator",
        route_decision,{
            "info":"info",
            "eval":"eval",
            "chat":"chat",
            "clarify":"clarify",
        }
    )

    # 三个Agent 都通向 END
    builder.add_edge("info",END)
    builder.add_edge("eval",END)
    builder.add_edge("chat",END)
    builder.add_edge("clarify",END)

    return builder.compile()


# ============ 提供给外部使用的工厂函数 ============
def make_initial_state(user_input:str , resume_text:str="" , jd_text:str=""):
    """创建初始 State"""
    return {
        "user_input":user_input,
        "route":"",
        "confidence": 0.0,                  
        "clarify_question": "",             
        "is_clarifying": False,             
        "conversation_history": [],         
        "search_query":"",
        "search_results":[],
        "resume_text":resume_text,
        "jd_text":jd_text,
        "match_score":0.0,
        "gap_report":"",
        "final_answer":"",
        }

if __name__ == "__main__":
    graph = build_graph()
    
    # 测试 1: 正常场景（高置信度）
    print("=" * 60)
    print("测试 1: 高置信度 - 闲聊")
    print("=" * 60)
    state = make_initial_state("你好")
    result = graph.invoke(state)
    print(f"\n回答:\n{result['final_answer']}")
    
    # 测试 2: 模糊场景（应该触发 clarify）
    print("\n" + "=" * 60)
    print("测试 2: 模糊意图 - 应触发 Clarify")
    print("=" * 60)
    state = make_initial_state("我能做你这种工作吗")
    result = graph.invoke(state)
    print(f"\nis_clarifying: {result['is_clarifying']}")
    print(f"反问内容:\n{result['final_answer']}")
    
    # 测试 3: 模糊场景 2
    print("\n" + "=" * 60)
    print("测试 3: 模糊意图 - 应触发 Clarify")
    print("=" * 60)
    state = make_initial_state("帮我看看我现在的水平")
    result = graph.invoke(state)
    print(f"\nis_clarifying: {result['is_clarifying']}")
    print(f"反问内容:\n{result['final_answer']}")
    
    # 测试 4: 信息检索（高置信度）
    print("\n" + "=" * 60)
    print("测试 4: 高置信度 - 信息检索")
    print("=" * 60)
    state = make_initial_state("最近有什么 AI Agent 相关内容")
    result = graph.invoke(state)
    print(f"\n回答:\n{result['final_answer'][:300]}")