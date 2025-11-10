import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from config import Config

class RiskManager:
    """高级风险管理引擎"""
    
    def __init__(self, config: Config):
        self.config = config
        self.trade_history = []
        self.performance_metrics = {
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "total_pnl": 0,
            "max_drawdown": 0,
            "current_drawdown": 0
        }
        self.peak_portfolio_value = 0
        
    def calculate_position_size(self, symbol: str, entry_price: float, 
                              stop_loss_price: float, portfolio_value: float) -> float:
        """基于风险的仓位计算"""
        
        # 计算单笔交易风险金额
        risk_amount = portfolio_value * self.config.MAX_PORTFOLIO_RISK
        
        # 计算每单位价格风险
        price_risk = abs(entry_price - stop_loss_price)
        if price_risk == 0:
            return 0
            
        # 计算基础仓位
        base_position = risk_amount / price_risk
        
        # 计算仓位价值
        position_value = base_position * entry_price
        
        # 应用最大仓位限制
        max_position_value = portfolio_value * self.config.MAX_POSITION_SIZE
        if position_value > max_position_value:
            base_position = max_position_value / entry_price
        
        return base_position
    
    def calculate_stop_loss_take_profit(self, entry_price: float, signal: str) -> Dict:
        """计算止损止盈价格"""
        if signal == "BUY":
            stop_loss = entry_price * (1 - self.config.STOP_LOSS_PCT)
            take_profit = entry_price * (1 + self.config.TAKE_PROFIT_PCT)
        elif signal == "SELL":
            stop_loss = entry_price * (1 + self.config.STOP_LOSS_PCT)
            take_profit = entry_price * (1 - self.config.TAKE_PROFIT_PCT)
        else:
            return {}
            
        return {
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "trailing_stop": entry_price * (1 - self.config.TRAILING_STOP_PCT) 
                            if signal == "BUY" else 
                            entry_price * (1 + self.config.TRAILING_STOP_PCT)
        }
    
    def should_exit_trade(self, position: Dict, current_price: float) -> Dict:
        """检查是否应该平仓"""
        if not position:
            return {"exit": False, "reason": ""}
            
        entry_price = position["entry_price"]
        signal = position["signal"]
        stop_loss = position.get("stop_loss")
        take_profit = position.get("take_profit")
        trailing_stop = position.get("trailing_stop")
        
        # 计算当前盈亏
        if signal == "BUY":
            pnl_pct = (current_price - entry_price) / entry_price
        else:  # SELL
            pnl_pct = (entry_price - current_price) / entry_price
        
        # 检查止损
        if stop_loss:
            if (signal == "BUY" and current_price <= stop_loss) or \
               (signal == "SELL" and current_price >= stop_loss):
                return {"exit": True, "reason": f"STOP_LOSS({pnl_pct:.2%})"}
        
        # 检查止盈
        if take_profit:
            if (signal == "BUY" and current_price >= take_profit) or \
               (signal == "SELL" and current_price <= take_profit):
                return {"exit": True, "reason": f"TAKE_PROFIT({pnl_pct:.2%})"}
        
        # 检查移动止损
        if trailing_stop and abs(pnl_pct) > 0.01:  # 至少有1%盈利才启动移动止损
            new_trailing_stop = current_price * (1 - self.config.TRAILING_STOP_PCT) \
                              if signal == "BUY" else \
                              current_price * (1 + self.config.TRAILING_STOP_PCT)
            
            # 更新移动止损（只向有利方向移动）
            if (signal == "BUY" and new_trailing_stop > trailing_stop) or \
               (signal == "SELL" and new_trailing_stop < trailing_stop):
                position["trailing_stop"] = new_trailing_stop
            
            # 检查移动止损触发
            if (signal == "BUY" and current_price <= position["trailing_stop"]) or \
               (signal == "SELL" and current_price >= position["trailing_stop"]):
                return {"exit": True, "reason": f"TRAILING_STOP({pnl_pct:.2%})"}
        
        return {"exit": False, "reason": ""}
    
    def check_trading_frequency(self) -> bool:
        """检查交易频率"""
        now = datetime.now()
        one_hour_ago = now - timedelta(hours=1)
        
        recent_trades = [t for t in self.trade_history 
                        if t.get("timestamp", now) > one_hour_ago]
        
        return len(recent_trades) < self.config.MAX_TRADES_PER_HOUR
    
    def check_cooldown_period(self) -> bool:
        """检查亏损后的冷却期"""
        if not self.trade_history:
            return True
            
        last_trade = self.trade_history[-1]
        if last_trade.get("pnl", 0) >= 0:
            return True
            
        trade_time = last_trade.get("timestamp", datetime.now())
        cooldown_end = trade_time + timedelta(seconds=self.config.COOLDOWN_AFTER_LOSS)
        
        return datetime.now() > cooldown_end
    
    def update_performance_metrics(self, portfolio_value: float):
        """更新性能指标"""
        if portfolio_value > self.peak_portfolio_value:
            self.peak_portfolio_value = portfolio_value
            self.performance_metrics["current_drawdown"] = 0
        else:
            self.performance_metrics["current_drawdown"] = \
                (self.peak_portfolio_value - portfolio_value) / self.peak_portfolio_value
            
        self.performance_metrics["max_drawdown"] = max(
            self.performance_metrics["max_drawdown"],
            self.performance_metrics["current_drawdown"]
        )
    
    def record_trade(self, trade_data: Dict):
        """记录交易"""
        trade_data["timestamp"] = datetime.now()
        self.trade_history.append(trade_data)
        
        # 更新统计
        self.performance_metrics["total_trades"] += 1
        pnl = trade_data.get("pnl", 0)
        self.performance_metrics["total_pnl"] += pnl
        
        if pnl > 0:
            self.performance_metrics["winning_trades"] += 1
        elif pnl < 0:
            self.performance_metrics["losing_trades"] += 1
    
    def get_trade_approval(self, symbol: str, signal: str, confidence: float, 
                          portfolio_value: float) -> Dict:
        """获取交易批准"""
        
        # 检查交易频率
        if not self.check_trading_frequency():
            return {"approved": False, "reason": "TRADING_FREQUENCY_LIMIT"}
        
        # 检查冷却期
        if not self.check_cooldown_period():
            return {"approved": False, "reason": "COOLDOWN_PERIOD"}
        
        # 检查信心度
        if confidence < self.config.ENTRY_CONFIDENCE:
            return {"approved": False, "reason": f"LOW_CONFIDENCE({confidence:.2f})"}
        
        # 检查回撤
        if self.performance_metrics["current_drawdown"] > 0.05:  # 5%回撤
            return {"approved": False, "reason": "HIGH_DRAWDOWN"}
        
        return {"approved": True, "reason": "APPROVED"}