import os
import streamlit as st
from dotenv import load_dotenv

# 尝试加载本地.env文件
load_dotenv()

# 优先使用 Streamlit Secrets，如果不存在则使用环境变量
OLLAMA_BASE_URL = st.secrets.get("OLLAMA_BASE_URL", os.getenv("OLLAMA_BASE_URL"))
DEEPSEEK_MODEL = st.secrets.get("DEEPSEEK_MODEL", os.getenv("DEEPSEEK_MODEL"))
DB_TYPE = st.secrets.get("DB_TYPE", os.getenv("DB_TYPE"))
DB_PATH = st.secrets.get("DB_PATH", os.getenv("DB_PATH"))
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
OPENAI_BASE_URL = st.secrets.get("OPENAI_BASE_URL", os.getenv("OPENAI_BASE_URL"))
OPENAI_MODEL = st.secrets.get("OPENAI_MODEL", os.getenv("OPENAI_MODEL"))

# 确保data目录存在
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True) 