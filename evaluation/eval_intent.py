"""
意图识别评测脚本
"""
import json
import sys
sys.path.insert(0, '..')   # 让脚本能找到上级目录的模块

from agent_orchestrator import orchestrator_node

CONFIDENCE_THRESHOLD = 0.7

def load_test_cases(filepath: str) -> list:
    """加载测试用例"""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["test_cases"]


def run_single_test(query: str) -> str:
    """跑单个 query，返回路由决策"""
    state = {
        "user_input": query,
        "route": "",
        "search_query": "",
        "confidence": 0.0,
        "clarify_question": "",
        "is_clarifying": False,
        "conversation_history": [],
        "search_results": [],
        "resume_text": "",
        "jd_text": "",
        "match_score": 0.0,
        "gap_report": "",
        "final_answer": "",
    }
    result = orchestrator_node(state)
    
    route = result.get("route", "unknown")
    confidence = result.get("confidence", 0.5)
    will_clarify = confidence < CONFIDENCE_THRESHOLD
    
    return {
        "route": route,
        "confidence": confidence,
        "will_clarify": will_clarify,
    }


def evaluate(test_cases: list) -> dict:
    """跑完整评测，返回指标"""
    total = len(test_cases)
    correct = 0
    failed_cases = []  # 失败用例
    
    # 分类统计
    confusion = {"clarify_correct": 0, "clarify_missed": 0, "clarify_wrongly": 0, "route_wrong": 0}
    
    print(f"开始评测，共 {total} 个用例\n")
    
    for i, case in enumerate(test_cases, 1):
        query = case["query"]
        expected_route = case["expected_route"]
        expected_clarify = case.get("expected_clarify", False)
        
        result = run_single_test(query)
        actual_route = result["route"]
        actual_clarify = result["will_clarify"]
        confidence = result["confidence"]
        
        # 判断对错
        is_correct = False
        
        if expected_clarify:
            # 期望触发 clarify
            if actual_clarify:
                is_correct = True
                confusion["clarify_correct"] += 1
            else:
                confusion["clarify_missed"] += 1
        else:
            # 期望直接路由
            if actual_clarify:
                # 不该触发但触发了
                confusion["clarify_wrongly"] += 1
            elif actual_route == expected_route:
                is_correct = True
            else:
                confusion["route_wrong"] += 1
        
        if is_correct:
            correct += 1
            mark = "✅"
        else:
            mark = "❌"
            failed_cases.append({
                "query": query,
                "expected_route": expected_route,
                "expected_clarify": expected_clarify,
                "actual_route": actual_route,
                "actual_clarify": actual_clarify,
                "confidence": confidence,
            })
        
        clarify_tag = "[Clarify]" if actual_clarify else f"[{actual_route}]"
        print(f"[{i:2d}/{total}] {mark} {query!r}")
        print(f"        期望: {'触发反问' if expected_clarify else expected_route} | "
              f"实际: {clarify_tag} (conf={confidence:.2f})")
    
    return {
        "total": total,
        "correct": correct,
        "accuracy": correct / total,
        "confusion": confusion,
        "failed_cases": failed_cases,
    }


def print_report(result: dict):
    print("\n" + "=" * 60)
    print("📊 评测报告")
    print("=" * 60)
    print(f"\n总用例数: {result['total']}")
    print(f"正确数: {result['correct']}")
    print(f"准确率: {result['accuracy']:.2%}")
    
    c = result["confusion"]
    print(f"\n详细分类:")
    print(f"  ✅ 正确触发反问: {c['clarify_correct']} 次")
    print(f"  ❌ 该反问但漏判: {c['clarify_missed']} 次")
    print(f"  ❌ 不该反问但反问: {c['clarify_wrongly']} 次")
    print(f"  ❌ 路由判错: {c['route_wrong']} 次")
    
    if result["failed_cases"]:
        print(f"\n失败用例:")
        for case in result["failed_cases"]:
            print(f"  - {case['query']!r}")
            print(f"    期望: route={case['expected_route']}, clarify={case['expected_clarify']}")
            print(f"    实际: route={case['actual_route']}, clarify={case['actual_clarify']}, conf={case['confidence']:.2f}")


if __name__ == "__main__":
    test_cases = load_test_cases("test_cases_intent.json")
    result = evaluate(test_cases)
    print_report(result)
    
    with open("eval_result_intent.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print("\n[评测结果已保存]")