"""
简历评估 MCP Server
暴露 4 个工具：parse_resume / parse_jd / compute_match_score / generate_gap_report
"""
import json
import sys
from mcp.server.fastmcp import FastMCP
from llm_utils import call_llm,call_llm_json

mcp = FastMCP("resume-eval-server")

# ============ 工具 1: parse_resume ============

PARSE_RESUME_PROMPT = """你是一个简历解析助手。请从以下简历文本中提取关键信息，返回 JSON 格式。

提取要求：
- skills: 候选人掌握的技术栈和工具列表
- experiences: 工作/实习/项目经历的简要描述列表
- education: 教育背景（学校 + 专业 + 学历）
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


@mcp.tool()
def parse_resume(resume_text:str) -> dict:
    """
    从简历文本中提取结构化信息
    
    参数:
        resume_text: 简历的纯文本内容
    
    返回:
        包含 skills, experiences, education, highlights 的字典
    """
    print(f" [MCP] parser_resume 调用",file=sys.stderr)
    prompt = PARSE_RESUME_PROMPT.format(resume_text=resume_text)
    return call_llm_json(
        prompt,
        default = {"skills": [], "experiences": [], "education": "", "highlights": []}
    )


# ============ 工具 2: parse_jd ============

PARSE_JD_PROMPT = """你是一个岗位 JD 解析助手。请从以下岗位描述中提取关键信息，返回 JSON 格式。

提取要求：
- required_skills: 岗位明确要求的硬技能（编程语言、框架、工具等）
- preferred_skills: 加分项的软技能或附加要求
- responsibilities: 主要工作职责的简要列表
- experience_level: 经验要求（如"实习生"、"1-3年"、"3年以上"）

请只返回JSON格式，不要返回其他内容：
{{
    "required_skills": ["技能1", "技能2", ...],
    "preferred_skills": ["技能1", "技能2", ...],
    "responsibilities": ["职责1", "职责2", ...],
    "experience_level": "经验要求"
}}

JD 文本：
{jd_text}"""


@mcp.tool()
def parse_jd(jd_text: str) -> dict:
    """
    从岗位 JD 文本中提取结构化信息
    
    参数:
        jd_text: 岗位描述的纯文本内容
    
    返回:
        包含 required_skills, preferred_skills, responsibilities, experience_level 的字典
    """
    print(f"[MCP] parse_jd 调用", file=sys.stderr)
    prompt = PARSE_JD_PROMPT.format(jd_text=jd_text)
    return call_llm_json(
        prompt,
        default={"required_skills": [], "preferred_skills": [], "responsibilities": [], "experience_level": []}
    )




# ============ 工具 3: compute_match_score ============

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

@mcp.tool()
def compute_match_score(resume_info: dict, jd_info: dict) -> dict:
    """
    计算简历与岗位的匹配度评分
    
    参数:
        resume_info: parse_resume 返回的结构化简历信息
        jd_info: parse_jd 返回的结构化 JD 信息
    
    返回:
        包含各维度评分和匹配/欠缺要点的字典
    """
    print(f"[MCP] compute_match_score 调用", file=sys.stderr)
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



# ============ 工具 4: generate_gap_report ============

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


@mcp.tool()
def generate_gap_report(resume_info: dict, jd_info: dict, score_info: dict) -> str:
    """
    生成自然语言的简历改进建议报告
    
    参数:
        resume_info: 结构化简历信息
        jd_info: 结构化 JD 信息
        score_info: compute_match_score 返回的评分结果
    
    返回:
        自然语言的改进建议报告（字符串）
    """
    print(f"[MCP] generate_gap_report 调用", file=sys.stderr)
    prompt = GAP_REPORT_PROMPT.format(
        resume_info=json.dumps(resume_info,ensure_ascii=False),
        jd_info=json.dumps(jd_info,ensure_ascii=False),
        score_info=json.dumps(score_info,ensure_ascii=False),
    )
        
    try:
        return call_llm(prompt)
    except Exception as e:
        return f"报告生成失败: {e}" 
    




if __name__ == "__main__":
    mcp.run(transport="stdio")