"""
端到端评估合理性测试
测试 Eval Agent 给出的综合评分是否落在预期区间
"""
import json
import sys
sys.path.insert(0, '..')

from agent_eval import parse_resume, parse_jd, compute_match_score


def load_test_cases(filepath: str) -> list:
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)["test_cases"]


def evaluate_single_case(case: dict) -> dict:
    """跑单个 case，返回是否落在预期区间"""
    print(f"\n{'='*60}")
    print(f"测试: {case['id']} - {case['description']}")
    print(f"期望评分区间: {case['expected_range']}")
    print('='*60)
    
    # 跑 3 步流程（不需要 generate_gap_report，省时间）
    resume_info = parse_resume(case["resume"])
    jd_info = parse_jd(case["jd"])
    score_info = compute_match_score(resume_info, jd_info)
    
    actual_score = score_info.get("overall_score", -1)
    expected_min, expected_max = case["expected_range"]
    in_range = expected_min <= actual_score <= expected_max
    
    print(f"  实际评分: {actual_score}")
    print(f"  {'✅ 落在预期区间' if in_range else '❌ 超出预期区间'}")
    
    return {
        "id": case["id"],
        "description": case["description"],
        "expected_range": case["expected_range"],
        "actual_score": actual_score,
        "in_range": in_range,
    }


def evaluate(test_cases: list) -> dict:
    results = []
    correct = 0
    
    for case in test_cases:
        result = evaluate_single_case(case)
        results.append(result)
        if result["in_range"]:
            correct += 1
    
    return {
        "total": len(test_cases),
        "correct": correct,
        "accuracy": correct / len(test_cases),
        "details": results,
    }


def print_report(result: dict):
    print("\n" + "=" * 60)
    print("📊 端到端评估合理性报告")
    print("=" * 60)
    
    print(f"\n总用例数: {result['total']}")
    print(f"评分合理: {result['correct']}")
    print(f"合理率: {result['accuracy']:.1%}")
    
    print("\n详细结果:")
    print(f"{'ID':<20} {'期望区间':<15} {'实际评分':<10} {'是否合理':<10}")
    print("-" * 60)
    for r in result["details"]:
        range_str = f"{r['expected_range'][0]}-{r['expected_range'][1]}"
        mark = "✅" if r["in_range"] else "❌"
        print(f"{r['id']:<20} {range_str:<15} {r['actual_score']:<10} {mark}")
    
    # 失败 case 提示
    failed = [r for r in result["details"] if not r["in_range"]]
    if failed:
        print("\n失败 case 分析:")
        for r in failed:
            expected = f"{r['expected_range'][0]}-{r['expected_range'][1]}"
            print(f"  - {r['id']}: 期望 {expected}, 实际 {r['actual_score']}")


if __name__ == "__main__":
    test_cases = load_test_cases("test_cases_e2e.json")
    result = evaluate(test_cases)
    print_report(result)
    
    with open("eval_result_e2e.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print("\n[结果已保存到 eval_result_e2e.json]")