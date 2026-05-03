"""
评估 Agent
职责：分析简历和 JD 的匹配度，给出改进建议

内部流程（多步）：
  1. parse_resume / parse_jd → 结构化提取
  2. compute_match_score → 打分 + 维度拆解
  3. generate_gap_report → 自然语言改进建议
"""
import json
from llm_utils import call_llm, call_llm_json
from agents_state import AgentState





# ============ Step 1: 解析简历 ============

PARSE_RESUME_PROMPT = """你是一个简历解析助手。请从以下简历文本中提取关键信息，返回 JSON 格式。

提取要求：
- skills: 候选人掌握的技术栈和工具列表
- experiences: 工作/实习/项目经历的简要描述列表
- education: 教育背景（学校 + 专业 + 学历），特别注意学历层次和院校水平
- highlights: 候选人的亮点（如奖项、特殊经历、量化成果）

请只返回JSON格式，不要返回其他内容：
{{
    "skills": ["技能1", "技能2", ...],
    "experiences": ["经历1的简要描述", "经历2的简要描述", ...],
    "education": "学校 + 专业 + 学历",
    "highlights": ["亮点1", "亮点2", ...]
}}

简历文本：
{resume_text}"""


def parse_resume(resume_text: str) -> dict:
    """从简历文本提取结构化信息"""
    prompt = PARSE_RESUME_PROMPT.format(resume_text=resume_text)
    return call_llm_json(
        prompt,
        default={"skills":[],"experiences":[],"education":"","highlights":[]}
    )


# ============ Step 2: 解析 JD ============

PARSE_JD_PROMPT = """你是一个岗位 JD 解析助手。请从以下岗位描述中提取关键信息，返回 JSON 格式。

提取要求：
- required_skills: 岗位明确要求的硬技能（编程语言、框架、工具等）
- preferred_skills: 加分项的软技能或附加要求
- responsibilities: 主要工作职责的简要列表，如有具体工作任务请一起罗列
- experience_level: 经验要求（如"实习生"、“大学生”、"1-3年"、"3年以上"）

请只返回JSON格式，不要返回其他内容：
{{
    "required_skills": ["技能1", "技能2", ...],
    "preferred_skills": ["技能1", "技能2", ...],
    "responsibilities": ["职责1", "职责2", ...],
    "experience_level": "经验要求"
}}

JD 文本：
{jd_text}"""


def parse_jd(jd_text: str) -> dict:
    """从 JD 文本提取结构化信息"""
    prompt = PARSE_JD_PROMPT.format(jd_text=jd_text)
    return call_llm_json(
        prompt,
        default={"required_skills": [], "preferred_skills": [], "responsibilities": [], "experience_level": []}
    )
        

# ============ Step 3: 计算匹配分数 ============

MATCH_SCORE_PROMPT = """你是一个简历-岗位匹配度评估专家。基于结构化的简历信息和 JD 信息，给出量化的匹配度评估。

评估维度：
1. 技能匹配度（候选人技能水平与岗位required_skills的匹配程度）
2. 经验相关性（候选人经历与岗位职责的相关程度）
3. 教育背景（学历院校层次及专业是否符合）
4. 综合评分（0-100整数，根据各维度综合得出）

请只返回JSON格式，不要返回其他内容：
{{
    "skill_match": 0-100整数,
    "experience_match": 0-100整数,
    "education_match": 0-100整数,
    "overall_score": 0-100整数,
    "matched_points": ["匹配亮点1", "匹配亮点2", ...],
    "missing_points": ["欠缺项1", "欠缺项2", ...]
}}

简历信息：
{resume_info}

JD 信息：
{jd_info}"""


def compute_match_score(resume_info: dict, jd_info: dict) -> dict:
    """基于结构化信息计算匹配度"""
    prompt = MATCH_SCORE_PROMPT.format(
        resume_info=json.dumps(resume_info, ensure_ascii=False),
        jd_info=json.dumps(jd_info, ensure_ascii=False),
    )
    return call_llm_json(
        prompt,
        default = {
            "skill_match": 0,
            "experience_match": 0,
            "education_match": 0,
            "overall_score": 0,
            "matched_points": [],
            "missing_points": [],
        }
    )
        


# ============ Step 4: 生成改进报告 ============

GAP_REPORT_PROMPT = """你是一个资深的求职导师。基于候选人简历、目标岗位、以及匹配度评估结果，生成一份个性化的改进建议报告。

报告要求：
1. 用第二人称（"你"）写作，口吻友好真诚
2. 先指出候选人的优势（基于 matched_points）
3. 然后指出与岗位的差距（基于 missing_points），分析为什么这些是关键
4. 给出 3-5 条具体的、可执行的改进建议（不要泛泛而谈）
5. 长度控制在 300-1000 字

简历信息：
{resume_info}

JD 信息：
{jd_info}

匹配评估：
{score_info}"""


def generate_gap_report(resume_info: dict, jd_info: dict, score_info: dict) -> str:
    """生成自然语言的改进建议报告"""

    prompt = GAP_REPORT_PROMPT.format(
        resume_info=json.dumps(resume_info,ensure_ascii=False),
        jd_info=json.dumps(jd_info,ensure_ascii=False),
        score_info=json.dumps(score_info,ensure_ascii=False),
    )
        
    try:
        return call_llm(prompt)
    except Exception as e:
        return f"报告生成失败: {e}" 



# ============ 把 4 步串成一个完整的 Node ============

def eval_agent_node(state: AgentState):
    """
    评估 Agent Node：完整的 4 步流程
    """
    resume_text = state["resume_text"]
    jd_text = state["jd_text"]
    
    if not resume_text or not jd_text:
        return {"final_answer": "请同时提供简历和岗位 JD"}
    
    print(f"\n[EvalAgent] 开始评估流程")
    
    print("[EvalAgent] Step 1/4: 解析简历...")
    resume_info = parse_resume(resume_text)
    
    print("[EvalAgent] Step 2/4: 解析 JD...")
    jd_info = parse_jd(jd_text)
    
    print("[EvalAgent] Step 3/4: 计算匹配度...")
    score_info = compute_match_score(resume_info, jd_info)
    
    print("[EvalAgent] Step 4/4: 生成改进报告...")
    report = generate_gap_report(resume_info, jd_info, score_info)
    
    # 拼接最终回答
    final_answer = f"""## 📊 简历-岗位匹配度评估

**综合评分：{score_info.get('overall_score', 0)}/100**
- 技能匹配：{score_info.get('skill_match', 0)}/100
- 经验匹配：{score_info.get('experience_match', 0)}/100
- 教育匹配：{score_info.get('education_match', 0)}/100

---

{report}
"""
    
    return {
        "match_score": float(score_info.get("overall_score", 0)),
        "gap_report": report,
        "final_answer": final_answer,
    }


# ============ 单元测试 ============
# if __name__ == "__main__":
#     # 测试简历
#     test_resume = """
#     王莹，同济大学计算机科学与技术专业本科在读。
#     技能：掌握 Python、了解 C++ 基础语法；熟悉 RAG、Agent、Function Calling 等大模型应用范式。
#     项目：
#     - InfoHunter：基于 RAG+Agent 的智能信息追踪系统，部署到阿里云 ECS。
#     - EcoAgent：复现 AAAI 2026 论文，云-端协同 Agent 框架。
#     经历：曾在火箭军服役两年，获优秀新兵和四有优秀士兵。
#     英语：CET 4/6。
#     """
    
#     # 测试 JD
#     test_jd = """
#     岗位：AI Agent 开发实习生
#     职责：
#     1. 参与 AI Agent 系统的设计与研发
#     2. 探索基于大模型的任务理解、工具调用与协同决策
#     3. 推动 Agent 在业务场景的落地
    
#     要求：
#     - 计算机相关专业本科及以上
#     - 熟悉 Python，有 LangChain / LangGraph 使用经验
#     - 了解 RAG、Function Calling、MCP 等技术
#     - 具有 Agent 项目经验者优先
#     """
    
#     print("=" * 50)
#     print("Step 1: 解析简历")
#     print("=" * 50)
#     resume_info = parse_resume(test_resume)
#     print(json.dumps(resume_info, ensure_ascii=False, indent=2))
    
#     print("\n" + "=" * 50)
#     print("Step 2: 解析 JD")
#     print("=" * 50)
#     jd_info = parse_jd(test_jd)
#     print(json.dumps(jd_info, ensure_ascii=False, indent=2))






# ============ 单元测试 ============
if __name__ == "__main__":
    test_resume = """
    王莹，同济大学计算机科学与技术专业本科在读。
    技能：掌握 Python、了解 C++ 基础语法；熟悉 RAG、Agent、Function Calling 等大模型应用范式。
    项目：
    - InfoHunter：基于 RAG+Agent 的智能信息追踪系统，部署到阿里云 ECS。
    - EcoAgent：复现 AAAI 2026 论文，云-端协同 Agent 框架。
    经历：曾在火箭军服役两年，获优秀新兵和四有优秀士兵。
    英语：CET 4/6。
    """
    
    test_jd = """
    岗位：AI Agent 开发实习生
    职责：
    1. 参与 AI Agent 系统的设计与研发
    2. 探索基于大模型的任务理解、工具调用与协同决策
    3. 推动 Agent 在业务场景的落地
    
    要求：
    - 计算机相关专业本科及以上
    - 熟悉 Python，有 LangChain / LangGraph 使用经验
    - 了解 RAG、Function Calling、MCP 等技术
    - 具有 Agent 项目经验者优先
    """
    
    # 用完整 Node 测试
    test_state = {
        "user_input": "评估我的简历",
        "route": "eval",
        "search_query": "",
        "search_results": [],
        "resume_text": test_resume,
        "jd_text": test_jd,
        "match_score": 0.0,
        "gap_report": "",
        "final_answer": "",
    }
    
    result = eval_agent_node(test_state)
    
    print("\n" + "=" * 50)
    print("最终评估结果")
    print("=" * 50)
    print(result["final_answer"])