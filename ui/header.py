import streamlit as st

def render_header(llm):
    """渲染页面头部信息"""
    # 创建三列布局
    col1, col2, col3 = st.columns([2,2,1])
    
    # 检查模型状态
    is_healthy = llm.check_health()
    model_info = llm.get_model_info()
    
    # 定义字体样式
    style = "font-size: 16px; margin: 0; padding: 0;"
    
    with col1:
        status_color = "🟢" if is_healthy else "🔴"
        st.markdown(f'<p style="{style}">{status_color} 模型服务状态: {"正常" if is_healthy else "异常"}</p>', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'<p style="{style}">🤖 模型: {model_info["name"]}</p>', unsafe_allow_html=True)
    
    with col3:
        st.markdown(f'<p style="{style}">👨‍💻 Developer by Huaiyuan Tan</p>', unsafe_allow_html=True)
    
    # 添加分隔线
    st.markdown("---") 