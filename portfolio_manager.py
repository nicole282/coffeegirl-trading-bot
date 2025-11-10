from typing import Dict, List, Optional
from datetime import datetime
from config import Config

class PortfolioManager:
    """投资组合管理"""
    
    def __init__(self, config: Config, api):
        self.config = config
        self.api = api
        self.positions = {}  # symbol -> position_data
        self.portfolio_value = 0
        self.cash_balance = 0
        
    def update_portfolio(self, account_info: Dict):
        """更新投资组合信息"""
        if not account_info:
            return
            
        # 这里需要根据实际的API响应结构调整
        # 假设API返回格式: {"balances": [{"asset": "USDT", "free": "1000"}, ...]}
        balances = account_info.get("balances", [])
        
        # 计算现金余额（USDT）
        usdt_balance = next((float(b["free"]) for b in balances if b["asset"] == "USDT"), 0)
        self.cash_balance = usdt_balance
        
        # 更新持仓
        self.positions = {}
        for balance in balances:
            asset = balance["asset"]
            if asset != "USDT" and float(balance["free"]) > 0:
                symbol = f"{asset}USDT"
                self.positions[symbol] = {
                    "asset": asset,
                    "quantity": float(balance["free"]),
                    "entry_price": self.get_average_entry_price(symbol),
                    "current_value": 0
                }
        
        # 计算投资组合总价值
        self.calculate_portfolio_value()
    
    def calculate_portfolio_value(self):
        """计算投资组合总价值"""
        total_value = self.cash_balance
        
        for symbol, position in self.positions.items():
            current_price = self.api.get_ticker_price(symbol)
            if current_price > 0:
                position_value = position["quantity"] * current_price
                position["current_value"] = position_value
                position["current_price"] = current_price
                total_value += position_value
        
        self.portfolio_value = total_value
        return total_value
    
    def get_average_entry_price(self, symbol: str) -> float:
        """获取平均入场价格（简化实现）"""
        # 在实际应用中，这里应该从交易记录中计算平均成本
        # 这里返回当前价格作为简化
        return self.api.get_ticker_price(symbol) or 0
    
    def get_position(self, symbol: str) -> Optional[Dict]:
        """获取指定symbol的持仓"""
        return self.positions.get(symbol)
    
    def get_all_positions(self) -> Dict:
        """获取所有持仓"""
        return self.positions
    
    def can_open_position(self, symbol: str, position_size: float) -> bool:
        """检查是否可以开新仓"""
        # 检查是否已有该symbol的持仓
        if symbol in self.positions:
            return False
            
        # 检查仓位大小是否超过限制
        if position_size > self.portfolio_value * self.config.MAX_POSITION_SIZE:
            return False
            
        # 检查现金是否足够
        if position_size > self.cash_balance:
            return False
            
        return True
    
    def update_position(self, symbol: str, action: str, quantity: float, price: float):
        """更新持仓"""
        if action == "BUY":
            if symbol in self.positions:
                # 加仓 - 计算新的平均成本
                old_position = self.positions[symbol]
                total_quantity = old_position["quantity"] + quantity
                total_cost = (old_position["quantity"] * old_position["entry_price"] + 
                            quantity * price)
                new_avg_price = total_cost / total_quantity
                
                self.positions[symbol].update({
                    "quantity": total_quantity,
                    "entry_price": new_avg_price
                })
            else:
                # 新开仓
                self.positions[symbol] = {
                    "asset": symbol.replace("USDT", ""),
                    "quantity": quantity,
                    "entry_price": price,
                    "current_value": quantity * price
                }
                
            # 更新现金余额
            self.cash_balance -= quantity * price
            
        elif action == "SELL":
            if symbol in self.positions:
                position = self.positions[symbol]
                
                if quantity >= position["quantity"]:
                    # 平仓
                    del self.positions[symbol]
                else:
                    # 减仓
                    position["quantity"] -= quantity
                
                # 更新现金余额
                self.cash_balance += quantity * price
    
    def get_portfolio_summary(self) -> Dict:
        """获取投资组合摘要"""
        self.calculate_portfolio_value()
        
        position_count = len(self.positions)
        total_invested = sum(pos["quantity"] * pos["entry_price"] 
                           for pos in self.positions.values())
        
        return {
            "total_value": self.portfolio_value,
            "cash_balance": self.cash_balance,
            "invested_value": total_invested,
            "position_count": position_count,
            "cash_ratio": self.cash_balance / self.portfolio_value if self.portfolio_value > 0 else 1,
            "positions": self.positions
        }