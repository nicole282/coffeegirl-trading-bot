from typing import Dict, List, Optional
from datetime import datetime
import requests
from config import Config
from exchange_api import RoostooAPI
from technical_analyzer import TechnicalAnalyzer
from risk_manager import RiskManager
from portfolio_manager import PortfolioManager

class StrategyEngine:
    """coffeegirl 策略引擎 - 集成链上数据版本"""

    def __init__(self, config: Config, api: RoostooAPI):
        self.config = config
        self.api = api
        self.technical_analyzer = TechnicalAnalyzer(config)
        self.risk_manager = RiskManager(config)
        self.portfolio_manager = PortfolioManager(config, api)
        self.no_trade_count = 0
        self.daily_trade_count = 0
        self.last_trade_date = None
        self.horus_api_key = "b0f507665085984b9c0b3b1f79d672825f07fe8caae37f3d3f1fb18d86e0a70a"
        self.horus_base_url = "https://api.horus.com"

    def get_horus_chain_data(self) -> Dict:
        }   "active_strategies": ["4H_TREND_WITH_CHAIN_DATA"]config.MAX_TRA
>
sh: warning: here-document at line 7 delimited by end-of-file (wanted `EOF')
sh-5.2$ vim strategy_engine.py
sh-5.2$ tmux
[detached (from session 18)]
sh-5.2$ cat strategy_engine.py
"""
coffeegirl 策略引擎 - 集成Horus链上数据版本
"""

from typing import Dict, List, Optional
from datetime import datetime
import requests
from config import Config
from exchange_api import RoostooAPI
from technical_analyzer import TechnicalAnalyzer
from risk_manager import RiskManager
from portfolio_manager import PortfolioManager

class StrategyEngine:
    """coffeegirl 策略引擎 - 集成链上数据版本"""

    def __init__(self, config: Config, api: RoostooAPI):
        self.config = config
        self.api = api
        self.technical_analyzer = TechnicalAnalyzer(config)
        self.risk_manager = RiskManager(config)
        self.portfolio_manager = PortfolioManager(config, api)
        self.no_trade_count = 0
        self.daily_trade_count = 0
        self.last_trade_date = None
        self.horus_api_key = "b0f507665085984b9c0b3b1f79d672825f07fe8caae37f3d3f1fb18d86e0a70a"
        self.horus_base_url = "https://api.horus.com"

    def get_horus_chain_data(self) -> Dict:
        """获取Horus链上数据"""
        try:
            headers = {"X-API-Key": self.horus_api_key}

            # 获取鲸鱼净流入数据
            whale_flow_response = requests.get(
                f"{self.horus_base_url}/addresses/whale_net_flow",
                headers=headers,
                params={"chain": "bitcoin", "interval": "1d"},
                timeout=10
            )

            # 获取鲸鱼活跃度数据
            whale_count_response = requests.get(
                f"{self.horus_base_url}/addresses/whale_inflow_count",
                headers=headers,
                params={"chain": "bitcoin", "interval": "1d"},
                timeout=10
            )

            # 获取矿工数据
            mining_response = requests.get(
                f"{self.horus_base_url}/blockchain/mining_work",
                headers=headers,
                params={"chain": "bitcoin", "interval": "1d"},
                timeout=10
            )

            whale_flow = whale_flow_response.json() if whale_flow_response.status_code == 200 else []
            whale_count = whale_count_response.json() if whale_count_response.status_code == 200 else []
            mining_data = mining_response.json() if mining_response.status_code == 200 else []

            return {
                "whale_flow": whale_flow,
                "whale_count": whale_count,
                "mining_data": mining_data,
                "success": True
            }

        except Exception as e:
            print(f"❌ Horus API错误: {e}")
            return {"success": False, "error": str(e)}

    def analyze_chain_signals(self, symbol: str) -> Dict:
        """分析链上数据信号"""
        chain_data = self.get_horus_chain_data()

        if not chain_data["success"]:
            return {"signal": "HOLD", "confidence": 0, "reason": "CHAIN_DATA_UNAVAILABLE"}

        whale_flow = chain_data.get("whale_flow", [])
        whale_count = chain_data.get("whale_count", [])
        mining_data = chain_data.get("mining_data", [])

        # 分析最近3天鲸鱼行为
        if len(whale_flow) >= 3 and len(whale_count) >= 3:
            recent_flow = whale_flow[-3:]
            recent_count = whale_count[-3:]

            # 计算鲸鱼积累信号
            whale_accumulating = all(day.get('whale_net_flow', 0) > 0 for day in recent_flow)
            active_whales = sum(day.get('whale_inflow_count', 0) for day in recent_count)

            # 分析矿工压力
            mining_pressure = False
            if len(mining_data) >= 5:
                current_work = mining_data[-1].get('work_zh', 0)
                previous_work = mining_data[-4].get('work_zh', 0)
                mining_pressure = current_work > previous_work * 1.1  # 挖矿难度增加10%

            print(f"🔗 {symbol} 链上分析:")
            print(f"   鲸鱼积累: {'是' if whale_accumulating else '否'}")
            print(f"   活跃鲸鱼: {active_whales}")
            print(f"   矿工压力: {'是' if mining_pressure else '否'}")

            # 生成链上信号
            if whale_accumulating and active_whales > 100 and not mining_pressure:
                return {
                    "signal": "BUY",
                    "confidence": 0.7,
                    "reason": f"WHALE_ACCUMULATION(active:{active_whales})"
                }
            elif whale_accumulating and active_whales > 50:
                return {
                    "signal": "BUY",
                    "confidence": 0.5,
                    "reason": f"MODERATE_WHALE_ACTIVITY(active:{active_whales})"
                }
            elif mining_pressure and not whale_accumulating:
                return {
                    "signal": "SELL",
                    "confidence": 0.6,
                    "reason": "MINING_PRESSURE"
                }

        return {"signal": "HOLD", "confidence": 0, "reason": "NO_CLEAR_CHAIN_SIGNAL"}

    def four_hour_trend_analysis(self, symbol: str, prices: List[float]) -> Dict:
        """4小时趋势分析 - 集成链上数据"""
        if len(prices) < 100:
            return {"signal": "HOLD", "confidence": 0, "reason": "INSUFFICIENT_DATA"}

        current_price = prices[-1]

        # 计算EMA指标
        def calculate_ema(data, period):
            if len(data) < period:
                return sum(data) / len(data)
            ema = data[0]
            alpha = 2 / (period + 1)
            for price in data[1:]:
                ema = price * alpha + ema * (1 - alpha)
            return ema

        # 计算50期和100期EMA
        ema_50 = calculate_ema(prices[-50:], 50)
        ema_100 = calculate_ema(prices[-100:], 100)

        # 计算趋势强度
        trend_strength = (ema_50 - ema_100) / ema_100 * 100

        # 计算价格相对位置
        price_vs_ema50 = (current_price - ema_50) / ema_50 * 100

        # 价格合理性验证
        reasonable_price_ranges = {
            "BTCUSDT": (1000, 200000),
            "ETHUSDT": (500, 10000),
            "ADAUSDT": (0.01, 10),
            "DOTUSDT": (1, 100),
            "LINKUSDT": (1, 100),
            "BNBUSDT": (100, 2000)
        }

        reasonable_range = reasonable_price_ranges.get(symbol, (0.1, 5000))
        if current_price < reasonable_range[0] or current_price > reasonable_range[1]:
            print(f"   ⚠️ 价格异常: ${current_price} (期望范围: ${reasonable_range[0]}-${reasonable_range[1]})")
            return {
                "signal": "HOLD",
                "confidence": 0.1,
                "reason": f"PRICE_ANOMALY(${current_price})"
            }

        print(f"   📊 {symbol} 4H趋势分析:")
        print(f"     当前价格: ${current_price:.4f}")
        print(f"     EMA50: ${ema_50:.4f}")
        print(f"     EMA100: ${ema_100:.4f}")
        print(f"     趋势强度: {trend_strength:.2f}%")
        print(f"     价格相对EMA50: {price_vs_ema50:.2f}%")

        # 获取链上数据信号
        chain_signal = self.analyze_chain_signals(symbol)
        print(f"   🔗 链上信号: {chain_signal['signal']} (信心度: {chain_signal['confidence']:.2f})")

        # 综合技术分析和链上数据
        buy_signals = 0
        confidence = 0

        # 技术分析信号
        if trend_strength > 0.5 and price_vs_ema50 > -1.0:
            buy_signals += 2
            confidence += 0.4
            print(f"     🟢 强势上升趋势")

        elif trend_strength < -1.0 and price_vs_ema50 < -3.0:
            buy_signals += 1
            confidence += 0.3
            print(f"     🔄 超跌反弹机会")

        if trend_strength > 0.2 and price_vs_ema50 > 0.5:
            buy_signals += 1
            confidence += 0.2
            print(f"     ✅ 趋势确认")

        # 链上数据信号加权
        if chain_signal["signal"] == "BUY":
            buy_signals += 1
            confidence += chain_signal["confidence"] * 0.3
            print(f"     🐋 链上数据支持买入")

        # 决策逻辑
        total_signals = buy_signals
        if total_signals >= 3 and confidence > 0.7:
            final_signal = "BUY"
            final_confidence = min(0.9, confidence)
            reason = f"STRONG_COMBO({total_signals} signals)"
        elif total_signals >= 2 and confidence > 0.5:
            final_signal = "BUY"
            final_confidence = confidence
            reason = f"MODERATE_COMBO({total_signals} signals)"
        else:
            final_signal = "HOLD"
            final_confidence = 0
            reason = f"WEAK_SIGNALS(tech:{buy_signals}, chain:{chain_signal['confidence']:.2f})"

        print(f"     🎯 最终决策: {final_signal} (总信心度: {final_confidence:.2f})")
        return {
            "signal": final_signal,
            "confidence": final_confidence,
            "reason": reason,
            "chain_signal": chain_signal
        }

    def find_4h_trend_opportunity(self, portfolio_summary: Dict) -> Optional[Dict]:
        """寻找4小时趋势机会 - 集成链上数据"""
        best_opportunity = None
        best_score = 0

        for symbol in self.config.SYMBOLS:
            if self.portfolio_manager.get_position(symbol):
                continue

            try:
                current_price = self.api.get_ticker_price(symbol)
                if current_price == 0:
                    continue

                # 生成价格数据（实际部署时应使用真实市场数据）
                import random
                base_price = current_price
                closes = [base_price]

                print(f"   💰 使用模拟平台价格: ${base_price:.2f}")

                # 生成价格序列
                if random.random() > 0.3:
                    trend_strength = random.uniform(0.02, 0.08)
                    trend_duration = random.randint(20, 80)
                    print(f"   📈 生成明显趋势: {trend_strength:.2%}")
                else:
                    trend_strength = random.uniform(-0.01, 0.01)
                    trend_duration = 50
                    print(f"   ⚪ 生成震荡市场")

                volatility = random.uniform(0.01, 0.03)

                for i in range(149):
                    if i < trend_duration:
                        current_trend = trend_strength * (i / trend_duration)
                    else:
                        current_trend = trend_strength

                    price_change = current_trend + random.gauss(0, volatility)
                    new_price = closes[-1] * (1 + price_change)
                    closes.append(max(new_price, base_price * 0.7))

                # 综合趋势分析（技术+链上）
                trend_result = self.four_hour_trend_analysis(symbol, closes)

                print(f"🌊 {symbol} 综合分析: {trend_result['signal']} "
                      f"(信心度: {trend_result['confidence']:.2f}) - {trend_result['reason']}")

                if (trend_result["signal"] == 'BUY' and
                    trend_result["confidence"] > best_score and
                    trend_result["confidence"] > self.config.ENTRY_CONFIDENCE):

                    best_score = trend_result["confidence"]
                    best_opportunity = {
                        'symbol': symbol,
                        'signal': 'BUY',
                        'confidence': trend_result['confidence'],
                        'current_price': current_price,
                        'strategy': '4H_TREND_WITH_CHAIN_DATA'
                    }

            except Exception as e:
                print(f"❌ {symbol} 分析失败: {e}")
                continue

        if best_opportunity:
            print(f"🎯 最佳机会: {best_opportunity['symbol']} "
                  f"(信心度: {best_opportunity['confidence']:.2f})")
            return self.execute_enhanced_trade(best_opportunity, portfolio_summary)

        return None

    def check_daily_trade_limit(self) -> bool:
        """检查每日交易限制"""
        today = datetime.now().date()

        if self.last_trade_date != today:
            self.daily_trade_count = 0
            self.last_trade_date = today
            print(f"📅 新的一天开始，交易计数重置")

        if self.daily_trade_count >= self.config.MAX_TRADES_PER_DAY:
            print(f"🚫 达到每日交易限制: {self.daily_trade_count}/{self.config.MAX_TRADES_PER_DAY}")
            return False

        return True

    def execute_enhanced_trade(self, opportunity: Dict, portfolio_summary:Dict) -> Dict:
        """执行交易 - 集成链上数据版本"""
        if not self.check_daily_trade_limit():
            return {
                "status": "rejected",
                "action": "HOLD",
                "reason": "DAILY_TRADE_LIMIT_REACHED"
            }

        symbol = opportunity["symbol"]
        current_price = opportunity["current_price"]

        risk_approval = self.risk_manager.get_trade_approval(
            symbol, opportunity["signal"], opportunity["confidence"], portfolio_summary["total_value"]
        )

        if not risk_approval["approved"]:
            return {"status": "rejected", "action": "HOLD", "reason": risk_approval["reason"]}

        # 仓位计算
        base_trade_amount = 10000
        confidence_multiplier = min(1.5, opportunity["confidence"] * 1.5)
        position_size = base_trade_amount * confidence_multiplier
        position_size = max(2000, min(12500, position_size))

        min_order_usd = 1.0
        if position_size < min_order_usd:
            position_size = min_order_usd
            print(f"⚠️ 调整到最小交易金额: ${min_order_usd}")

        raw_quantity = position_size / current_price

        precision_rules = {
            "BTCUSDT": 4,
            "ETHUSDT": 4,
            "ADAUSDT": 0,
            "DOTUSDT": 1,
            "LINKUSDT": 1,
            "BNBUSDT": 3
        }

        precision = precision_rules.get(symbol, 1)

        if precision == 0:
            quantity = int(round(raw_quantity))
            if quantity < 1:
                quantity = 1
        else:
            quantity = round(raw_quantity * (10 ** precision)) / (10 ** precision)
            quantity = float(round(quantity, precision))

        actual_position_size = quantity * current_price

        print(f"💰 计划金额: ${position_size:.2f}")
        print(f"💰 实际金额: ${actual_position_size:.2f}")
        print(f"📦 交易数量: {quantity} {symbol.replace('USDT', '')}")
        print(f"🎯 精度: {precision}位小数")
        print(f"🚀 执行交易: {opportunity['signal']} {symbol}")
        print(f"   ☕ 信心度: {opportunity['confidence']:.2f}")
        print(f"   策略: {opportunity.get('strategy', '4H_TREND_WITH_CHAIN_DATA')}")

        # 下单
        print(f"   📤 发送订单请求...")
        result = self.api.place_order(symbol, opportunity["signal"], "MARKET", quantity)

        if result:
            print(f"   📥 API响应: {result}")
            if result.get("Success"):
                print("   ✅ 订单执行成功")
                self.portfolio_manager.update_position(symbol, opportunity["signal"], quantity, current_price)
                self.daily_trade_count += 1

                trade_record = {
                    "symbol": symbol,
                    "action": opportunity["signal"],
                    "quantity": quantity,
                    "entry_price": current_price,
                    "pnl": 0,
                    "strategy": opportunity.get('strategy', '4H_TREND_WITH_CHAIN_DATA')
                }
                self.risk_manager.record_trade(trade_record)

                return {
                    "status": "success",
                    "action": opportunity["signal"],
                    "symbol": symbol,
                    "enhanced_confidence": opportunity["confidence"],
                    "result": "ORDER_PLACED",
                    "daily_trades": f"{self.daily_trade_count}/{self.config.MAX_TRADES_PER_DAY}"
                }
            else:
                error_msg = result.get('ErrMsg', 'Unknown error')
                print(f"   ❌ 订单失败: {error_msg}")
        else:
            print("   ❌ API无响应")

        return {
            "status": "error",
            "action": opportunity["signal"],
            "symbol": symbol,
            "reason": f"ORDER_FAILED: {result.get('ErrMsg', 'Unknown error') if result else 'No response'}"
        }

    def check_exit_conditions(self) -> Optional[Dict]:
        """检查退出条件"""
        positions = self.portfolio_manager.get_all_positions()

        for symbol, position in positions.items():
            current_price = self.api.get_ticker_price(symbol)
            if current_price == 0:
                continue

            pnl_pct = (current_price - position["entry_price"]) / position["entry_price"]

            # 止盈 (1.2%)
            if pnl_pct >= 0.012:
                result = self.api.place_order(symbol, "SELL", "MARKET", position["quantity"])
                if result and result.get("Success"):
                    self.portfolio_manager.update_position(symbol, "SELL",position["quantity"], current_price)
                    pnl = (current_price - position["entry_price"]) * position["quantity"]
                    self.risk_manager.record_trade({
                        "symbol": symbol,
                        "action": "SELL",
                        "quantity": position["quantity"],
                        "entry_price": position["entry_price"],
                        "exit_price": current_price,
                        "pnl": pnl,
                        "reason": "TAKE_PROFIT_4H"
                    })

                    return {
                        "status": "success",
                        "action": "SELL",
                        "symbol": symbol,
                        "reason": f"PROFIT({pnl_pct:.2%})",
                        "result": "ORDER_PLACED"
                    }

            # 止损 (2.5%)
            if pnl_pct <= -0.025:
                result = self.api.place_order(symbol, "SELL", "MARKET", position["quantity"])
                if result and result.get("Success"):
                    self.portfolio_manager.update_position(symbol, "SELL",position["quantity"], current_price)
                    pnl = (current_price - position["entry_price"]) * position["quantity"]
                    self.risk_manager.record_trade({
                        "symbol": symbol,
                        "action": "SELL",
                        "quantity": position["quantity"],
                        "entry_price": position["entry_price"],
                        "exit_price": current_price,
                        "pnl": pnl,
                        "reason": "STOP_LOSS_4H"
                    })

                    return {
                        "status": "success",
                        "action": "SELL",
                        "symbol": symbol,
                        "reason": f"STOP_LOSS({pnl_pct:.2%})",
                        "result": "ORDER_PLACED"
                    }

        return None

    def check_time_stop(self, positions: Dict) -> Optional[Dict]:
        """检查时间止损"""
        from datetime import datetime, timedelta

        for symbol, position in positions.items():
            if 'entry_timestamp' not in position:
                position['entry_timestamp'] = datetime.now()
                continue

            entry_time = position['entry_timestamp']
            current_time = datetime.now()
            hold_hours = (current_time - entry_time).total_seconds() / 3600

            if hold_hours >= self.config.MAX_HOLD_HOURS:
                print(f"⏰ {symbol} 时间止损: 持仓{hold_hours:.1f}小时")

                current_price = self.api.get_ticker_price(symbol)
                if current_price > 0:
                    result = self.api.place_order(symbol, "SELL", "MARKET", position["quantity"])
                    if result and result.get("Success"):
                        self.portfolio_manager.update_position(symbol, "SELL", position["quantity"], current_price)
                        pnl = (current_price - position["entry_price"]) * position["quantity"]
                        self.risk_manager.record_trade({
                            "symbol": symbol,
                            "action": "SELL",
                            "quantity": position["quantity"],
                            "entry_price": position["entry_price"],
                            "exit_price": current_price,
                            "pnl": pnl,
                            "reason": f"TIME_STOP({hold_hours:.1f}h)"
                        })

                        return {
                            "status": "success",
                            "action": "SELL",
                            "symbol": symbol,
                            "reason": f"TIME_STOP({hold_hours:.1f}h)",
                            "result": "ORDER_PLACED"
                        }

        return None

    def execute_enhanced_trading_cycle(self) -> Dict:
        """执行交易周期"""
        try:
            if not self.check_daily_trade_limit():
                return {
                    "status": "rejected",
                    "action": "HOLD",
                    "reason": "DAILY_TRADE_LIMIT_REACHED"
                }

            account_info = self.api.get_account_info()
            if not account_info:
                return {"status": "error", "message": "无法获取账户信息"}

            self.portfolio_manager.update_portfolio(account_info)
            portfolio_summary = self.portfolio_manager.get_portfolio_summary()

            # 检查退出条件
            exit_results = self.check_exit_conditions()
            if exit_results:
                return exit_results

            # 检查时间止损
            positions = self.portfolio_manager.get_all_positions()
            time_stop_result = self.check_time_stop(positions)
            if time_stop_result:
                return time_stop_result

            # 寻找交易机会
            entry_result = self.find_4h_trend_opportunity(portfolio_summary)

            if entry_result:
                self.no_trade_count = 0
                return entry_result

            self.no_trade_count += 1

            return {
                "status": "success",
                "action": "HOLD",
                "reason": "NO_4H_TREND_OPPORTUNITY",
                "portfolio_value": portfolio_summary["total_value"],
                "daily_trades": f"{self.daily_trade_count}/{self.config.MAX_TRADES_PER_DAY}"
            }

        except Exception as e:
            return {"status": "error", "message": f"交易周期执行错误: {str(e)}"}

    def get_strategy_status(self) -> Dict:
        """获取策略状态"""
        portfolio_summary = self.portfolio_manager.get_portfolio_summary()

        return {
            "portfolio": portfolio_summary,
            "performance": self.risk_manager.performance_metrics,
            "positions": len(self.portfolio_manager.positions),
            "market_conditions": "4H_TREND_WITH_CHAIN_DATA",
            "no_trade_count": self.no_trade_count,
            "daily_trades": f"{self.daily_trade_count}/{self.config.MAX_TRADES_PER_DAY}",
            "active_strategies": ["4H_TREND_WITH_CHAIN_DATA"]
        }
