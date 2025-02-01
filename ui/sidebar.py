import streamlit as st

def show_database_status(test_results):
    """显示数据库状态"""
    st.sidebar.write("数据库状态：")
    st.sidebar.write(test_results)

def show_schema_info():
    """显示数据库表结构信息"""
    with st.sidebar:
        with st.expander("查看数据表结构", expanded=True):
            st.code("""
            1. DEPT (部门表)
               - DEPTNO: INTEGER PRIMARY KEY (部门编号)
               - DNAME: TEXT (部门名称)
               - LOC: TEXT (位置)
            
            2. EMP (员工表)
               - EMPNO: INTEGER PRIMARY KEY (员工编号)
               - ENAME: TEXT (员工姓名)
               - JOB: TEXT (职位)
               - MGR: INTEGER (上级编号)
               - HIREDATE: DATE (入职日期)
               - SAL: DECIMAL (薪资)
               - COMM: DECIMAL (提成)
               - DEPTNO: INTEGER (部门编号)
            
            3. SALGRADE (薪资等级表)
               - GRADE: INTEGER PRIMARY KEY (等级)
               - LOSAL: DECIMAL (最低工资)
               - HISAL: DECIMAL (最高工资)
            
            4. BONUS (奖金表)
               - ENAME: TEXT (员工姓名)
               - JOB: TEXT (职位)
               - SAL: DECIMAL (薪资)
               - COMM: DECIMAL (奖金)
            """)

def show_history_questions(history_db):
    """显示历史问题"""
    with st.sidebar:
        with st.expander("历史问题", expanded=False):
            questions = history_db.get_questions()
            if questions:
                for id, question in questions:
                    if st.button(f"📝 {question[:50]}...", key=f"q_{id}"):
                        st.session_state.reuse_question = question
                        st.rerun()
            else:
                st.info("暂无历史问题") 