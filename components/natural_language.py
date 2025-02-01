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
    if 'current_query' not in st.session_state:
        st.session_state.current_query = None
    if 'system_prompt' not in st.session_state:
        st.session_state.system_prompt = """你是一个SQLite数据库专家，请将用户的自然语言转换为SQLite SQL查询语句。
        
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
    
    def handle_query():
        st.session_state.query_clicked = True
        st.session_state.current_query = user_input
    
    def execute_deepseek():
        with st.spinner("执行查询中..."):
            result = db.execute_query(st.session_state.sql_results['deepseek']['sql'])
            st.session_state.deepseek_result = result
    
    def execute_chatgpt():
        with st.spinner("执行查询中..."):
            result = db.execute_query(st.session_state.sql_results['chatgpt']['sql'])
            st.session_state.chatgpt_result = result
    
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
    if st.session_state.query_clicked and st.session_state.current_query:
        col1, col2 = st.columns(2)
        
        with col2:
            st.subheader("ChatGPT生成的SQL:")
            with st.spinner("ChatGPT生成中..."):
                chatgpt_result = llm.generate_sql(st.session_state.current_query, db)
                st.session_state.sql_results = chatgpt_result
                
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
            
            # 创建日志容器
            log_container = st.empty()
            status_container = st.empty()
            
            with st.spinner("DeepSeek生成中..."):
                # 创建日志存储
                if 'log_messages' not in st.session_state:
                    st.session_state.log_messages = []
                
                # 定义日志处理函数
                def log_handler(message):
                    st.session_state.log_messages.append(message)
                    # 更新状态显示
                    if message.startswith('==='):
                        status_container.info(message)
                    elif 'SQL验证成功' in message:
                        status_container.success(message)
                    elif 'SQL执行失败' in message:
                        status_container.error(message)
                    # 更新日志显示
                    with log_container.container():
                        with st.expander("查看执行日志", expanded=False):
                            for msg in st.session_state.log_messages:
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
                
                # 清除之前的日志
                st.session_state.log_messages = []
                
                # 生成SQL并处理日志
                deepseek_result = llm._generate_sql_deepseek(st.session_state.system_prompt, 
                                                           st.session_state.current_query, 
                                                           db,
                                                           log_callback=log_handler)
                
                st.session_state.sql_results['deepseek'] = deepseek_result
                
                # 清除状态显示
                status_container.empty()
                
                # 显示最终SQL和结果
                if isinstance(deepseek_result, dict):
                    st.code(deepseek_result['sql'], language="sql")
                    st.info(f"生成耗时: {deepseek_result['time']:.2f}秒")
                    
                    # 如果SQL生成成功，直接执行并显示结果
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