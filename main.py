#!/usr/bin/env python3
"""
coffeegirl 交易机器人主程序
"""

import time
import schedule
from datetime import datetime
from config import Config
from exchange_api import RoostooAPI
from enhanced_strategy import EnhancedStrategy

class CoffeeGirlTradingBot:
    """coffeegirl 交易机器人"""
    
    def __init__(self):
        self.config = Config()
        self.api = RoostooAPI(self.config)
        self.strategy_engine = EnhancedStrategy(self.config, self.api)
        self.is_running = True
        self.cycle_count = 0
        
        print("=" * 60)
        print("☕ coffeegirl 交易机器人初始化完成")
        print("=" * 60)
        
    def print_banner(self):
        """打印启动横幅"""
        banner = """
        ╔══════════════════════════════════════════════╗
        ║               ☕ coffeegirl ☕                ║
        ║                                              ║
        ║        · 智能交易 · 风险控制 · 稳定收益 ·     ║
        ║                                              ╕
        ╚══════════════════════════════════════════════╝
        """
        print(banner)
        
    def print_status(self, result: dict):
        """打印状态信息"""
        self.cycle_count += 1
        
        print(f"\n☕ 交易周期 #{self.cycle_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 50)
        
        status = result.get("status", "UNKNOWN")
        action = result.get("action", "HOLD")
        symbol = result.get("symbol", "")
        enhanced_confidence = result.get("enhanced_confidence", 0)
        
        status_icons = {"success": "✅", "error": "❌", "rejected": "⚠️"}
        action_icons = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}
        
        icon = status_icons.get(status, "🔵")
        action_icon = action_icons.get(action, "⚪")
        
        print(f"{icon} 状态: {status} | {action_icon} 操作: {action}")
        
        if symbol:
            print(f"📊 标的: {symbol}")
        if enhanced_confidence > 0:
            print(f"💪 信心度: {enhanced_confidence:.2f}")
        
        # 获取策略状态
        strategy_status = self.strategy_engine.get_strategy_status()
        portfolio = strategy_status["portfolio"]
        performance = strategy_status["performance"]
        
        print(f"💰 投资组合总值: ${portfolio['total_value']:,.2f}")
        print(f"💵 现金余额: ${portfolio['cash_balance']:,.2f}")
        print(f"📈 持仓数量: {portfolio['position_count']}")
        
        if performance["total_trades"] > 0:
            win_rate = (performance["winning_trades"] / performance["total_trades"]) * 100
            print(f"🎯 总交易: {performance['total_trades']} | 胜率: {win_rate:.1f}%")
            print(f"📉 当前回撤: {performance['current_drawdown']:.2%}")
        
        print("-" * 50)
    
    def run_trading_cycle(self):
        """运行交易周期"""
        try:
            result = self.strategy_engine.execute_enhanced_trading_cycle()
            self.print_status(result)
            
        except Exception as e:
            print(f"❌ 交易周期执行异常: {e}")
            import traceback
            traceback.print_exc()
    
    def start(self):
        """启动机器人"""
        self.print_banner()
        
        print("🚀 启动参数:")
        print(f"   • 交易对: {', '.join(self.config.SYMBOLS)}")
        print(f"   • 数据源: Roostoo + Horus")
        print(f"   • 执行间隔: {self.config.EXECUTION_INTERVAL}秒")
        print(f"   • 团队: {self.config.TEAM_NAME}")
        print()
        
        # 立即执行一次初始分析
        print("🔍 执行初始分析...")
        self.run_trading_cycle()
        
        # 设置定时执行
        schedule.every(self.config.EXECUTION_INTERVAL).seconds.do(self.run_trading_cycle)
        
        print(f"\n⏰ 定时任务已启动，每 {self.config.EXECUTION_INTERVAL} 秒执行一次")
        print("💡 按 Ctrl+C 停止机器人")
        print("=" * 60)
        
        try:
            while self.is_running:
                schedule.run_pending()
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n\n🛑 收到停止信号...")
        except Exception as e:
            print(f"\n\n❌ 发生错误: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """停止机器人"""
        self.is_running = False
        print("✅ coffeegirl 交易机器人已安全停止")

if __name__ == "__main__":
    bot = CoffeeGirlTradingBot()
    bot.start()