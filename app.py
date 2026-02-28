import streamlit as st
import pandas as pd
import numpy as np

st.title("🦅 交易所实时监控系统 v0.1")

st.write("这是你的第一个 Streamlit 页面。")

# 模拟一个图表
chart_data = pd.DataFrame(
    np.random.randn(20, 3),
    columns=['a', 'b', 'c'])

st.line_chart(chart_data)

st.success("前端环境配置成功！")