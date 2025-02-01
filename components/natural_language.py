import streamlit as st
import pandas as pd

def render_natural_language_query(llm, db, history_db):
    """渲染自然语言查询界面"""
    # 初始化session_state
    if 'sql_results' not in st.session_state:
        st.session_state.sql_results = None
    if 'deepseek_result' not in st.session_state:
        st.session_state.deepseek_result = None
    if 'chatgpt_result' not in st.session_state:
        st.session_state.chatgpt_result = None
    if 'query_clicked' not in st.session_state:
        st.session_state.query_clicked = False

    def handle_query():
        st.session_state.query_clicked = True
    
    # 检查是否要复用历史问题
    if hasattr(st.session_state, 'reuse_question'):
        user_input = st.text_area(
            "请输入你的自然语言查询:",
            value=st.session_state.reuse_question,
            height=100
        )
        del st.session_state.reuse_question
    else:
        user_input = st.text_area("请输入你的自然语言查询:", height=100)
    
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.button("查询", key="nlq", on_click=handle_query)
    with col2:
        if st.button("保存问题", key="save_q") and user_input:
            history_db.save_question(user_input)
            st.success("问题已保存！")
    
    # 处理查询点击
    if st.session_state.query_clicked and user_input:
        with st.spinner("正在生成SQL..."):
            st.session_state.sql_results = llm.generate_sql(user_input)
            st.session_state.deepseek_result = None
            st.session_state.chatgpt_result = None
        st.session_state.query_clicked = False  # 重置查询状态
    
    # 如果有SQL结果，显示它们
    if st.session_state.sql_results:
        # 显示两个模型的SQL
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("DeepSeek生成的SQL:")
            st.code(st.session_state.sql_results.get('deepseek', 'Error: No SQL generated'), language="sql")
            
            # 执行DeepSeek SQL
            if st.button("执行DeepSeek SQL", key="run_deepseek"):
                with st.spinner("执行查询中..."):
                    result = db.execute_query(st.session_state.sql_results['deepseek'])
                    st.session_state.deepseek_result = result
            
            # 显示DeepSeek的执行结果
            if st.session_state.deepseek_result is not None:
                if isinstance(st.session_state.deepseek_result, pd.DataFrame):
                    st.subheader("DeepSeek查询结果:")
                    st.dataframe(st.session_state.deepseek_result)
                else:
                    st.error(f"DeepSeek查询错误: {st.session_state.deepseek_result}")
        
        with col2:
            st.subheader("ChatGPT生成的SQL:")
            if 'chatgpt' in st.session_state.sql_results:
                st.code(st.session_state.sql_results['chatgpt'], language="sql")
                
                # 执行ChatGPT SQL
                if st.button("执行ChatGPT SQL", key="run_chatgpt"):
                    with st.spinner("执行查询中..."):
                        result = db.execute_query(st.session_state.sql_results['chatgpt'])
                        st.session_state.chatgpt_result = result
                
                # 显示ChatGPT的执行结果
                if st.session_state.chatgpt_result is not None:
                    if isinstance(st.session_state.chatgpt_result, pd.DataFrame):
                        st.subheader("ChatGPT查询结果:")
                        st.dataframe(st.session_state.chatgpt_result)
                    else:
                        st.error(f"ChatGPT查询错误: {st.session_state.chatgpt_result}")
            else:
                st.error("ChatGPT未能生成SQL（可能是配置问题）")
    elif not user_input:
        st.warning("请输入查询内容") 