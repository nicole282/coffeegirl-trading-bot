from typing import Dict, List, Optional
from datetime import datetime
from config import Config

class PortfolioManager:
    """投资组合管理 - 修复版"""

    def __init__(self, config: Config, api):
        self.config = config
        self.api = api
        self.positions = {}
        self.portfolio_value = 0
        self.cash_balance = 50000  # 直接设置初始余额 $50,000
        self.initial_balance = 50000


    def update_portfolio(self, account_info: Dict):
        """更新投资组合信息 - 修复版"""
        if not account_info:
            print("❌ 账户信息为空")
            return

        # 根据调试结果，Roostoo API返回的是SpotWallet字段
        if account_info.get("Success"):
            # 尝试从SpotWallet获取余额
            spot_wallet = account_info.get("SpotWallet", {})

            # 查找USD余额
            usd_balance = 0
            if "USD" in spot_wallet:
                usd_balance = float(spot_wallet["USD"].get("Free", 0))
                print(f"✅ 从SpotWallet获取USD余额: ${usd_balance:,.2f}")

            # 如果SpotWallet没有，尝试旧的Wallet字段
            if usd_balance == 0:
                wallet_data = account_info.get("Wallet", {})
                for asset, balance_info in wallet_data.items():
                    if asset == "USD":
                        usd_balance = float(balance_info.get("Free", 0))
                        print(f"✅ 从Wallet获取USD余额: ${usd_balance:,.2f}")
                        break

            self.cash_balance = usd_balance if usd_balance > 0 else self.initial_balance

            # 更新持仓
            self.positions = {}

            # 从SpotWallet获取持仓
            for asset, balance_info in spot_wallet.items():
                if asset != "USD" and float(balance_info.get("Free", 0)) >0:
                    symbol = f"{asset}USDT"
                    free_balance = float(balance_info.get("Free", 0))

                    self.positions[symbol] = {
                        "asset": asset,
                        "quantity": free_balance,
                        "entry_price": self.get_average_entry_price(symbol),
                        "current_value": 0
                    }
                    print(f"📈 发现持仓 {symbol}: {free_balance}")

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
        print(f"📊 投资组合总值: ${self.portfolio_value:,.2f}")
        return total_value

    def get_average_entry_price(self, symbol: str) -> float:
        """获取平均入场价格"""
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
            cost = quantity * price

            if symbol in self.positions:
                # 加仓 - 计算新的平均成本
                old_position = self.positions[symbol]
                total_quantity = old_position["quantity"] + quantity
                total_cost = (old_position["quantity"] * old_position["entry_price"] + cost)
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
                    "current_value": cost
                }

            # 更新现金余额
            self.cash_balance -= cost
            print(f"💸 买入支出: ${cost:,.2f}, 剩余现金: ${self.cash_balance:,.2f}")

        elif action == "SELL":
            if symbol in self.positions:
                position = self.positions[symbol]
                revenue = quantity * price

                if quantity >= position["quantity"]:
                    # 平仓
                    del self.positions[symbol]
                else:
                    # 减仓
                    position["quantity"] -= quantity

                # 更新现金余额
                self.cash_balance += revenue
                print(f"💵 卖出收入: ${revenue:,.2f}, 剩余现金: ${self.cash_balance:,.2f}")

    def get_portfolio_summary(self) -> Dict:
        """获取投资组合摘要"""
        self.calculate_portfolio_value()

        position_count = len(self.positions)
        total_invested = sum(pos["quantity"] * pos["entry_price"] for pos in self.positions.values())

        return {
            "total_value": self.portfolio_value,
            "cash_balance": self.cash_balance,
            "invested_value": total_invested,
            "position_count": position_count,
            "cash_ratio": self.cash_balance / self.portfolio_value if self.portfolio_value > 0 else 1,
            "positions": self.positions
        }
