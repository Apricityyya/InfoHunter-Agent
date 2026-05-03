"""
InfoHunter - Streamlit 前端界面
"""
import streamlit as st

# ❌ 删掉这行
# from agent_fc import FCAgent as Agent

# ✅ 改用 LangGraph
from agent_graph import build_graph, make_initial_state
from rag import RAGEngine

from storage import ArticleStore
from collector import fetch_all_rss
from store_articles import store_articles


# ============================================
# 页面配置
# ============================================
st.set_page_config(
    page_title="InfoHunter Agent",
    page_icon="🔍",
    layout="wide",
)


# ============================================
# 初始化（session_state 缓存）
# ============================================
# RAG 引擎（用于侧边栏的"抓取/推送"按钮直接读写 store）
if "rag" not in st.session_state:
    st.session_state.rag = RAGEngine()

# LangGraph 主图（用于智能问答）
if "graph" not in st.session_state:
    st.session_state.graph = build_graph()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# ============================================
# 侧边栏
# ============================================
with st.sidebar:
    st.title("📊 系统信息")

    # 显示数据库文章数量
    count = st.session_state.rag.store.get_count()
    st.metric("文章总数", count)
    
    st.divider()

    # ===== 数据管理 =====
    st.subheader("📥 数据管理")

    if st.button("🔄 抓取最新文章"):
        with st.spinner("正在抓取并过滤文章..."):
            articles = fetch_all_rss()
            
            from subscription import load_subscriptions, keyword_filter
            topics = load_subscriptions()["topics"]
            
            filtered = []
            for article in articles:
                matched = keyword_filter(article, topics)
                if matched:
                    article["matched_topics"] = matched
                    filtered.append(article)
            
            store = st.session_state.rag.store
            store_articles(filtered, store)
    
        st.success(f"抓取 {len(articles)} 篇，过滤后保留 {len(filtered)} 篇")
        st.rerun()
    
    if st.button("📨 推送简报到微信"):
        with st.spinner("正在生成并推送简报..."):
            store = st.session_state.rag.store
            count = store.get_count()
            if count == 0:
                st.warning("数据库里没有文章，请先抓取")
            else:
                all_data = store.collection.get()
                content = f"共 {count} 篇文章\n\n"
                for meta in all_data["metadatas"]:
                    title = meta.get('title', '')
                    source = meta.get('source', '')
                    link = meta.get('link', '')
                    content += f"- [{title}]({link}) ({source})\n"
                
                from notifier import push_to_wechat
                push_to_wechat("📢 InfoHunter 简报", content)
                st.success("推送成功，请查看微信")

    st.divider()

    if st.button("🗑️ 清空对话记录"):
        st.session_state.chat_history = []
        st.rerun()


# ============================================
# 主界面 - 标签页
# ============================================
tab1, tab2, tab3= st.tabs(["💬 智能问答", "📄 文章列表", "📋 简历评估"])


# ===== 标签页1: 智能问答 =====
with tab1:
    st.title("🔍 InfoHunter Agent")
    st.caption("基于 LangGraph 多 Agent + MCP 协议的智能求职助手")

    # 显示历史对话
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    user_input = st.chat_input("输入你的问题...")

    if user_input:
        # 显示用户消息
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        with st.spinner("Agent 思考中..."):
            # 检查是否处于"等待澄清回复"状态
            if st.session_state.get("awaiting_clarify"):
                # 用户再回复反问，构造增强输入
                pending = st.session_state.awaiting_clarify
                augmented_input = augmented_input = f"""【对话上下文】
用户最初的提问: {pending['original_query']}
助手的澄清反问: {pending['clarify_question']}
用户的回复: {user_input}

请综合以上上下文判断用户的真实意图。"""
                state = make_initial_state(augmented_input)
                st.session_state.awaiting_clarify = None # 清除澄清状态（无论这次是否再次触发反问）

            else:  
                # 正常用 LangGraph 调用
                state = make_initial_state(user_input)
            result = st.session_state.graph.invoke(state)
            answer = result["final_answer"]

            # 检查这次结果是否出发clarify
            if result.get("is_clarifying"):
                # 记录澄清状态，下一次用户输入会被当做回复
                st.session_state.awaiting_clarify = {
                    "original_query":user_input,
                    "clarify_question":result["clarify_question"],
                }

        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        st.rerun()


# ===== 标签页2: 文章列表 =====
with tab2:
    st.title("📄 文章列表")

    store = st.session_state.rag.store
    count = store.get_count()
    if count == 0:
        st.info("暂无文章，请先在侧边栏点击抓取")
    else:
        all_data = store.collection.get()
        for doc, meta in zip(all_data["documents"], all_data["metadatas"]):
            with st.expander(f"[{meta.get('source', '')}] {meta.get('title', '')}"):
                st.write(f"日期: {meta.get('date', '')}")
                st.write(f"内容: {doc}")



# ===== 标签页3: 简历评估 =====
with tab3:
    st.title("📋 简历评估")
    st.caption("粘贴你的简历和岗位 JD，AI 会分析匹配度并给出改进建议")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📄 你的简历")
        resume_text = st.text_area(
            "粘贴简历内容",
            height=400,
            placeholder="把简历的文字内容复制粘贴到这里...\n\n建议包含：\n- 教育背景\n- 技能\n- 项目经历\n- 实习/工作经历",
            key="resume_input",
        )
    
    with col2:
        st.subheader("💼 目标岗位 JD")
        jd_text = st.text_area(
            "粘贴岗位描述",
            height=400,
            placeholder="把岗位 JD 复制粘贴到这里...\n\n建议包含：\n- 岗位职责\n- 任职要求\n- 加分项",
            key="jd_input",
        )
    
    if st.button("🚀 开始评估", type="primary", use_container_width=True):
        if not resume_text.strip() or not jd_text.strip():
            st.error("请同时提供简历和岗位 JD")
        else:
            with st.spinner("Agent 正在分析（约 30-60 秒）..."):
                # 直接调用 eval_agent_node 跑完整 4 步流程
                from agent_eval import eval_agent_node
                
                state = make_initial_state(
                    user_input="评估我的简历",
                    resume_text=resume_text,
                    jd_text=jd_text,
                )
                result = eval_agent_node(state)
            
            # 展示结果
            st.success("评估完成！")
            
            # 综合评分
            score = result["match_score"]
            st.markdown(f"### 📊 综合评分：**{score:.0f}/100**")
            
            # 进度条可视化
            st.progress(score / 100)
            
            st.divider()
            
            # 改进建议
            st.markdown("### 💡 详细分析与建议")
            st.markdown(result["gap_report"])