import streamlit as st

def render_chat(llm):
    """渲染对话界面"""
    # 初始化会话状态
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # 初始化输入状态
    if "chat_input_key" not in st.session_state:
        st.session_state.chat_input_key = 0

    # 消息处理函数
    def handle_message(user_input):
        if user_input:
            # 添加用户消息
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # 获取助手响应
            response = llm.chat(user_input)
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            # 通过改变key来重置输入框
            st.session_state.chat_input_key += 1

    # 显示对话历史
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 用户输入区域
    col1, col2 = st.columns([4, 1])
    
    with col1:
        user_input = st.text_input(
            "输入你的问题...",
            key=f"chat_input_{st.session_state.chat_input_key}",
            label_visibility="collapsed"
        )
    
    with col2:
        if st.button("发送", key="send_chat"):
            handle_message(user_input)
            st.rerun()

    # 清空对话按钮
    if st.button("清空对话", key="clear_chat"):
        st.session_state.messages = []
        st.session_state.chat_input_key += 1
        st.rerun() 