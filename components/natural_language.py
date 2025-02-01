import streamlit as st
import pandas as pd

def render_natural_language_query(llm, db, history_db):
    """渲染自然语言查询界面"""
    # 初始化session_state
    if 'query_state' not in st.session_state:
        st.session_state.query_state = {
            'sql_results': None,
            'deepseek_result': None,
            'chatgpt_result': None,
            'current_query': None,
            'log_messages': [],
            'system_prompt': """你是一个SQLite数据库专家，请将用户的自然语言转换为SQLite SQL查询语句。
            
            注意事项：
            1. 使用SQLite支持的语法
            2. 不要使用其他数据库特有的函数
            3. 日期函数使用SQLite的date/datetime函数
            4. 字符串连接使用 || 而不是 CONCAT
            5. 使用标准的SQL聚合函数(COUNT, SUM, AVG, MAX, MIN)
            6. 请按照以下格式编写SQL:
               - SELECT/INSERT/UPDATE/DELETE 单独一行
               - FROM 子句单独一行
               - WHERE/GROUP BY/HAVING/ORDER BY 各自单独一行
               - JOIN 子句每个单独一行
               - 使用适当的缩进
               - 子查询使用合适的换行和缩进
            
            目前的数据库表结构如下：
            
            DEPT (部门表):
            - DEPTNO: INTEGER PRIMARY KEY (部门编号)
            - DNAME: TEXT (部门名称)
            - LOC: TEXT (位置)
            
            EMP (员工表):
            - EMPNO: INTEGER PRIMARY KEY (员工编号)
            - ENAME: TEXT (员工姓名)
            - JOB: TEXT (职位)
            - MGR: INTEGER (上级编号)
            - HIREDATE: DATE (入职日期)
            - SAL: DECIMAL (薪资)
            - COMM: DECIMAL (提成)
            - DEPTNO: INTEGER (部门编号)
            
            SALGRADE (薪资等级表):
            - GRADE: INTEGER PRIMARY KEY (等级)
            - LOSAL: DECIMAL (最低工资)
            - HISAL: DECIMAL (最高工资)
            
            BONUS (奖金表):
            - ENAME: TEXT (员工姓名)
            - JOB: TEXT (职位)
            - SAL: DECIMAL (薪资)
            - COMM: DECIMAL (奖金)
            
            请只返回SQL语句，不需要其他解释。确保SQL语句符合SQLite语法规范。"""
        }

    # 使用form包装输入部分
    with st.form(key='query_form'):
        user_input = st.text_area("请输入你的自然语言查询:", height=100)
        col1, col2 = st.columns([4, 1])
        
        with col1:
            submit_button = st.form_submit_button("查询")
        with col2:
            save_button = st.form_submit_button("保存问题")
    
    # 处理保存操作
    if save_button and user_input:
        history_db.save_question(user_input)
        st.success("问题已保存！")
    
    # 处理查询操作
    if submit_button and user_input:
        col1, col2 = st.columns(2)
        
        with col2:
            st.subheader("ChatGPT生成的SQL:")
            with st.spinner("ChatGPT生成中..."):
                chatgpt_result = llm.generate_sql(user_input, db)
                
                if 'chatgpt' in chatgpt_result:
                    st.code(chatgpt_result['chatgpt']['sql'], language="sql")
                    st.info(f"生成耗时: {chatgpt_result['chatgpt']['time']:.2f}秒")
                    
                    # 直接执行并显示结果
                    with st.spinner("执行查询中..."):
                        result = db.execute_query(chatgpt_result['chatgpt']['sql'])
                        if isinstance(result, pd.DataFrame):
                            st.subheader("ChatGPT查询结果:")
                            st.dataframe(result)
                        else:
                            st.error(f"ChatGPT查询错误: {result}")
        
        with col1:
            st.subheader("DeepSeek生成的SQL:")
            log_container = st.empty()
            status_container = st.empty()
            
            with st.spinner("DeepSeek生成中..."):
                def log_handler(message):
                    if 'log_messages' not in st.session_state.query_state:
                        st.session_state.query_state['log_messages'] = []
                    st.session_state.query_state['log_messages'].append(message)
                    with log_container.container():
                        with st.expander("查看执行日志", expanded=False):
                            for msg in st.session_state.query_state['log_messages']:
                                if msg.startswith('==='):
                                    st.markdown(f"**{msg}**")
                                elif msg.startswith('['):
                                    if 'SQL验证成功' in msg:
                                        st.success(msg)
                                    elif 'SQL执行失败' in msg:
                                        st.error(msg)
                                    elif '生成的SQL' in msg:
                                        time, sql = msg.split('生成的SQL:', 1)
                                        st.info(time + '生成的SQL:')
                                        st.code(sql.strip(), language='sql')
                                    else:
                                        st.info(msg)
                
                deepseek_result = llm._generate_sql_deepseek(
                    st.session_state.query_state['system_prompt'],
                    user_input,
                    db,
                    log_callback=log_handler
                )
                
                if isinstance(deepseek_result, dict):
                    st.code(deepseek_result['sql'], language="sql")
                    st.info(f"生成耗时: {deepseek_result['time']:.2f}秒")
                    
                    if deepseek_result['success']:
                        with st.spinner("执行查询中..."):
                            result = db.execute_query(deepseek_result['sql'])
                            if isinstance(result, pd.DataFrame):
                                st.subheader("DeepSeek查询结果:")
                                st.dataframe(result)
                            else:
                                st.error(f"DeepSeek查询错误: {result}")
                    else:
                        st.error(f"SQL生成失败: {deepseek_result['error']}")
    
    elif not user_input:
        st.warning("请输入查询内容") 