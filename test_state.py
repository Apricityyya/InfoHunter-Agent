"""测试 State 定义"""
from agents_state import AgentState


def make_initial_state(user_input: str) -> AgentState:
    """创建初始 State，所有字段给默认值"""
    return {
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


if __name__ == "__main__":
    # 测试1: 创建初始 State
    state = make_initial_state("最近有什么 AI 新闻？")
    print("初始 State:")
    for key, value in state.items():
        print(f"  {key}: {value!r}")
    
    # 测试2: 模拟 Node 更新 State
    print("\n模拟 router_node 更新后:")
    state["route"] = "info"
    print(f"  route: {state['route']}")
    
    print("\n模拟 info_node 更新后:")
    state["search_results"] = ["文章1", "文章2"]
    state["final_answer"] = "找到 2 篇相关文章"
    print(f"  search_results: {state['search_results']}")
    print(f"  final_answer: {state['final_answer']}")