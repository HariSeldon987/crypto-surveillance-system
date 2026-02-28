code
Markdown
# 🦅 Bybit Real-time Market Surveillance System

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red.svg)
![DuckDB](https://img.shields.io/badge/Database-DuckDB-yellow.svg)

## 📖 项目简介 (Introduction)

这是一个面向加密货币衍生品市场的**实时风控监控系统**。
针对 Bybit BTC/USDT 交易对，系统能够实时采集 Orderbook（订单簿）深度数据，计算微观市场指标（如 Orderbook Imbalance, Spread），并在检测到异常波动时触发自动化报警。

**核心价值：** 帮助交易员和风控团队在毫秒级捕捉市场流动性失衡，识别潜在的盘口操纵或剧烈行情的先行信号。

## 🏗️ 系统架构 (Architecture)

本项目采用了 **ELT (Extract-Load-Transform)** 架构，实现了数据采集与分析的解耦。

```mermaid
graph LR
    A[Bybit API] -->|CCXT Fetcher| B(Python ETL Pipeline)
    B -->|Data Validation| C{Quality Check}
    C -->|Pass| D[(DuckDB OLAP)]
    C -->|Fail| E[Error Log]
    D -->|SQL Views| F[Streamlit Dashboard]
    B -->|Alert Trigger| G[Email Notification]
Extract: 使用 CCXT 库处理交易所 API 连接与限流（Rate Limiting）。
Validate: 基于 Pandas 实现向量化的数据完整性与业务逻辑校验（如 Bid < Ask）。
Load & Transform: 使用嵌入式列存数据库 DuckDB，通过 SQL View 实时计算失衡率指标。
Visualize: 使用 Streamlit 构建动态交互式看板。
🛠️ 技术栈 (Tech Stack)
编程语言: Python 3.9
数据采集: CCXT (处理 API 连接与重试)
数据存储: DuckDB (OLAP 场景下的高性能列式存储)
数据工程: Pandas (数据清洗), Python smtplib (报警)
前端可视化: Streamlit
🚀 快速开始 (Quick Start)
1. 安装依赖
code
Bash
git clone https://github.com/your-username/crypto_surveillance.git
cd crypto_surveillance
pip install -r requirements.txt
2. 配置环境
复制 .env.example 为 .env，并填入配置（可选）：
code
Ini
BYBIT_API_KEY=your_key
BYBIT_SECRET=your_secret
EMAIL_HOST_PASSWORD=your_smtp_password
3. 启动系统
本系统分为后端数据管道和前端看板，需在两个终端分别运行。
Terminal 1 (启动数据采集):
code
Bash
python src/pipeline.py
Terminal 2 (启动可视化看板):
code
Bash
streamlit run src/dashboard.py
📊 数据字典 (Data Dictionary)
核心指标计算逻辑如下：
字段名	类型	定义	计算逻辑 (SQL/Python)
bid_vol_top5	Float	买盘前5档总量	SUM(Qty) of Bids[0:5]
imbalance_ratio	Float	订单簿失衡率	(BidVol - AskVol) / (BidVol + AskVol)
spread	Float	买卖点差	BestAsk - BestBid
Imbalance > 0.8: 极度看多压力 (Buy Pressure)
Imbalance < -0.8: 极度看空压力 (Sell Pressure)
💡 工程亮点 (Engineering Highlights)
高并发处理: 解决了 DuckDB 在 Windows 下的文件锁冲突问题，实现了 Backend 写入与 Frontend 读取的并发共存。
鲁棒性设计:
Fetcher: 实现了自动重试与指数退避机制。
Validator: 实现了“隔离模式”，脏数据不入库，直接隔离记录。
模块化: 遵循 OOP 设计原则，将 Fetcher, Loader, Notifier 解耦，易于扩展更多交易所。
📞 联系方式
Author: 朱华鑫
Email: 13849708801@163.com