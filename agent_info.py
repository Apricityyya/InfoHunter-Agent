"""
信息 Agent
职责：根据 search_query 调用 RAG，返回带来源引用的回答
"""
from rag import RAGEngine
from agents_state import AgentState


# 模块级实例化
rag = RAGEngine()


def info_agent_node(state: AgentState):
    """
    信息 Agent Node
    
    输入: state['search_query']  (调度 Agent 提炼的检索词)
    输出: 更新 state['search_results'] 和 state['final_answer']
    """
    query = state["search_query"] or state["user_input"]   # 兜底：search_query 为空就用原始输入
    print(f"\n[InfoAgent] 检索: {query}")
    
    # 1. 调用 rag.ask(query) 获取带来源的回答
    answer = rag.ask(query)
    # 2. 调用 rag.store.search(query) 获取原始检索结果
    results = rag.store.search(query)
    # 3. 把结果填入 state，返回更新字典
    return {
        "search_results":results["documents"][0],
        "final_answer":answer,
    }





# ============ 单元测试 ============
if __name__ == "__main__":
    test_state = {
        "user_input": "最近有什么 AI Agent 相关的内容",
        "route": "info",
        "search_query": "AI Agent 开发",
        "search_results": [],
        "resume_text": "",
        "jd_text": "",
        "match_score": 0.0,
        "gap_report": "",
        "final_answer": "",
    }
    
    result = info_agent_node(test_state)
    print(f"\n返回字段: {list(result.keys())}")
    print(f"\nfinal_answer:\n{result.get('final_answer', '')[:800]}")