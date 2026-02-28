import logging
from typing import Dict, Any, Optional
from datetime import datetime

# 配置日志 (模拟生产环境日志格式)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [Validator] %(message)s'
)

class OrderbookValidator:
    """
    数据质检员 (Quality Assurance)
    职责：检查数据完整性、业务逻辑合理性 (Spread > 0)
    """
    
    def __init__(self, spread_threshold: float = 0):
        """
        :param spread_threshold: 最小点差阈值，通常为 0。
        """
        self.threshold = spread_threshold

    def validate(self, data: Optional[Dict[str, Any]]) -> bool:
        """
        主验证函数
        :param data: Fetcher 抓回来的原始字典
        :return: True (通过) / False (失败)
        """
        # 1. 完整性检查 (Completeness)
        # 防止 API 返回空数据或 None
        if not data:
            logging.warning("数据为空 (None)")
            return False
            
        required_keys = ['symbol', 'bids', 'asks', 'timestamp']
        if not all(key in data for key in required_keys):
            logging.error(f"数据结构缺失: {data.keys()}")
            return False

        # 防止空列表 (有Key但没数据)
        if not data['bids'] or not data['asks']:
            logging.warning(f"订单簿为空: {data['symbol']}")
            return False

        # 2. 业务逻辑检查 (Consistency) - 核心任务
        return self._check_crossed_market(data)

    def _check_crossed_market(self, data: Dict[str, Any]) -> bool:
        """
        检查是否存在盘口倒挂 (Bid >= Ask)
        """
        # 取出最优买卖价 (Best Bid / Best Ask)
        # 结构: [[price, qty], [price, qty]...]
        best_bid_price = float(data['bids'][0][0])
        best_ask_price = float(data['asks'][0][0])
        
        spread = best_ask_price - best_bid_price
        
        # 逻辑断言
        if spread <= self.threshold:
            # 🚨 严重错误：记录 Error Log
            logging.error(
                f"盘口倒挂警报! Symbol: {data['symbol']} | "
                f"Bid: {best_bid_price} >= Ask: {best_ask_price} | "
                f"Spread: {spread}"
            )
            return False
        
        # ✅ 通过验证
        # 在 Debug 模式下可以打印 Spread，生产环境通常不打印正常日志以节省空间
        # logging.info(f"Check Pass. Spread: {spread}")
        return True

if __name__ == "__main__":
    # --- 单元测试 ---
    validator = OrderbookValidator()
    
    # Case 1: 正常数据
    good_data = {
        'symbol': 'BTC/USDT', 'timestamp': '...',
        'bids': [[99, 1]], 'asks': [[100, 1]]
    }
    print(f"Case 1 (正常): {validator.validate(good_data)}")
    
    # Case 2: 倒挂数据 (脏数据)
    bad_data = {
        'symbol': 'BTC/USDT', 'timestamp': '...',
        'bids': [[101, 1]], 'asks': [[100, 1]] # 买价比卖价高
    }
    print(f"Case 2 (倒挂): {validator.validate(bad_data)}")