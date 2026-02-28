import time
from datetime import datetime
from fetcher import OrderbookFetcher
from validator import OrderbookValidator
from db_loader import DuckDBLoader
from notifier import EmailNotifier # 导入新模块

# ⚡️ 阈值配置
ALERT_THRESHOLD = 0.8  # 绝对值大于 0.8 报警
COOLDOWN_SECONDS = 300 # 冷却时间 5 分钟 (300秒)

def run_pipeline():
    # 1. 实例化组件
    fetcher = OrderbookFetcher(symbol='BTC/USDT')
    validator = OrderbookValidator()
    loader = DuckDBLoader()
    notifier = EmailNotifier()
    
    # 状态变量：记录上一次报警的时间戳
    last_alert_time = 0
    
    print("🚀 监控管道启动 (With Alerting)...")
    
    try:
        while True:
            # --- Step 1: Extract ---
            raw_data = fetcher.fetch_data()
            
            # --- Step 2: Validate ---
            if validator.validate(raw_data):
                # --- Step 3: Load ---
                loader.save(raw_data)
                
                # --- Step 4: Calculate & Alert (核心逻辑) ---
                
                # 4.1 在 Python 侧直接计算 Imbalance (为了低延迟，不去查库了)
                bids = raw_data['bids']
                asks = raw_data['asks']
                bid_vol = sum(x[1] for x in bids)
                ask_vol = sum(x[1] for x in asks)
                
                # 防止分母为0
                total_vol = bid_vol + ask_vol
                if total_vol > 0:
                    imbalance = (bid_vol - ask_vol) / total_vol
                else:
                    imbalance = 0
                
                best_bid_price = bids[0][0]
                
                # 打印实时状态
                print(f"Update: {datetime.now().strftime('%H:%M:%S')} | Imbalance: {imbalance:.4f}")

                # 4.2 报警触发逻辑 (Check Trigger)
                # 条件 A: 失衡率绝对值超过阈值 (既看多也看空)
                # 条件 B: 当前时间 - 上次报警时间 > 冷却时间
                if abs(imbalance) > ALERT_THRESHOLD:
                    current_time = time.time()
                    
                    if current_time - last_alert_time > COOLDOWN_SECONDS:
                        print("🔥 触发阈值！正在发送报警...")
                        success = notifier.send_alert("BTC/USDT", imbalance, best_bid_price)
                        
                        if success:
                            # 更新冷却计时器
                            last_alert_time = current_time
                    else:
                        print(f"⏳ 报警冷却中... (剩余 {int(COOLDOWN_SECONDS - (current_time - last_alert_time))} 秒)")
                        
            else:
                print("🚫 脏数据丢弃")
                
            time.sleep(1) # 1秒轮询一次
            
    except KeyboardInterrupt:
        print("\n🛑 管道停止")
        loader.close()

if __name__ == "__main__":
    run_pipeline()