import ccxt
import time
from typing import Dict, Any, Optional
from datetime import datetime

class OrderbookFetcher:
    """
    交易所订单簿采集器 (Producer)
    职责：连接交易所，获取实时深度数据，处理网络异常。
    """

    def __init__(self, symbol: str = 'BTC/USDT', exchange_id: str = 'bybit'):
        """
        初始化采集器
        :param symbol: 交易对，例如 'BTC/USDT'
        :param exchange_id: 交易所 ID，默认 'bybit'
        """
        self.symbol = symbol
        self.exchange_id = exchange_id
        
        # 1. 动态加载交易所实例 (CS 反射思维)
        # ccxt.bybit(), ccxt.binance() ...
        if not hasattr(ccxt, exchange_id):
            raise ValueError(f"不支持的交易所: {exchange_id}")
        
        self.exchange = getattr(ccxt, exchange_id)({
            'enableRateLimit': True,  # ⚡️ 核心：自动处理 API 限流 (Leaky Bucket 算法)
            'timeout': 10000          # 10秒超时
        })
        
        print(f"🚀 [{exchange_id.upper()}] Fetcher 初始化完成. Target: {symbol}")

    def fetch_data(self) -> Optional[Dict[str, Any]]:
        """
        核心方法：抓取一次 Snapshot
        :return: 清洗后的字典数据 OR None (如果失败)
        """
        try:
            # 2. 发送请求 (IO Bound)
            # limit=5 代表只抓前5档 (买1-买5，卖1-卖5)，对于监控买卖压力足够了，且速度最快
            orderbook = self.exchange.fetch_order_book(self.symbol, limit=5)
            
            # 3. 基础清洗 (Extract)
            # CCXT 返回的标准结构: {'bids': [[price, qty], ...], 'asks': ...}
            timestamp = datetime.now()
            
            # CS 视角：我们需要计算 Latency (API返回时间 - 本地时间)
            # 但这里简单起见，我们只记录本地接收时间
            data_payload = {
                'exchange': self.exchange_id,
                'symbol': self.symbol,
                'timestamp': timestamp,
                'bids': orderbook['bids'], # 买单队列 [[价格, 数量], ...]
                'asks': orderbook['asks'], # 卖单队列
                'latency_ms': self.exchange.last_response_headers.get('X-Response-Time', 0) # 尝试获取服务端耗时
            }
            
            return data_payload

        except ccxt.NetworkError as e:
            print(f"⚠️ 网络错误: {e}")
        except ccxt.ExchangeError as e:
            print(f"❌ 交易所错误 (检查 Symbol?): {e}")
        except Exception as e:
            print(f"👻 未知错误: {e}")
            
        return None

# --- 单元测试 (Unit Test) ---
# 只有直接运行此文件时才会执行 (Entry Point Protection)
if __name__ == "__main__":
    # 实例化
    fetcher = OrderbookFetcher(symbol='BTC/USDT')
    
    print("开始连续抓取测试 (按 Ctrl+C 停止)...")
    try:
        while True:
            data = fetcher.fetch_data()
            if data:
                # 打印最优买一和卖一 (Best Bid/Ask)
                best_bid = data['bids'][0]
                best_ask = data['asks'][0]
                print(f"[{data['timestamp']}] "
                      f"买一: {best_bid[0]} ({best_bid[1]}) | "
                      f"卖一: {best_ask[0]} ({best_ask[1]})")
            
            time.sleep(1) # 模拟 1秒 1次 的频率
            
    except KeyboardInterrupt:
        print("\n🛑 测试停止")