"""
InfoHunter - 配置文件
注意：API Key是敏感信息，不能上传到GitHub！
"""
import os
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

# 通义千问 API 配置
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")

# 通义千问的API地址（兼容openai格式）
DASHSCOPE_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"

# 使用的模型名称（可根据实际需要替换）
MODEL_NAME = "qwen3.6-plus"

