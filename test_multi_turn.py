"""
多轮对话测试：模拟前端驱动 graph 的过程
"""
from agent_graph import build_graph,make_initial_state

def build_augmented_input(original_query:str,clarify_question:str,user_reply:str) -> str:
    """
    构造增强的 user_input
    把原始问题 + 反问 + 用户回复拼接起来给 Orchestrator
    """
    return f""" 【对话上下文】
用户最初的提问：{original_query}
助手的澄清反问：{clarify_question}
用户的回复：{user_reply}

请综合以上上下文判断用户的真实意图。"""



def conversation_demo(initial_query:str,user_reply:str):
    """
    模拟一次完整的两轮对话：
    1. 用户提出模糊问题 → 触发 clarify
    2. 用户回复反问 → 进入正确的子 Agent
    """

    graph = build_graph()

    # ========== 第 1 轮 ==========
    print("\n" + "🔵 " * 25)
    print(f"用户: {initial_query}")
    print("🔵 " * 25)

    state = make_initial_state(initial_query)
    result = graph.invoke(state)

    print(f"\n[第1轮结果] is_clarifying = {result['is_clarifying']}")
    print(f"助手: {result['final_answer']}")

    # 如果第一轮就直接给答案，对话结束
    if not result["is_clarifying"]:
        print("\n[结束] 第一轮已得到答案，无需多轮")
        return
    
    # ========== 第 2 轮 ==========
    clarify_question = result["clarify_question"]

    print("\n" + "🟢 " * 25)
    print(f"用户: {user_reply}")
    print("🟢 " * 25)
    
    # 关键: 构造带上下文的 augmented_input
    augmented_input = build_augmented_input(
        original_query=initial_query,
        clarify_question=clarify_question,
        user_reply=user_reply,
    )
    print(f"\n[Augmented Input]:\n{augmented_input}\n")

    state2 = make_initial_state(augmented_input)
    result2 = graph.invoke(state2)

    print(f"\n[第2轮结果] is_clarifying = {result2['is_clarifying']}")
    print(f"助手: {result2['final_answer'][:300]}")






if __name__ == "__main__":
    # 测试场景 1: 模糊问题 → 用户澄清想评估简历
    print("=" * 60)
    print("场景 1: 用户澄清后想评估简历")
    print("=" * 60)
    conversation_demo(
        initial_query="帮我看看我现在的水平",
        user_reply="我想评估一下简历",
    )
    
    # 测试场景 2: 模糊问题 → 用户澄清想看资讯
    print("\n\n" + "=" * 60)
    print("场景 2: 用户澄清后想看资讯")
    print("=" * 60)
    conversation_demo(
        initial_query="帮我看看我现在的水平",
        user_reply="想了解一下行业最新动态",
    )
    
    # 测试场景 3: 用户首问就很明确，不应触发 clarify
    print("\n\n" + "=" * 60)
    print("场景 3: 明确问题，单轮即可")
    print("=" * 60)
    conversation_demo(
        initial_query="最近 AI Agent 有什么新进展",
        user_reply="（这一轮不应该触发，因为第一轮已经给答案了）",
    )