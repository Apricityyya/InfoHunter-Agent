"""
LLM 调用工具模块
统一封装：客户端创建、重试机制、JSON解析等通用能力
"""

import json
import time
from openai import OpenAI
from config import DASHSCOPE_API_KEY,DASHSCOPE_BASE_URL,MODEL_NAME

# ============ 全局唯一的 LLM 客户端 ============
# 模块级单例：所有 Agent 共用一个 client，避免重复创建连接
client = OpenAI(
    api_key=DASHSCOPE_API_KEY,
    base_url=DASHSCOPE_BASE_URL,
)


# ============ 带重试的 LLM 调用 ============
def call_llm(prompt:str,max_retries:int = 3,**kwargs) -> str:
    """
    调用LLM并自动重试

    参数：
        prompt: 提示词
        max_retries: 最大重试次数
        **kwargs: 透传给API的其它参数(如 tools、temperature)

    返回：
        LLM回复的字符串内容

    异常：
        重试max_retries次后仍失败，抛出最后一次异常
    """
    last_error = None

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role":"user","content":prompt}],
                extra_body={"enable_thinking":False},
                **kwargs,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt #指数退避：1s, 2s, 4s
                print(f" [LLM 调用失败 {attempt+1}/{max_retries}: {e}, {wait_time}s 后重试]")
                time.sleep(wait_time)
            else:
                print(f" [LLM 调用最终失败: {e}]")
        raise last_error
    

# ============ JSON 解析（带 ```json``` 清理） ============
def parse_llm_json(reply:str)->dict:
    """
    解析 LLM 返回的 JSON 字符串
    自动清理 ```json``` 代码块包裹
    
    参数:
        reply: LLM 返回的原始字符串
        
    返回:
        解析后的字典
        
    异常:
        JSON 格式错误时抛出 json.JSONDecodeError
    """
    reply = reply.strip()

    # 清理 ```json``` 包裹
    if reply.startswith("```"):
        reply = reply.split("```")[1]
        if reply.startswith("json"):
            reply = reply[4:]
    reply = reply.strip()

    return json.loads(reply)
    


# ============ 一站式：调 LLM + 解析 JSON ============
def call_llm_json(prompt:str,default:dict=None,**kwargs) -> dict:
    """
    调用LLM并解析JSON，失败时返回默认值

    参数：  
        prompt: 提示词
        default: 失败时返回的默认值(None 时返回空字典)

    返回：
        解析后的字典，或失败时的 default
    """
    try:
        reply = call_llm(prompt,**kwargs)
        return parse_llm_json(reply)
    except Exception as e:
        print(f" [JSON 解析或 LLM 调用失败: {e}, 返回默认值]")
        return default if default is not None else {}
        
