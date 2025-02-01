import streamlit as st
from openai import OpenAI

def render_chatgpt_chat(*args):  # 添加*args来忽略任何传入的参数
    """渲染ChatGPT对话界面"""
    # 初始化对话历史
    if "chatgpt_messages" not in st.session_state:
        st.session_state.chatgpt_messages = []
    
    # 初始化OpenAI客户端
    client = OpenAI(
        api_key="sk-1pUmQlsIkgla3CuvKTgCrzDZ3r0pBxO608YJvIHCN18lvOrn",
        base_url="https://api.chatanywhere.tech/v1"
    )

    # 显示对话历史
    for message in st.session_state.chatgpt_messages:
        if message["role"] == "user":
            st.write("👤 You:")
            st.markdown(message["content"])
        else:
            st.write("🤖 Assistant:")
            st.markdown(message["content"])
        st.write("---")

    # 用户输入区域
    col1, col2 = st.columns([4, 1])
    
    with col1:
        user_input = st.text_input(
            "输入你的问题...",
            key="chatgpt_input",
            label_visibility="collapsed"
        )
    
    with col2:
        send_button = st.button("发送", key="send_chatgpt")
    
    if send_button and user_input:
        # 添加用户消息
        st.session_state.chatgpt_messages.append({"role": "user", "content": user_input})
        
        # 获取ChatGPT响应
        with st.spinner("思考中..."):
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.chatgpt_messages
                ],
                temperature=0.1,
                max_tokens=1000
            )
            message = response.choices[0].message.content
            st.session_state.chatgpt_messages.append({"role": "assistant", "content": message})
        
        st.rerun()

    # 清空对话按钮
    if st.button("清空对话", key="clear_chatgpt"):
        st.session_state.chatgpt_messages = []
        st.rerun() 