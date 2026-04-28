# 🔍 InfoHunter-Agent

一个基于 **RAG + Agent** 的智能信息追踪系统。自动从 RSS 源抓取文章，通过关键词粗筛 + LLM 精筛进行两层过滤，将文章向量化存入 ChromaDB，支持用户通过自然语言提问获取有依据、可溯源的回答。

## 功能特性

- **RSS 自动抓取**：支持配置多个 RSS 源，自动抓取最新文章
- **两层智能过滤**：关键词粗筛（快速、免费）+ LLM 精筛（精准、低成本），有效减少信息噪声
- **AI 摘要提炼**：自动对文章进行摘要、打标签、分类、评估重要性
- **RAG 知识问答**：基于向量检索的问答系统，回答时引用来源，确保信息有据可查
- **Agent 智能路由**：自动识别用户意图，判断是检索文章、查询统计还是直接对话
- **Web 交互界面**：基于 Streamlit 的对话式界面，支持实时问答

## 技术架构

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│  RSS 源抓取  │────→│  两层过滤     │────→│  AI 摘要提炼  │
│ (feedparser) │     │ 关键词+LLM   │     │ (通义千问)    │
└─────────────┘     └──────────────┘     └──────┬───────┘
                                                │
                                                ▼
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│  Streamlit  │←────│  Agent 路由   │←────│ 向量化存储    │
│  前端界面    │     │ 意图识别+工具  │     │ (ChromaDB)   │
└─────────────┘     └──────────────┘     └──────────────┘
                          │
                    ┌─────┴─────┐
                    ▼           ▼
              RAG 检索      直接对话
              带来源回答    通用问答
```

**数据处理流程**：RSS 抓取 → 关键词粗筛 → LLM 精筛 → 正文提取 → AI 摘要 → Embedding 向量化 → 存入 ChromaDB

**问答流程**：用户提问 → Agent 意图识别 → 选择工具（RAG 检索 / 统计查询 / 直接对话） → 生成回答

## 技术栈

| 技术                | 用途                           | 选择理由                                             |
| ------------------- | ------------------------------ | ---------------------------------------------------- |
| Python              | 项目基础语言                   | AI 生态最完善，库支持丰富                            |
| 通义千问 API (Qwen) | LLM 对话、摘要、过滤、意图识别 | 中文效果好，有免费额度                               |
| text-embedding-v3   | 文本向量化                     | 通义千问配套 Embedding 模型，1024 维，中文语义理解强 |
| ChromaDB            | 向量数据库                     | 轻量级、本地运行、无需额外部署，适合快速原型         |
| feedparser          | RSS 解析                       | Python 标准 RSS 解析库，稳定可靠                     |
| BeautifulSoup       | 网页正文提取                   | HTML 解析的事实标准                                  |
| Streamlit           | Web 前端界面                   | 专为 AI 应用设计，几十行代码即可搭建交互界面         |

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/Apricityyya/InfoHunter-Agent.git
cd InfoHunter-Agent
```

### 2. 创建虚拟环境

```bash
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # Mac/Linux

#或者用conda
conda create -n venv python=3.11
conda activate venv
```

### 3. 安装依赖

```bash
pip install feedparser requests beautifulsoup4 openai chromadb streamlit
```

### 4. 配置 API Key

在 `config.py` 中填入你的通义千问 API Key：

```python
DASHSCOPE_API_KEY = "你的API Key"
```

> 注意：请勿将 API Key 提交到 GitHub。建议使用环境变量管理敏感配置。

### 5. 导入文章到向量数据库

```bash
python store_articles.py
```

### 6. 启动应用

```bash
streamlit run app.py
```

浏览器会自动打开 `http://localhost:8501`，即可开始使用。

## 项目结构

```
InfoHunter-Agent/
├── config.py           # 配置管理（API Key、模型名称）
├── collector.py        # RSS 信息采集模块
├── extractor.py        # 网页正文提取模块
├── subscription.py     # 订阅管理 + 两层过滤（关键词粗筛 + LLM 精筛）
├── summarizer.py       # AI 摘要提炼模块
├── storage.py          # 向量存储模块（Embedding + ChromaDB）
├── store_articles.py   # 文章批量导入脚本
├── rag.py              # RAG 问答引擎
├── agent.py            # Agent 意图路由 + 工具调用
├── pipeline.py         # 完整处理流程串联
├── app.py              # Streamlit 前端界面
├── subscriptions.json  # 用户订阅配置
└── README.md           # 项目说明文档
```
