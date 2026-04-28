"""
InfoHunter - Streamlit 前端界面
"""
import streamlit as st
# from agent import Agent
from agent_fc import FCAgent as Agent
from storage import ArticleStore
from collector import fetch_all_rss
from store_articles import store_articles


# ============================================
# 页面配置（必须放在最前面）
# ============================================
st.set_page_config(
    page_title="InfoHunter Agent",
    page_icon="🔍",
    layout="wide",
)


# ============================================
# 初始化（用 st.session_state 缓存，避免每次重新创建）
# ============================================
# session_state 是 Streamlit 的"记忆"机制
# 因为每次用户操作脚本都会重新执行，不用 session_state 的话
# agent 每次都会被重新创建，之前的对话记录也会丢失
if "agent" not in st.session_state:
    st.session_state.agent = Agent()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []



# ============================================
# 侧边栏
# ============================================
with st.sidebar:
    st.title("📊 系统信息")

    # 任务1: 显示数据库文章数量
    # 提示: 用 st.session_state.agent.rag.store.get_count() 获取数量
    #       用 st.metric("文章总数", 数量) 显示
    # TODO: 你来写（2行代码）
    count = st.session_state.agent.rag.store.get_count()
    st.metric("文章总数",count)
    
    st.divider()    # 分隔线

    # ===== 改进1: 抓取最新文章按钮 =====
    st.subheader("📥 数据管理")

    # 任务1: 写一个抓取按钮
    # 点击后执行: 抓取 RSS → 存入向量数据库 → 显示成功提示
    #
    # 提示:
    #   - if st.button("按钮文字"):  判断按钮是否被点击
    #   - with st.spinner("提示文字"):  显示加载动画
    #   - articles = fetch_all_rss()  抓取文章
    #   - store = st.session_state.agent.rag.store  获取存储实例
    #   - store_articles(articles, store)  存入向量数据库
    #   - st.success(f"成功信息")  显示成功提示
    #   - st.rerun()  刷新页面（更新文章数量）
    # TODO: 你来写
    if st.button("🔄 抓取最新文章"):
        with st.spinner("正在抓取并过滤文章..."):
            # 第1步：抓取
            articles = fetch_all_rss()
            
            # 第2步：关键词过滤（只用粗筛，不调 LLM，省钱省时间）
            from subscription import load_subscriptions, keyword_filter
            topics = load_subscriptions()["topics"]
            
            filtered = []
            for article in articles:
                matched = keyword_filter(article, topics)
                if matched:
                    article["matched_topics"] = matched
                    filtered.append(article)
            
            # 第3步：只把通过过滤的文章存入向量库
            store = st.session_state.agent.rag.store
            store_articles(filtered, store)
    
        st.success(f"抓取 {len(articles)} 篇，过滤后保留 {len(filtered)} 篇")
        st.rerun()
    
    if st.button("📨 推送简报到微信"):
        with st.spinner("正在生成并推送简报..."):
            # 从向量库取所有文章 → 调用 push_daily_brief → 显示成功
            store = st.session_state.agent.rag.store
        count = store.get_count()
        if count == 0:
            st.warning("数据库里没有文章，请先抓取")
        else:
            all_data = store.collection.get()
            # 拼接简报内容
            content = f"共 {count} 篇文章\n\n"
            for meta in all_data["metadatas"]:
                title = meta.get('title', '')
                source = meta.get('source', '')
                link = meta.get('link', '')
                content += f"- [{title}]({link}) ({source})\n"
            # 推送
            from notifier import push_to_wechat
            push_to_wechat("📢 InfoHunter 简报", content)
            st.success("推送成功，请查看微信")

    st.divider()

    # 清空对话按钮
    if st.button("🗑️ 清空对话记录"):
        st.session_state.chat_history = []
        st.rerun()   # 重新运行页面


# ============================================
# 主界面 - 用标签页切换"对话"和"文章列表"
# ============================================
tab1, tab2 = st.tabs(["💬 智能问答", "📄 文章列表"])


# ===== 标签页1: 智能问答 =====
with tab1:
    st.title("🔍 InfoHunter Agent")
    st.caption("基于 RAG + Function Calling 的智能信息追踪系统")

    # 显示历史对话
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # # 用户输入
    # user_input = st.chat_input("输入你的问题...")

    # if user_input:
    #     with st.chat_message("user"):
    #         st.write(user_input)
    #     st.session_state.chat_history.append({"role": "user", "content": user_input})

    #     with st.chat_message("assistant"):
    #         with st.spinner("Agent 思考中..."):
    #             answer = st.session_state.agent.run(user_input)
    #         st.write(answer)
    #     st.session_state.chat_history.append({"role": "assistant", "content": answer})
    # 用户输入
    user_input = st.chat_input("输入你的问题...")

    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        with st.spinner("Agent 思考中..."):
            answer = st.session_state.agent.run(user_input)

        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        st.rerun()

# ===== 标签页2: 文章列表 =====
with tab2:
    st.title("📄 文章列表")

    # 任务2: 展示数据库中的所有文章
    # 
    # 提示:
    #   - store = st.session_state.agent.rag.store
    #   - count = store.get_count()
    #   - 如果 count == 0，用 st.info("暂无文章，请先在侧边栏点击抓取") 提示
    #   - 如果有文章，用 store.collection.get() 获取所有数据
    #     返回值是字典: {"ids": [...], "documents": [...], "metadatas": [...]}
    #   - 遍历 metadatas，展示每篇文章的信息
    #   - 用 st.expander(标题) 做可折叠展示:
    #     with st.expander(f"[来源] 标题"):
    #         st.write(f"日期: {meta['date']}")
    #         st.write(f"内容: {doc[:200]}...")
    # TODO: 你来写
    store = st.session_state.agent.rag.store
    count = store.get_count()
    if count==0:
        st.info("暂无文章，请先在侧边栏点击抓取")
    else:
        all_data = store.collection.get()
        for doc,meta in zip(all_data["documents"],all_data["metadatas"]):
            with st.expander(f"[{meta.get('source','')}] {meta.get('title','')}"):
                st.write(f"日期: {meta.get('date','')}")
                st.write(f"内容: {doc}")
            