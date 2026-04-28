# 🔍 InfoHunter-Agent

一个基于 **RAG + Agent** 的智能信息追踪系统，面向求职者自动监控技术趋势、行业动态等信息。通过 RSS 自动抓取文章，关键词粗筛 + LLM 精筛两层过滤，将文章向量化存入 ChromaDB，支持自然语言问答并通过微信推送每日简报。已部署至阿里云 ECS，实现每日定时自动运行。

## 功能特性

- **RSS 多源自动抓取**：支持配置多个 RSS 源（技术博客、行业资讯、论文等），自动抓取最新文章
- **两层智能过滤**：关键词粗筛（快速、免费）+ LLM 精筛（精准、低成本），信息噪声降低约 70%
- **AI 摘要提炼**：自动对文章进行摘要、打标签、分类、评估重要性
- **RAG 知识问答**：基于 Embedding 向量检索的问答系统，回答时引用来源，确保有据可查
- **Agent 智能路由**：对比实现了手写 prompt 路由和标准 Function Calling 两种方案，支持多工具自动调用
- **多轮对话记忆**：基于对话历史的上下文理解，支持指代消解（如"它的分块策略有哪些？"）
- **分块策略对比**：实现固定长度分块和按段落分块两种策略，通过实验验证检索效果差异
- **微信简报推送**：通过 Server酱 Webhook 自动推送带链接的每日简报到微信
- **云服务器部署**：部署至阿里云 ECS，通过 cron 定时任务实现每日自动抓取、过滤、推送
- **Web 交互界面**：基于 Streamlit 的对话式界面，支持一键抓取、文章浏览和实时问答

## 技术架构

```
数据采集层                  数据处理层                   数据存储层
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│  RSS 源抓取  │────→│  两层过滤     │────→│  AI 摘要提炼  │
│ (feedparser) │     │ 关键词+LLM   │     │ (通义千问)    │
└─────────────┘     └──────────────┘     └──────┬───────┘
                                                │
                                                ▼
                                         ┌──────────────┐
                                         │ Embedding    │
                                         │ 向量化存储    │
                                         │ (ChromaDB)   │
                                         └──────┬───────┘
                                                │
交互层                      智能决策层            │
┌─────────────┐     ┌──────────────┐            │
│  Streamlit  │←────│ Agent 路由    │←───────────┘
│  Web 界面    │     │Function Call │
└─────────────┘     └──────┬───────┘
                           │
推送层              ┌──────┴───────┐
┌─────────────┐     │   工具选择    │
│  Server酱   │     ├──────────────┤
│  微信推送    │     │ RAG 检索     │
└─────────────┘     │ 统计查询     │
       ↑            │ 直接对话     │
       │            └──────────────┘
  auto_brief.py
  (cron 定时执行)
```

**数据处理流程**：RSS 抓取 → 关键词粗筛 → LLM 精筛 → 正文提取 → AI 摘要 → Embedding 向量化 → 存入 ChromaDB

**问答流程**：用户提问 → Agent 意图识别（Function Calling）→ 选择工具 → 生成带来源引用的回答

**推送流程**：cron 定时触发 → 抓取 → 过滤 → 存储 → 生成简报 → Server酱推送至微信

## 技术栈

| 技术                | 用途                           | 选择理由                                             |
| ------------------- | ------------------------------ | ---------------------------------------------------- |
| Python              | 项目基础语言                   | AI 生态最完善，库支持丰富                            |
| 通义千问 API (Qwen) | LLM 对话、摘要、过滤、意图识别 | 中文效果好，有免费额度                               |
| Function Calling    | Agent 工具调用                 | API 原生支持，比手写 prompt 路由更稳定               |
| text-embedding-v3   | 文本向量化                     | 通义千问配套 Embedding 模型，1024 维，中文语义理解强 |
| ChromaDB            | 向量数据库                     | 轻量级、本地运行、无需额外部署，适合快速原型         |
| feedparser          | RSS 解析                       | Python 标准 RSS 解析库，稳定可靠                     |
| BeautifulSoup       | 网页正文提取                   | HTML 解析的事实标准                                  |
| Streamlit           | Web 前端界面                   | 专为 AI 应用设计，几十行代码即可搭建交互界面         |
| Server酱            | 微信消息推送                   | 免费的 Webhook 推送服务，一行代码即可推送到微信      |
| 阿里云 ECS + cron   | 云服务器部署 + 定时任务        | 学生优惠价格低，cron 实现零成本定时执行              |

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/Apricityyya/InfoHunter-Agent.git
cd InfoHunter-Agent
```

### 2. 创建虚拟环境

```bash
# 方式一：venv
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # Mac/Linux

# 方式二：conda
conda create -n infohunter python=3.11
conda activate infohunter
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

创建 `.env` 文件：

```dotenv
DASHSCOPE_API_KEY=你的通义千问API_Key
SERVER_CHAN_KEY=你的Server酱SendKey
```

> 注意：`.env` 已在 `.gitignore` 中，不会上传到 GitHub。

### 5. 启动应用

```bash
streamlit run app.py
```

浏览器会自动打开 `http://localhost:8501`，在侧边栏点击"抓取最新文章"导入数据，即可开始使用。

### 6. 一键推送简报（可选）

```bash
python auto_brief.py
```

微信会收到带链接的文章简报。

## 项目结构

```
InfoHunter-Agent/
├── app.py              # Streamlit 前端界面（对话 + 文章列表 + 一键抓取/推送）
├── auto_brief.py       # 一键抓取+过滤+推送脚本（cron 定时执行此文件）
├── config.py           # 配置管理（从 .env 读取 API Key）
├── collector.py        # RSS 信息采集模块
├── extractor.py        # 网页正文提取模块
├── subscription.py     # 订阅管理 + 两层过滤（关键词粗筛 + LLM 精筛）
├── summarizer.py       # AI 摘要提炼模块
├── storage.py          # 向量存储模块（Embedding + ChromaDB + 分块策略）
├── store_articles.py   # 文章批量导入脚本
├── rag.py              # RAG 问答引擎（检索 + 构建上下文 + LLM 回答）
├── agent.py            # 手写 prompt 路由版 Agent
├── agent_fc.py         # Function Calling 版 Agent（含多轮对话记忆）
├── notifier.py         # 微信推送模块（Server酱）
├── pipeline.py         # 完整处理流程串联
├── import.py           # 手动导入模块（URL / 文本）
├── subscriptions.json  # 用户订阅配置（关注话题 + 关键词）
├── requirements.txt    # 项目依赖
├── .env                # 环境变量（不上传 GitHub）
├── .gitignore          # Git 忽略规则
├── tests/              # 测试文件
│   ├── test_llm.py         # LLM API 测试
│   ├── test_embedding.py   # Embedding API 测试
│   ├── test_fc.py          # Function Calling 测试
│   ├── test_rss.py         # RSS 源可用性测试
│   ├── test_chunking.py    # 分块功能测试
│   └── experiment.py       # 分块策略对比实验
└── README.md           # 项目说明文档
```
