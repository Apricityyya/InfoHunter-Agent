"""
测试通义千问 Embedding API
"""
from openai import OpenAI
from config import DASHSCOPE_API_KEY, DASHSCOPE_BASE_URL

client = OpenAI(
    api_key=DASHSCOPE_API_KEY,
    base_url=DASHSCOPE_BASE_URL,
)

# 调用 Embedding API
response = client.embeddings.create(
    model="text-embedding-v3",        # 通义千问的 Embedding 模型
    input=["AI Agent 是什么？", "今天天气真好"],   # 传入两段文字
)

# 看看返回了什么
print(f"返回了 {len(response.data)} 个向量")
print(f"每个向量的维度: {len(response.data[0].embedding)}")
print(f"向量前5个数字: {response.data[0].embedding[:5]}")