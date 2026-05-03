"""
工具调用成功率评测
测试 Eval Agent 内部 4 个工具的稳定性和 schema 合规性
"""
import json
import sys
sys.path.insert(0, '..')

from agent_eval import parse_resume, parse_jd, compute_match_score, generate_gap_report


def load_test_cases(filepath: str) -> list:
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)["test_cases"]


# ============ Schema 校验函数 ============

def validate_resume_info(info: dict) -> tuple[bool, str]:
    """校验 parse_resume 返回值"""
    required_fields = ["skills", "experiences", "education", "highlights"]
    for field in required_fields:
        if field not in info:
            return False, f"缺少字段 '{field}'"
    if not isinstance(info["skills"], list):
        return False, "skills 不是列表"
    if not isinstance(info["experiences"], list):
        return False, "experiences 不是列表"
    return True, "OK"


def validate_jd_info(info: dict) -> tuple[bool, str]:
    """校验 parse_jd 返回值"""
    required_fields = ["required_skills", "preferred_skills", "responsibilities", "experience_level"]
    for field in required_fields:
        if field not in info:
            return False, f"缺少字段 '{field}'"
    if not isinstance(info["required_skills"], list):
        return False, "required_skills 不是列表"
    return True, "OK"


def validate_score_info(info: dict) -> tuple[bool, str]:
    """校验 compute_match_score 返回值"""
    required_fields = ["skill_match", "experience_match", "education_match", "overall_score", "matched_points", "missing_points"]
    for field in required_fields:
        if field not in info:
            return False, f"缺少字段 '{field}'"
    
    # 检查 4 个评分是不是 0-100 的数字
    for score_field in ["skill_match", "experience_match", "education_match", "overall_score"]:
        score = info[score_field]
        if not isinstance(score, (int, float)):
            return False, f"{score_field} 不是数字"
        if not 0 <= score <= 100:
            return False, f"{score_field}={score} 超出 0-100 范围"
    
    return True, "OK"


def validate_report(report: str) -> tuple[bool, str]:
    """校验 generate_gap_report 返回值"""
    if not isinstance(report, str):
        return False, "返回值不是字符串"
    if len(report) < 100:
        return False, f"报告太短（{len(report)} 字）"
    return True, "OK"


# ============ 单 case 评测 ============

def evaluate_single_case(case: dict) -> dict:
    """跑单个测试用例的 4 步流程，记录每一步的成败"""
    print(f"\n{'='*60}")
    print(f"测试: {case['id']} - {case['description']}")
    print('='*60)
    
    results = {
        "id": case["id"],
        "parse_resume": {"success": False, "msg": ""},
        "parse_jd": {"success": False, "msg": ""},
        "compute_match_score": {"success": False, "msg": ""},
        "generate_gap_report": {"success": False, "msg": ""},
    }
    
    # Step 1: parse_resume
    print("[Step 1] parse_resume...")
    resume_info = parse_resume(case["resume"])
    valid, msg = validate_resume_info(resume_info)
    results["parse_resume"] = {"success": valid, "msg": msg}
    print(f"  {'✅' if valid else '❌'} {msg}")
    
    # Step 2: parse_jd
    print("[Step 2] parse_jd...")
    jd_info = parse_jd(case["jd"])
    valid, msg = validate_jd_info(jd_info)
    results["parse_jd"] = {"success": valid, "msg": msg}
    print(f"  {'✅' if valid else '❌'} {msg}")
    
    # Step 3: compute_match_score（依赖前两步成功）
    print("[Step 3] compute_match_score...")
    score_info = compute_match_score(resume_info, jd_info)
    valid, msg = validate_score_info(score_info)
    results["compute_match_score"] = {"success": valid, "msg": msg}
    print(f"  {'✅' if valid else '❌'} {msg}")
    if valid:
        print(f"     综合评分: {score_info['overall_score']}")
    
    # Step 4: generate_gap_report
    print("[Step 4] generate_gap_report...")
    report = generate_gap_report(resume_info, jd_info, score_info)
    valid, msg = validate_report(report)
    results["generate_gap_report"] = {"success": valid, "msg": msg}
    print(f"  {'✅' if valid else '❌'} {msg}")
    if valid:
        print(f"     报告长度: {len(report)} 字")
    
    return results


# ============ 完整评测 ============

def evaluate(test_cases: list) -> dict:
    """跑全部用例，统计每个工具的成功率"""
    all_results = []
    
    # 4 个工具的成功计数
    tool_stats = {
        "parse_resume": {"success": 0, "total": 0},
        "parse_jd": {"success": 0, "total": 0},
        "compute_match_score": {"success": 0, "total": 0},
        "generate_gap_report": {"success": 0, "total": 0},
    }
    
    for case in test_cases:
        result = evaluate_single_case(case)
        all_results.append(result)
        
        for tool in tool_stats:
            tool_stats[tool]["total"] += 1
            if result[tool]["success"]:
                tool_stats[tool]["success"] += 1
    
    return {
        "tool_stats": tool_stats,
        "details": all_results,
    }


def print_report(result: dict):
    print("\n" + "=" * 60)
    print("📊 工具调用成功率评测报告")
    print("=" * 60)
    
    print(f"\n{'工具名':<25} {'成功率':>10} {'成功/总数':>12}")
    print("-" * 50)
    for tool, stats in result["tool_stats"].items():
        rate = stats["success"] / stats["total"] if stats["total"] > 0 else 0
        print(f"{tool:<25} {rate:>9.1%} {stats['success']:>5}/{stats['total']:<5}")
    
    # 失败明细
    print("\n失败明细:")
    has_failure = False
    for case_result in result["details"]:
        for tool in ["parse_resume", "parse_jd", "compute_match_score", "generate_gap_report"]:
            if not case_result[tool]["success"]:
                has_failure = True
                print(f"  - {case_result['id']} / {tool}: {case_result[tool]['msg']}")
    if not has_failure:
        print("  (无)")


if __name__ == "__main__":
    test_cases = load_test_cases("test_cases_tools.json")
    result = evaluate(test_cases)
    print_report(result)
    
    with open("eval_result_tools.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print("\n[结果已保存到 eval_result_tools.json]")