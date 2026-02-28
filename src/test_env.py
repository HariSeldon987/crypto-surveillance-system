import ccxt
import duckdb
import pandas as pd
import time

print("🚀 开始环境自检...\n")

# --- 1. 测试 CCXT 连接 Bybit ---
print("1️⃣ 测试 CCXT (连接 Bybit)...")
try:
    # 实例化 Bybit 接口 (不需要 Key 也能查公开行情)
    exchange = ccxt.bybit()
    # 获取 BTC/USDT 的最新 ticker
    ticker = exchange.fetch_ticker('BTC/USDT')
    print(f"   ✅ 连接成功! BTC 当前价格: ${ticker['last']}")
except Exception as e:
    print(f"   ❌ CCXT 失败: {e}")

# --- 2. 测试 DuckDB 读写 ---
print("\n2️⃣ 测试 DuckDB (内存模式)...")
try:
    # 创建内存数据库
    con = duckdb.connect(database=':memory:')
    # 造点数据
    df = pd.DataFrame({'id': [1, 2, 3], 'value': [100, 200, 300]})
    # 直接查询 Pandas DataFrame (DuckDB 的黑魔法)
    res = con.execute("SELECT AVG(value) FROM df").fetchone()
    print(f"   ✅ SQL 执行成功! 平均值: {res[0]}")
except Exception as e:
    print(f"   ❌ DuckDB 失败: {e}")

print("\n🎉 环境自检完成！")