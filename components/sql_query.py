import streamlit as st
import pandas as pd
from ui.examples import EXAMPLE_QUERIES

def render_sql_query(db):
    """渲染SQL查询界面"""
    # 示例查询选择
    example = st.selectbox(
        "选择示例查询",
        ["自定义查询"] + list(EXAMPLE_QUERIES.keys())
    )
    
    if example != "自定义查询":
        sql_input = st.text_area(
            "SQL查询:",
            value=EXAMPLE_QUERIES[example],
            height=150,
            key="sql_input"
        )
    else:
        sql_input = st.text_area(
            "SQL查询:",
            height=150,
            key="sql_input"
        )
    
    if st.button("执行SQL", key="sql"):
        if sql_input:
            with st.spinner("执行查询中..."):
                result = db.execute_query(sql_input)
                if isinstance(result, pd.DataFrame):
                    st.subheader("查询结果:")
                    st.dataframe(result)
                else:
                    st.error(f"查询错误: {result}")
        else:
            st.warning("请输入SQL查询") 