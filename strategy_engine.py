#!/usr/bin/env python3
"""
coffeegirl 增强策略引擎 - 整合Horus数据
"""

from typing import Dict, List, Optional
from datetime import datetime
from config import Config
from exchange_api import RoostooAPI
from technical_analyzer import TechnicalAnalyzer
from risk_manager import RiskManager
from portfolio_manager import PortfolioManager
from horus_data import HorusData

class EnhancedStrategy:
    """coffeegirl 增强策略引擎"""
    
    def __init__(self, config: Config, api: RoostooAPI):
        self.config = config
        self.api = api
        self.technical_analyzer = TechnicalAnalyzer(config)
        self.risk_manager = RiskManager(config)
        self.portfolio_manager = PortfolioManager(config, api)
        self.horus_data = HorusData(config.HORUS_API_KEY)
        
        self.horus_cache = {}
        self.cache_timeout = 300
        
    def get_enhanced_analysis(self, symbol: str, prices: List[float]) -> Dict:
        """增强版分析"""
        technical_analysis = self.technical_analyzer.comprehensive_analysis(prices)
        horus_analysis = self.get_horus_analysis(symbol)
        enhanced_signal = self.fuse_signals(technical_analysis, horus_analysis, symbol)
        
        return enhanced_signal
    
    def get_horus_analysis(self, symbol: str) -> Dict:
        """获取Horus数据"""
        current_time = datetime.now().timestamp()
        
        cache_key = f"{symbol}_{current_time // self.cache_timeout}"
        if cache_key in self.horus_cache:
            return self.horus_cache[cache_key]
        
        try:
            sentiment = self.horus_data.get_market_sentiment(symbol)
            whale_activity = self.horus_data.get_whale_activity(symbol)
            market_metrics = self.horus_data.get_market_metrics(symbol)
            patterns = self.horus_data.get_historical_patterns(symbol)
            
            horus_analysis = {
                "sentiment": sentiment,
                "whale_activity": whale_activity,
                "market_metrics": market_metrics,
                "patterns": patterns,
                "timestamp": current_time
            }
            
            self.horus_cache[cache_key] = horus_analysis
            return horus_analysis
            
        except Exception as e:
            print(f"Horus数据分析失败: {e}")
            return self.get_fallback_horus_analysis()
    
    def get_fallback_horus_analysis(self) -> Dict:
        """备用Horus数据"""
        return {
            "sentiment": {"sentiment_score": 0.5, "bullish_ratio": 0.5},
            "whale_activity": {"net_flow": 0, "whale_confidence": 0.5},
            "market_metrics": {"market_trend": "neutral", "volatility_24h": 0.02},
            "patterns": {"pattern_confidence": 0.5, "expected_direction": "neutral"}
        }
    
    def fuse_signals(self, technical: Dict, horus: Dict, symbol: str) -> Dict:
        """融合技术信号和Horus信号"""
        tech_signal = technical["signal"]
        tech_confidence = technical["confidence"]
        horus_signal, horus_confidence = self.analyze_horus_signals(horus)
        
        print(f"☕ {symbol} 信号分析:")
        print(f"   技术信号: {tech_signal} (信心度: {tech_confidence:.2f})")
        print(f"   数据信号: {horus_signal} (信心度: {horus_confidence:.2f})")
        
        if tech_signal == horus_signal and tech_signal != "HOLD":
            fused_confidence = (tech_confidence * 0.6 + horus_confidence * 0.4) * 1.2
            final_signal = tech_signal
            reason = f"技术+数据双重确认"
            
        elif tech_signal != horus_signal:
            if tech_confidence >= horus_confidence:
                final_signal = tech_signal
                fused_confidence = tech_confidence * 0.8
                reason = f"技术信号主导"
            else:
                final_signal = horus_signal
                fused_confidence = horus_confidence * 0.8
                reason = f"数据信号主导"
        else:
            final_signal = "HOLD"
            fused_confidence = 0
            reason = "信号不足"
        
        adjusted_confidence = self.apply_hus_adjustments(fused_confidence, horus)
        
        return {
            "signal": final_signal,
            "confidence": min(0.95, adjusted_confidence),
            "reason": reason,
            "technical_analysis": technical,
            "horus_analysis": horus,
            "is_enhanced": True
        }
    
    def analyze_horus_signals(self, horus: Dict) -> tuple:
        """分析Horus数据"""
        sentiment_score = horus["sentiment"]["sentiment_score"]
        bullish_ratio = horus["sentiment"]["bullish_ratio"]
        net_flow = horus["whale_activity"]["net_flow"]
        whale_confidence = horus["whale_activity"]["whale_confidence"]
        market_trend = horus["market_metrics"]["market_trend"]
        pattern_direction = horus["patterns"]["expected_direction"]
        pattern_confidence = horus["patterns"]["pattern_confidence"]
        
        horus_confidence = 0
        buy_signals = 0
        sell_signals = 0
        
        if sentiment_score > self.config.BULLISH_SENTIMENT_THRESHOLD:
            buy_signals += 1
            horus_confidence += self.config.SENTIMENT_WEIGHT
        elif sentiment_score < self.config.BEARISH_SENTIMENT_THRESHOLD:
            sell_signals += 1
            horus_confidence += self.config.SENTIMENT_WEIGHT
        
        if net_flow > self.config.NET_FLOW_THRESHOLD and whale_confidence > 0.6:
            buy_signals += 1
            horus_confidence += self.config.WHALE_WEIGHT
        elif net_flow < -self.config.NET_FLOW_THRESHOLD and whale_confidence > 0.6:
            sell_signals += 1
            horus_confidence += self.config.WHALE_WEIGHT
        
        if market_trend == "bullish":
            buy_signals += 1
            horus_confidence += self.config.MARKET_METRICS_WEIGHT * 0.5
        elif market_trend == "bearish":
            sell_signals += 1
            horus_confidence += self.config.MARKET_METRICS_WEIGHT * 0.5
        
        if pattern_direction == "up" and pattern_confidence > 0.6:
            buy_signals += 1
            horus_confidence += self.config.PATTERN_WEIGHT * pattern_confidence
        elif pattern_direction == "down" and pattern_confidence > 0.6:
            sell_signals += 1
            horus_confidence += self.config.PATTERN_WEIGHT * pattern_confidence
        
        if buy_signals > sell_signals and horus_confidence > 0.3:
            return "BUY", horus_confidence
        elif sell_signals > buy_signals and horus_confidence > 0.3:
            return "SELL", horus_confidence
        else:
            return "HOLD", 0
    
    def apply_hus_adjustments(self, confidence: float, horus: Dict) -> float:
        """应用Horus数据调整"""
        adjusted_confidence = confidence
        
        volatility = horus["market_metrics"]["volatility_24h"]
        if volatility > 0.05:
            adjusted_confidence *= 0.8
        elif volatility < 0.01:
            adjusted_confidence *= 1.1
        
        liquidity = horus["market_metrics"]["liquidity_score"]
        if liquidity > 0.7:
            adjusted_confidence *= 1.1
        elif liquidity < 0.3:
            adjusted_confidence *= 0.9
        
        return adjusted_confidence
    
    def execute_enhanced_trading_cycle(self) -> Dict:
        """执行增强交易周期"""
        try:
            account_info = self.api.get_account_info()
            if not account_info:
                return {"status": "error", "message": "无法获取账户信息"}
                
            self.portfolio_manager.update_portfolio(account_info)
            portfolio_summary = self.portfolio_manager.get_portfolio_summary()
            
            exit_results = self.check_exit_conditions()
            if exit_results:
                return exit_results
            
            entry_result = self.find_enhanced_entry_opportunity(portfolio_summary)
            if entry_result:
                return entry_result
            
            return {
                "status": "success", 
                "action": "HOLD", 
                "reason": "NO_ENHANCED_OPPORTUNITY",
                "portfolio_value": portfolio_summary["total_value"]
            }
            
        except Exception as e:
            return {"status": "error", "message": f"交易周期执行错误: {str(e)}"}
    
    def find_enhanced_entry_opportunity(self, portfolio_summary: Dict) -> Optional[Dict]:
        """寻找入场机会"""
        best_opportunity = None
        best_score = 0
        
        for symbol in self.config.SYMBOLS:
            if self.portfolio_manager.get_position(symbol):
                continue
                
            klines = self.api.get_klines(symbol, self.config.BASE_TIMEFRAME, 100)
            if not klines:
                continue
                
            closes = [float(k[4]) for k in klines]
            enhanced_analysis = self.get_enhanced_analysis(symbol, closes)
            
            print(f"☕ {symbol} 增强分析: {enhanced_analysis['signal']} "
                  f"(信心度: {enhanced_analysis['confidence']:.2f})")
            
            if (enhanced_analysis["signal"] != 'HOLD' and 
                enhanced_analysis["confidence"] > best_score and 
                enhanced_analysis["confidence"] > self.config.ENTRY_CONFIDENCE):
                
                best_score = enhanced_analysis["confidence"]
                best_opportunity = {
                    'symbol': symbol,
                    'signal': enhanced_analysis['signal'],
                    'confidence': enhanced_analysis['confidence'],
                    'analysis': enhanced_analysis,
                    'current_price': closes[-1] if closes else 0
                }
        
        if best_opportunity:
            return self.execute_enhanced_trade(best_opportunity, portfolio_summary)
        
        return None
    
    def execute_enhanced_trade(self, opportunity: Dict, portfolio_summary: Dict) -> Dict:
        """执行交易"""
        symbol = opportunity["symbol"]
        current_price = opportunity["current_price"]
        
        risk_approval = self.risk_manager.get_trading_approval(
            symbol, opportunity["signal"], opportunity["confidence"], portfolio_summary["total_value"]
        )
        
        if not risk_approval["approved"]:
            return {"status": "rejected", "action": "HOLD", "reason": risk_approval["reason"]}
        
        volatility = opportunity["analysis"]["horus_analysis"]["market_metrics"]["volatility_24h"]
        position_size = self.risk_manager.calculate_position_size(
            symbol, current_price, 
            current_price * (1 - self.config.STOP_LOSS_PCT), 
            portfolio_summary["total_value"]
        )
        
        quantity = position_size / current_price
        
        print(f"🚀 执行交易: {opportunity['signal']} {symbol}")
        print(f"   ☕ 信心度: {opportunity['confidence']:.2f}")
        print(f"   数量: {quantity:.6f}")
        
        result = self.api.place_order(symbol, opportunity["signal"], quantity)
        
        if result:
            self.portfolio_manager.update_position(symbol, opportunity["signal"], quantity, current_price)
            
            trade_record = {
                "symbol": symbol,
                "action": opportunity["signal"],
                "quantity": quantity,
                "entry_price": current_price,
                "pnl": 0,
                "enhanced_analysis": opportunity["analysis"]
            }
            self.risk_manager.record_trade(trade_record)
            
        return {
            "status": "success", 
            "action": opportunity["signal"],
            "symbol": symbol,
            "enhanced_confidence": opportunity["confidence"],
            "result": result
        }
    
    def check_exit_conditions(self) -> Optional[Dict]:
        """检查退出条件"""
        positions = self.portfolio_manager.get_all_positions()
        
        for symbol, position in positions.items():
            current_price = self.api.get_ticker_price(symbol)
            if current_price == 0:
                continue
                
            simulated_position = {
                "entry_price": position["entry_price"],
                "signal": "BUY",
                "stop_loss": position["entry_price"] * (1 - self.config.STOP_LOSS_PCT),
                "take_profit": position["entry_price"] * (1 + self.config.TAKE_PROFIT_PCT)
            }
            
            exit_check = self.risk_manager.should_exit_trade(simulated_position, current_price)
            
            if exit_check["exit"]:
                result = self.api.place_order(symbol, "SELL", position["quantity"])
                if result:
                    self.portfolio_manager.update_position(symbol, "SELL", position["quantity"], current_price)
                    pnl = (current_price - position["entry_price"]) * position["quantity"]
                    self.risk_manager.record_trade({
                        "symbol": symbol,
                        "action": "SELL",
                        "quantity": position["quantity"],
                        "entry_price": position["entry_price"],
                        "exit_price": current_price,
                        "pnl": pnl,
                        "reason": exit_check["reason"]
                    })
                
                return {
                    "status": "success",
                    "action": "SELL",
                    "symbol": symbol,
                    "reason": exit_check["reason"],
                    "result": result
                }
        
        return None
    
    def get_strategy_status(self) -> Dict:
        """获取策略状态"""
        portfolio_summary = self.portfolio_manager.get_portfolio_summary()
        
        return {
            "portfolio": portfolio_summary,
            "performance": self.risk_manager.performance_metrics,
            "positions": len(self.portfolio_manager.positions),
            "market_conditions": {}
        }