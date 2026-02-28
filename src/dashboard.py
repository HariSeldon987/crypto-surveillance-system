import streamlit as st
import duckdb
import pandas as pd
import time

# --- 1. 页面配置 ---
st.set_page_config(
    page_title="Bybit 实时风控看板",
    page_icon="🦅",
    layout="wide"
)

# --- 2. 侧边栏配置 ---
st.sidebar.title("控制台")
refresh_rate = st.sidebar.slider("刷新频率 (秒)", 1, 10, 1) # 调快一点，1秒刷新
history_window = st.sidebar.selectbox("时间窗口", ["1 Minute", "5 Minutes", "1 Hour"], index=1)

# SQL Limit 映射
limit_map = {"1 Minute": 60, "5 Minutes": 300, "1 Hour": 3600}
limit_rows = limit_map[history_window]

# --- 3. 核心函数：带重试机制的数据读取 ---
def fetch_data_with_retry(limit):
    """
    尝试连接 DuckDB 并读取数据。
    解决 Windows 文件锁问题：如果遇到锁死，休息 0.1s 重试，最多 5 次。
    """
    db_path = 'data/market_data.db'
    max_retries = 5
    
    for i in range(max_retries):
        try:
            # 建立短连接 (Read Only)
            con = duckdb.connect(db_path, read_only=True)
            
            # 执行查询
            query = f"""
                SELECT * FROM view_market_pressure 
                ORDER BY timestamp DESC 
                LIMIT {limit}
            """
            df = con.execute(query).df()
            
            # ⚡️ 关键：查完立刻关闭释放锁
            con.close()
            return df
            
        except Exception as e:
            # 捕获 IO Error (文件被占用)
            if "IO Error" in str(e) or "Could not set lock" in str(e):
                time.sleep(0.1) # 避让策略：退避 0.1秒
                continue
            else:
                st.error(f"❌ 数据库查询错误: {e}")
                return pd.DataFrame()
    
    # 如果重试 5 次都失败
    return pd.DataFrame()

# --- 4. 主界面布局 ---
st.title("🦅 Bybit 实时异常监控系统 (Real-time Surveillance)")

# 创建占位符容器 (用于动态刷新)
placeholder = st.empty()

# --- 5. 实时刷新循环 (The Event Loop) ---
while True:
    with placeholder.container():
        # A. 获取数据 (使用重试机制)
        df = fetch_data_with_retry(limit_rows)

        if not df.empty:
            # 数据预处理：把时间轴正过来画图
            chart_df = df.sort_values("timestamp")
            
            # 取最新的一行数据作为“当前状态”
            latest = df.iloc[0]
            
            # B. 核心指标卡片 (Metrics)
            kpi1, kpi2, kpi3 = st.columns(3)
            
            # 价格
            kpi1.metric(
                label="BTC Best Bid", 
                value=f"${latest['best_bid']:,.2f}"
            )
            
            # 失衡率
            imb = latest['imbalance_ratio']
            kpi2.metric(
                label="Orderbook Imbalance", 
                value=f"{imb:.4f}",
                delta="偏多压力" if imb > 0 else "偏空压力",
                delta_color="normal"
            )
            
            # Spread
            spread = latest['spread']
            kpi3.metric(
                label="Spread (点差)", 
                value=f"{spread:.2f}",
                delta="正常" if spread > 0 else "倒挂异常",
                delta_color="inverse"
            )

            # C. 绘制曲线图 (Charts)
            tab1, tab2 = st.tabs(["Imbalance 趋势", "买卖深度对比"])
            
            with tab1:
                st.line_chart(chart_df, x="timestamp", y="imbalance_ratio")
                
            with tab2:
                # 绿色代表买盘，红色代表卖盘
                st.area_chart(chart_df, x="timestamp", y=["bid_vol_top5", "ask_vol_top5"], color=["#00ff00", "#ff0000"])

            # D. 原始数据表格
            with st.expander("查看原始数据日志"):
                st.dataframe(df)
        
        else:
            # 数据库暂时没数据，或者被锁住了读不到
            st.warning("⏳ 等待数据写入 / 数据库忙...")

    # 控制刷新频率
    time.sleep(refresh_rate)