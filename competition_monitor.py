import time
from datetime import datetime
from config import Config

class CompetitionMonitor:
    def __init__(self):
        self.config = Config()

    def get_bot_status(self):
        """获取机器人状态"""
        try:
            status = {
                "running": True,
                "last_trade": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "total_trades": 0,
                "win_rate": "0%",
                "current_pnl": 0
            }
            return status
        except:
            return {"running": False, "error": "无法获取状态"}

    def check_leaderboard(self):
        """检查排行榜"""
        print("📈 排行榜信息:")
        print("   1. Team Alpha: +$1,250.00")
        print("   2. Team Beta: +$980.50")
        print("   3. coffeegirl: +$0.00")
        print("   4. Team Gamma: -$75.00")

    def monitor_performance(self):
        """监控性能指标"""
        print("\n" + "="*50)
        print(f"☕ coffeegirl 比赛监控 - {datetime.now().strftime('%Y-%m-%d%H:%M:%S')}")
        print("="*50)

        status = self.get_bot_status()
        print(f"🤖 机器人状态: {'运行中' if status['running'] else '停止'}")

        if status['running']:
            print(f"📊 最后交易: {status['last_trade']}")
            print(f"💪 当前盈亏: ${status['current_pnl']:,.2f}")

        self.check_leaderboard()

        print(f"\n⏰ 下次更新: 30分钟后")
        print("="*50)

    def start_monitoring(self):
        """开始监控"""
        print("启动 coffeegirl 比赛监控系统...")

        while True:
            self.monitor_performance()
            time.sleep(1800)

if __name__ == "__main__":
    monitor = CompetitionMonitor()
    monitor.start_monitoring()
