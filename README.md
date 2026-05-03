# 🔍 InfoHunter-Agent

> 一个面向求职者的 **多 Agent 智能助手系统**，基于 LangGraph + MCP + RAG 构建。

支持自然语言驱动的两类核心场景：(1) 求职信息检索 —— 自动监控行业资讯并基于向量检索回答用户问题；(2) 简历-岗位匹配评估 —— 智能分析候选人简历与目标 JD 的匹配度并生成个性化改进建议。系统已部署至阿里云 ECS，通过 cron 定时任务实现每日自动运行，并提供 Web 与微信双端交互。

---

## ✨ 核心能力

### 🤖 Agent 架构（项目核心）

- **LangGraph 多 Agent 协同**：基于状态机式编排，将单 Agent 拆分为 Orchestrator（调度）/ Info Agent（信息检索）/ Eval Agent（简历评估）/ Chat Node（兜底闲聊）四个独立节点，各司其职、协作完成复杂任务
- **基于置信度的澄清式追问**：Orchestrator 输出 (route, confidence) 双字段，置信度低于阈值（0.7）时进入 Clarify Node 主动反问用户，避免误判；多轮对话由调用方驱动，通过上下文增强让第二轮判断准确率从 60% 提升至 95%
- **MCP 协议工具集成**：将简历评估的 4 个核心工具（parse_resume / parse_jd / compute_match_score / generate_gap_report）封装为标准 MCP Server，对外提供与厂商解耦的工具接口；同时在内部 Agent 中保留直连调用以避免不必要的进程间通信开销，体现工程权衡
- **关注点分离的 LLM 调用层**：通用能力（重试、指数退避、JSON 解析、Fallback）抽离至 `llm_utils` 模块，每个 Agent 只关注业务逻辑

### 📚 RAG 知识检索

- **多 RSS 源采集 + 两层智能过滤**：关键词粗筛（规则匹配，零成本）+ LLM 精筛（语义理解，按需调用），信息噪声降低约 60%
- **Embedding 向量化检索**：基于 text-embedding-v3（1024 维）+ ChromaDB 持久化向量库，支持语义级文章召回
- **带溯源引用的回答**：所有回答自动标注来源链接（[1] [2] ...），保证信息可追溯

### 📊 评测体系（面试硬通货）

| 评测维度         | 测试集规模              | 当前指标 |
| ---------------- | ----------------------- | -------- |
| 意图识别准确率   | 40 用例（明确 + 模糊）  | 95%      |
| 工具调用成功率   | 5 输入 × 4 工具 = 20 次 | 100%     |
| 端到端评分合理性 | 5 组（强/弱/中等匹配）  | 100%     |

测评代码与数据全部归档于 `evaluation/` 目录，每次代码变更都可回归测试。

### 🚀 部署与交互

- **阿里云 ECS 全自动部署**：通过 cron 实现每日定时抓取 + 过滤 + 推送
- **Server酱 微信推送**：自动生成带链接的每日简报推送至微信
- **Streamlit Web 界面**：三页签设计 —— 智能问答（含多轮澄清）/ 文章列表 / 简历评估
- **跨平台访问**：服务器常驻 8501 端口，手机/PC 浏览器均可直接访问

---

## 🏗 技术架构

### 整体架构图

```
                            ┌──────────────────┐
                            │   用户输入        │
                            └────────┬─────────┘
                                     ▼
                       ┌────────────────────────┐
                       │   Orchestrator Agent   │
                       │   (LLM 意图识别 +       │
                       │    置信度评估)          │
                       └─────────┬──────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              ▼                  ▼                  ▼
       confidence < 0.7    confidence ≥ 0.7    confidence ≥ 0.7
              │                  │                  │
              ▼                  │                  │
       ┌────────────┐            │                  │
       │  Clarify   │            │                  │
       │   Node     │            │                  │
       │ (反问澄清)  │            │                  │
       └─────┬──────┘            │                  │
             │              ┌────┴────┐         ┌───┴────┐
             │              ▼         ▼         ▼        ▼
             │        Info Agent  Eval Agent  Chat   Eval
             │        (RAG 检索)   (4 步流程)  Node   Agent
             │              │         │         │        │
             │              │    ┌────┴────┐   │        │
             │              │    │  MCP    │   │        │
             │              │    │ Server  │   │        │
             │              │    │ (4 工具) │   │        │
             │              │    └────┬────┘   │        │
             │              │         │         │        │
             └──────────────┴─────────┴─────────┴────────┘
                                     │
                                     ▼
                              ┌────────────┐
                              │    END     │
                              └────────────┘
```

### 数据流：从信息采集到知识问答

```
RSS 源
  ↓
collector.py  (feedparser 解析)
  ↓
subscription.py  (关键词粗筛)
  ↓
subscription.py  (LLM 语义精筛)
  ↓
extractor.py  (网页正文提取)
  ↓
summarizer.py  (AI 摘要 + 标签 + 重要性)
  ↓
storage.py  (Embedding 向量化 + ChromaDB)
  ↓
rag.py  (语义检索 + 上下文构建 + LLM 生成)
  ↓
带溯源引用的回答
```

### 简历评估流：Eval Agent 内部 4 步链路

```
用户输入: 简历文本 + JD 文本
       ↓
┌──────────────────────────┐
│ Step 1: parse_resume     │  提取 skills / experiences /
│         (LLM)            │  education / highlights
└──────────┬───────────────┘
           ↓
┌──────────────────────────┐
│ Step 2: parse_jd         │  提取 required_skills /
│         (LLM)            │  preferred_skills /
└──────────┬───────────────┘  responsibilities / level
           ↓
┌──────────────────────────┐
│ Step 3: compute_match    │  打分 (0-100) + 维度拆解
│         _score (LLM)     │  输出 matched / missing 要点
└──────────┬───────────────┘
           ↓
┌──────────────────────────┐
│ Step 4: generate_gap     │  自然语言改进建议（300-1000 字）
│         _report (LLM)    │  含优势分析 + 差距诊断 + 具体行动
└──────────┬───────────────┘
           ↓
   匹配评分 + 详细报告
```

> **设计权衡**：为何分 4 步而非一次性 prompt？分步设计的好处是 ① 每一步可独立调试和评测；② 每个 prompt 任务单一，准确率更高；③ 工具粒度更细，便于通过 MCP 暴露和复用。

---

## 🛠 技术栈

| 类别           | 技术                         | 选择理由                                                                      |
| -------------- | ---------------------------- | ----------------------------------------------------------------------------- |
| **Agent 编排** | LangGraph                    | 状态机式可视化编排，原生支持条件路由、状态持久化、流式输出，工业事实标准      |
| **工具协议**   | MCP (Model Context Protocol) | Anthropic 主导的标准协议，实现 Agent 与工具解耦；2026 年大厂 JD 高频技术词    |
| **LLM 后端**   | 通义千问 Qwen3               | 中文能力强，免费额度充足                                                      |
| **Embedding**  | text-embedding-v3 (1024d)    | 通义千问配套，中文语义理解优于通用模型                                        |
| **向量库**     | ChromaDB                     | 轻量级嵌入式数据库，零运维，适合中小规模场景；亿级以上数据可平滑迁移至 Milvus |
| **RSS 解析**   | feedparser                   | Python 标准 RSS 解析库                                                        |
| **网页提取**   | BeautifulSoup                | HTML 解析事实标准                                                             |
| **Web 前端**   | Streamlit                    | 专为 AI 应用设计，多页签 + 长表单 + 进度可视化开箱即用                        |
| **微信推送**   | Server酱                     | 免费 Webhook 推送，符合微信平台规范                                           |
| **部署**       | 阿里云 ECS + cron            | 学生优惠成本低，cron 实现零成本定时调度                                       |

---

## 🔍 几个值得深挖的工程细节

### 1. 为什么不在 Eval Agent 里直接调用 MCP？

> 同进程内直接函数调用比走 MCP 协议（启动子进程 + 序列化 + IPC）快约 10 倍。MCP 的真正价值在于**让外部系统**能以标准协议复用工具。所以本项目采用**双轨架构**：Eval Agent 内部直连保性能，MCP Server 对外暴露保通用性。

### 2. 为什么置信度阈值设为 0.7？

> 通过 40 用例评测发现：阈值 0.7 时澄清触发率 60%，无误拦；阈值 0.8 时拦截过多明确 case，体验下降。这是经过实测的折中点。同时承认 LLM 主观置信度本身存在局限（某些错误判断也会给高置信度），未来工作中将引入客观信号（关键词覆盖度、向量相似度）补充。

### 3. 为什么 LangGraph 不能"等待用户输入"？

> 因为 `graph.invoke()` 是同步执行——节点依次运行直到 END，无法暂停等待异步用户回复。多轮对话必须由**调用方驱动**：检测到 `is_clarifying=True` 后，把"原问题 + 反问 + 用户回复"拼接成增强输入再次 invoke。这是 LangGraph 的设计哲学：**图本身只描述执行流，对话状态由外部管理**。

### 4. 为什么 RAG 不做分块？

> 当前数据源是 RSS 摘要，长度通常在 200 字以内，分块反而会破坏语义完整性。代码中保留了固定长度分块和按段落分块两种实现，并在 `tests/experiment.py` 中验证段落分块在长文档场景下检索准确率更优。当未来接入长文档（如 PDF 技术报告）时可一键启用。

---

## 🚀 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/Apricityyya/InfoHunter-Agent.git
cd InfoHunter-Agent
```

### 2. 创建虚拟环境

```bash
# venv
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # macOS / Linux

# 或 conda
conda create -n infohunter python=3.11
conda activate infohunter
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

新建 `.env` 文件（已加入 `.gitignore`，不会上传到 GitHub）：

```dotenv
DASHSCOPE_API_KEY=你的通义千问API_Key
SERVER_CHAN_KEY=你的Server酱SendKey
```

### 5. 启动 Web 界面

```bash
streamlit run app.py
```

浏览器自动打开 `http://localhost:8501`，三个页签：

- **💬 智能问答**：自然语言提问，自动路由到信息检索 / 简历评估 / 闲聊
- **📄 文章列表**：浏览已采集的所有文章
- **📋 简历评估**：粘贴简历 + JD，一键获取匹配评分和改进建议

### 6. 一键推送简报（可选）

```bash
python auto_brief.py
```

抓取最新文章并推送到微信，可配置至 cron 实现每日自动运行。

### 7. 运行评测（可选）

```bash
cd evaluation
python eval_intent.py    # 意图识别评测
python eval_tools.py     # 工具调用评测
python eval_e2e.py       # 端到端评估合理性测试
```

---

## 📁 项目结构

```
InfoHunter-Agent/
│
├── app.py                       # Streamlit 前端（3 页签 + 多轮澄清对话）
├── auto_brief.py                # 一键抓取+过滤+推送（cron 调度入口）
│
├── 【LangGraph 多 Agent 架构】
├── agents_state.py              # 共享 State 定义（含 confidence 等扩展字段）
├── agent_graph.py               # 主图组装（Orchestrator + Info + Eval + Clarify + Chat）
├── agent_orchestrator.py        # 调度 Agent（意图识别 + 置信度评估）
├── agent_info.py                # 信息 Agent（RAG 检索）
├── agent_eval.py                # 评估 Agent（4 步流程：parse → parse → score → report）
│
├── 【MCP 协议层】
├── mcp_resume_server.py         # MCP Server：暴露简历评估 4 工具
├── mcp_resume_client.py         # MCP Client 端到端测试
│
├── 【LLM 工具层】
├── llm_utils.py                 # 重试 + 退避 + JSON 解析 + Fallback
├── config.py                    # 配置管理（从 .env 读取）
│
├── 【数据采集与处理】
├── collector.py                 # RSS 采集
├── extractor.py                 # 网页正文提取
├── subscription.py              # 订阅管理 + 两层过滤
├── summarizer.py                # AI 摘要
├── storage.py                   # Embedding + ChromaDB（含分块策略）
├── store_articles.py            # 文章批量导入
├── rag.py                       # RAG 问答引擎
│
├── 【外部集成】
├── notifier.py                  # 微信推送（Server酱）
│
├── 【历史版本】（保留用于面试对比）
├── agent.py                     # 手写 prompt 路由版 Agent
├── agent_fc.py                  # Function Calling 版 Agent
├── pipeline.py                  # 早期串联版 pipeline
│
├── 【评测体系】
├── evaluation/
│   ├── test_cases_intent.json   # 40 个意图识别测试用例
│   ├── test_cases_tools.json    # 5 个工具调用测试用例
│   ├── test_cases_e2e.json      # 5 组端到端评估用例
│   ├── eval_intent.py           # 意图识别评测脚本
│   ├── eval_tools.py            # 工具调用评测脚本
│   ├── eval_e2e.py              # 端到端评估脚本
│   └── eval_result_*.json       # 历次评测结果存档
│
├── 【单元测试】
├── tests/
│   ├── test_llm.py
│   ├── test_embedding.py
│   ├── test_fc.py
│   ├── test_rss.py
│   ├── test_chunking.py
│   └── experiment.py            # 分块策略对比实验
│
├── subscriptions.json           # 用户订阅配置
├── requirements.txt             # 项目依赖
├── .env                         # 环境变量（不上传 GitHub）
├── .gitignore                   # Git 忽略规则
└── README.md                    # 本文档
```

---

## 🎯 演进路线

### 已完成（v2）

- [x] 单 Agent → LangGraph 多 Agent 架构升级
- [x] Function Calling → MCP 协议升级
- [x] 加入简历-JD 匹配评估能力（4 步流程）
- [x] 实现澄清式追问机制（基于置信度路由）
- [x] 三层评测体系（意图 / 工具 / 端到端）
- [x] Streamlit 前端整合多 Agent + 简历评估页

### 未来工作

- [ ] **客观置信度信号**：用 query 与意图描述的向量相似度替代或补充 LLM 主观置信度
- [ ] **持久化记忆**：跨会话的用户画像沉淀，让 Agent 在多次对话间保持对用户的认知
- [ ] **流式输出**：Streamlit 端展示 Agent 推理过程的中间步骤
- [ ] **分布式部署**：MCP Server 独立进程化，支持多 Agent 并发调用
- [ ] **真实流量评测**：收集线上用户真实 query 扩充测试集，做 A/B 测试

---

## 📜 License

MIT
