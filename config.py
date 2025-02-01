import os
import streamlit as st
from dotenv import load_dotenv

# 尝试加载本地.env文件
load_dotenv()

# 根据环境选择配置来源
try:
    # 尝试使用 Streamlit Secrets
    OLLAMA_BASE_URL = st.secrets["OLLAMA_BASE_URL"]
    DEEPSEEK_MODEL = st.secrets["DEEPSEEK_MODEL"]
    DB_TYPE = st.secrets["DB_TYPE"]
    DB_PATH = st.secrets["DB_PATH"]
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
    OPENAI_BASE_URL = st.secrets["OPENAI_BASE_URL"]
    OPENAI_MODEL = st.secrets["OPENAI_MODEL"]
except (FileNotFoundError, KeyError):
    # 如果不是在 Streamlit Cloud 环境，使用环境变量
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL")
    DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL")
    DB_TYPE = os.getenv("DB_TYPE")
    DB_PATH = os.getenv("DB_PATH")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL")

# 确保data目录存在
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True) 