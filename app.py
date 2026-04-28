"""
InfoHunter - Streamlit 前端界面
"""
import streamlit as st
# from agent import Agent
from agent_fc import FCAgent as Agent
from storage import ArticleStore


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

    # 清空对话按钮
    if st.button("🗑️ 清空对话记录"):
        st.session_state.chat_history = []
        st.rerun()   # 重新运行页面


# ============================================
# 主界面
# ============================================
st.title("🔍 InfoHunter Agent")
st.caption("基于 RAG 的智能信息追踪系统 | 输入问题，Agent 会自动检索相关文章并回答")


# ============================================
# 显示历史对话
# ============================================
# 任务2: 遍历 st.session_state.chat_history，显示每条对话
# chat_history 的结构是: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}, ...]
# 用 st.chat_message(role) 显示对话气泡
#
# 示例:
#   with st.chat_message("user"):
#       st.write("用户说的话")
#   with st.chat_message("assistant"):
#       st.write("AI的回答")
#
# TODO: 用 for 循环遍历 chat_histo
for msg in st.session_state.chat_history:
    role = msg.get("role","")
    content = msg.get("content","")
    with st.chat_message(role):
        st.write(content)



# ============================================
# 用户输入
# ============================================
user_input = st.chat_input("输入你的问题...")   # 底部输入框

if user_input:
    # 显示用户消息
    with st.chat_message("user"):
        st.write(user_input)

    # 保存用户消息到历史
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # Agent 处理
    with st.chat_message("assistant"):
        # 任务3: 调用 Agent 获取回答并显示
        #
        # 步骤:
        #   1. 用 with st.spinner("思考中...") 包裹调用过程（显示加载动画）
        #   2. 在 spinner 里面调用 st.session_state.agent.run(user_input)
        #   3. 用 st.write(answer) 显示回答
        #   4. 把 assistant 的回答也保存到 chat_history
        #
        # TODO: 你来写
        with st.spinner("Agent 思考中..."):
            answer = st.session_state.agent.run(user_input)
        st.write(answer)
        st.session_state.chat_history.append({"role":"assistant","content":answer})