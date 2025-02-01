import streamlit as st
import pandas as pd
from config import DB_PATH, OLLAMA_BASE_URL, DEEPSEEK_MODEL, OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL
from utils.db import Database
from utils.llm import LLMClient
from utils.history_db import HistoryDB
from ui.sidebar import show_database_status, show_schema_info, show_history_questions
from ui.header import render_header
from components.natural_language import render_natural_language_query
from components.sql_query import render_sql_query
from components.chat import render_chat
from components.chatgpt_chat import render_chatgpt_chat

# 初始化数据库和LLM客户端
db = Database(DB_PATH)
llm = LLMClient(
    base_url=OLLAMA_BASE_URL,
    model=DEEPSEEK_MODEL,
    openai_key=OPENAI_API_KEY,
    openai_base_url=OPENAI_BASE_URL,
    openai_model=OPENAI_MODEL
)
history_db = HistoryDB(DB_PATH)

# 渲染页面头部
render_header(llm)

# Streamlit界面
st.title("自然语言转SQL工具")

# 显示数据库状态
test_results = db.test_db()
show_database_status(test_results)

# 显示表结构信息
show_schema_info()

# 显示历史问题
show_history_questions(history_db)

# 创建四个标签页
tab1, tab2, tab3, tab4 = st.tabs(["自然语言查询数据库", "SQL查询", "DeepSeek对话", "ChatGPT对话"])

# Tab 1: 自然语言查询
with tab1:
    render_natural_language_query(llm, db, history_db)

# Tab 2: SQL查询
with tab2:
    render_sql_query(db)

# Tab 3: 大模型对话
with tab3:
    render_chat(llm)

# Tab 4: ChatGPT对话
with tab4:
    render_chatgpt_chat(llm) 