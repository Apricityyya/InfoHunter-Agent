"""
测试通义千问API是否能正常调用
"""

from openai import OpenAI
from config import DASHSCOPE_API_KEY,DASHSCOPE_BASE_URL,MODEL_NAME

# 创建客户端（QWEN兼容OpenAI接口，所以用OpenAI库就能调）
client = OpenAI(
    api_key=DASHSCOPE_API_KEY,
    base_url=DASHSCOPE_BASE_URL,
)

# 发一条最简单的消息测试
response = client.chat.completions.create(
    model=MODEL_NAME,
    messages=[
        {"role":"user","content":"你好，请用一句话介绍你自己"}
    ],
)

# 提取回复内容
reply = response.choices[0].message.content
print(f"通义千问回复：{reply}")


