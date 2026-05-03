"""
调度 Agent (Orchestrator)
职责: 理解用户意图，决定路由到哪个子Agent
"""
import json
from llm_utils import call_llm,call_llm_json
from agents_state import AgentState


# ============ 路由 Prompt ============
ORCHESTRATOR_PROMPT = """你是一个求职助手的意图识别模块。根据用户的输入，判断该路由到哪个子 Agent。

可用路由：
- info: 用户想了解资讯、新闻、行业动态、检索文章库的内容
- eval: 用户想评估简历、判断岗位匹配度、获取简历改进建议。
        特别注意：当用户明确涉及【工作/岗位/职业能力】的自我评估时（如"我能不能做X工作"、"我适不适合X岗位"），路由到 eval。
- chat: 用户在闲聊、打招呼、或与求职无关的问题，包括泛泛的自我探索。

【置信度评估】
- 0.9-1.0: 用户意图非常明确，关键词清晰
- 0.7-0.9: 意图基本明确，有少量歧义
- 0.5-0.7: 意图模糊，可能有 2 种解读
- 0.0-0.5: 意图非常不明确，几乎无法判断

请只返回JSON格式，不要返回其他内容：
{{"route": "上述三个之一", "search_query": "如果路由是info，从用户输入提炼出的检索关键词；其他情况留空","confidence":0.0-1.0之间的浮点数}}

用户输入 : {user_input}"""



# ============ Nodes ============
def orchestrator_node(state: AgentState):
    """
    调度 Agent Node
    
    输入: state['user_input']
    输出: 更新 state['route'] 和 state['search_query']
    """
    user_input = state["user_input"]
    print(f"\n[Orchestrator] 分析用户意图: {user_input}")
  
    prompt = ORCHESTRATOR_PROMPT.format(user_input=user_input)

    result = call_llm_json(
        prompt,
        default = {"route":"chat","search_query":"","confidence":0.5}
        )
    print(f"[Orchestrator] 决策: route={result['route']}, search_query='{result['search_query']}', confidence={result.get('confidence',0):.2f}")
    return result
  


def route_decision(state: AgentState):
    """LangGraph 条件路由函数  """
    return state["route"]

# ============ 单元测试 ============
if __name__ == "__main__":
    test_cases = [
        "最近 AI 圈有什么动静",                     # 应走 info
        "帮我看看我适不适合腾讯的算法岗",             # 应走 eval
        "你好啊",                                   # 应走 chat
        "字节有没有 AI Agent 实习",                 # 应走 info
        "我的简历能拿到大厂面试吗",                  # 应走 eval
    ]
    
    for user_input in test_cases:
        print("\n" + "=" * 50)
        print(f"测试: {user_input}")
        print("=" * 50)
        
        # 手动构造 state
        state = {
            "user_input": user_input,
            "route": "",
            "search_query": "",
            "search_results": [],
            "resume_text": "",
            "jd_text": "",
            "match_score": 0.0,
            "gap_report": "",
            "final_answer": "",
        }
        
        result = orchestrator_node(state)
        print(f"返回: {result}")