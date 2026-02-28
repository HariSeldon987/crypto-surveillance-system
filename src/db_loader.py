import duckdb
from typing import Dict, Any

class DuckDBLoader:
    def __init__(self, db_path: str = 'data/market_data.db'):
        self.db_path = db_path
        # 初始化时建表
        self._init_schema()

    def _get_conn(self):
        """获取一个临时连接"""
        return duckdb.connect(self.db_path, read_only=False)

    def _init_schema(self):
        con = self._get_conn()
        try:
            con.execute("""
                CREATE TABLE IF NOT EXISTS orderbook_snapshots (
                    symbol VARCHAR,
                    timestamp TIMESTAMP,
                    bid_vol_top5 DOUBLE,
                    ask_vol_top5 DOUBLE,
                    best_bid DOUBLE,
                    best_ask DOUBLE
                )
            """)
            con.execute("""
                CREATE OR REPLACE VIEW view_market_pressure AS
                SELECT 
                    symbol,
                    timestamp,
                    bid_vol_top5,
                    ask_vol_top5,
                    best_bid,
                    (bid_vol_top5 - ask_vol_top5) / NULLIF((bid_vol_top5 + ask_vol_top5), 0) AS imbalance_ratio,
                    (best_ask - best_bid) AS spread
                FROM orderbook_snapshots
            """)
        finally:
            # ⚡️ 关键：无论成功失败，必须关闭连接！
            con.close()

    def save(self, data: Dict[str, Any]):
        total_bid_vol = sum(item[1] for item in data['bids'])
        total_ask_vol = sum(item[1] for item in data['asks'])
        best_bid = data['bids'][0][0]
        best_ask = data['asks'][0][0]
        
        # ⚡️ 关键：写入时才打开，写完立马关
        con = self._get_conn()
        try:
            con.execute("""
                INSERT INTO orderbook_snapshots VALUES (?, ?, ?, ?, ?, ?)
            """, (
                data['symbol'],
                data['timestamp'],
                total_bid_vol,
                total_ask_vol,
                best_bid,
                best_ask
            ))
            print(f"💾 [DB] 数据已写入并释放锁")
        except Exception as e:
            print(f"❌ 写入失败: {e}")
        finally:
            con.close() # <--- 这里释放了文件锁，Streamlit 才有机会读取

    def close(self):
        pass