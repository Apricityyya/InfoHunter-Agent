"""
LangGraph 多 Agent 共享 State 定义
"""
from typing import TypedDict


class AgentState(TypedDict):
    # ===== 用户输入 =====
    user_input: str               # 当前用户的提问
    
    # ===== 调度 Agent 输出 =====
    route: str                    # 路由决策: "info" / "eval" / "chat"
    confidence: float             # LLM 对路由的置信度0-1

    # ===== 澄清相关 ======
    clarify_question: str         # 给用户的反问内容
    is_clarifying: bool           # 当前是否处于澄清等待状态
    conversation_history: list    # 多轮对话历史
    
    # ===== 信息 Agent 用的字段 =====
    search_query: str             # 检索关键词（可能从 user_input 提炼）
    search_results: list          # RAG 检索结果（暂时用 list，后面优化）
    
    # ===== 评估 Agent 用的字段 =====
    resume_text: str              # 用户简历原文
    jd_text: str                  # 岗位 JD 原文
    match_score: float            # 匹配分数 0-100
    gap_report: str               # 差距分析报告
    
    # ===== 最终输出 =====
    final_answer: str             # 给用户的最终回答