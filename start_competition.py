#!/usr/bin/env python3
"""
coffeegirl 比赛专用启动脚本
"""

import time
from datetime import datetime, timedelta
from main import CoffeeGirlTradingBot

def wait_until_competition_start():
    """等待比赛开始"""
    competition_start = datetime(2024, 11, 10, 20, 0, 0)
    now = datetime.now()
    
    if now < competition_start:
        wait_seconds = (competition_start - now).total_seconds()
        print(f"⏰ 比赛将于 {competition_start} 开始")
        print(f"🕒 还有 {wait_seconds:.0f} 秒 ({wait_seconds/3600:.1f} 小时)")
        
        while datetime.now() < competition_start:
            remaining = (competition_start - datetime.now()).total_seconds()
            print(f"\r⏳ 倒计时: {remaining:.0f}秒", end="", flush=True)
            time.sleep(1)
        
        print("\n🎯 比赛开始！启动 coffeegirl 交易机器人...")
    else:
        print("🎯 比赛已开始，立即启动机器人...")

if __name__ == "__main__":
    print("☕ coffeegirl 交易比赛 - 自动启动器")
    print("=" * 50)
    
    wait_until_competition_start()
    
    bot = CoffeeGirlTradingBot()
    bot.start()