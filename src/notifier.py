import smtplib
from email.mime.text import MIMEText
from email.header import Header
import logging

# 配置区域 (和之前一样，建议放入 .env)
MAIL_HOST = "smtp.163.com"
MAIL_USER = "13849708801@163.com"
MAIL_PASS = "BKrkSHPsNYZ6y3ah" # ⚠️ 填授权码
RECEIVER  = "13849708801@163.com"

class EmailNotifier:
    def __init__(self):
        self.host = MAIL_HOST
        self.user = MAIL_USER
        self.password = MAIL_PASS
        self.port = 465 # SSL 端口

    def send_alert(self, symbol: str, imbalance: float, price: float):
        """
        发送高优报警邮件
        """
        # 判断方向
        direction = "🚀 极度看多 (Buy)" if imbalance > 0 else "📉 极度看空 (Sell)"
        
        subject = f"🚨 【风控警报】{symbol} 出现失衡！Imbalance: {imbalance:.2f}"
        
        content = f"""
        监控对象: {symbol}
        当前价格: ${price}
        --------------------------------
        失衡指标: {imbalance:.4f}
        市场状态: {direction}
        --------------------------------
        请立即检查盘口或执行策略！
        """
        
        message = MIMEText(content, 'plain', 'utf-8')
        message['From'] = Header("Bybit哨兵", 'utf-8')
        message['To'] =  Header("分析师", 'utf-8')
        message['Subject'] = Header(subject, 'utf-8')

        try:
            # 使用 SSL 连接
            smtp = smtplib.SMTP_SSL(self.host, self.port)
            smtp.login(self.user, self.password)
            smtp.sendmail(self.user, [RECEIVER], message.as_string())
            smtp.quit()
            logging.info(f"📧 报警邮件已发送: {subject}")
            return True
        except Exception as e:
            logging.error(f"❌ 邮件发送失败: {e}")
            return False

if __name__ == "__main__":
    # 单元测试
    notifier = EmailNotifier()
    notifier.send_alert("BTC/USDT", 0.85, 65000.0)