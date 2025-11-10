import numpy as np
from typing import List, Dict, Tuple
from config import Config

class TechnicalAnalyzer:
    """高级技术分析引擎"""
    
    def __init__(self, config: Config):
        self.config = config
        
    def calculate_rsi(self, prices: List[float], period: int = None) -> float:
        """计算RSI指标"""
        if period is None:
            period = self.config.RSI_PERIOD
            
        if len(prices) < period + 1:
            return 50.0
            
        deltas = np.diff(prices)
        gains = np.maximum(deltas, 0)
        losses = np.maximum(-deltas, 0)
        
        avg_gains = np.mean(gains[-period:])
        avg_losses = np.mean(losses[-period:])
        
        if avg_losses == 0:
            return 100.0 if avg_gains > 0 else 50.0
            
        rs = avg_gains / avg_losses
        rsi = 100.0 - (100.0 / (1.0 + rs))
        return rsi
    
    def calculate_moving_averages(self, prices: List[float]) -> Tuple[float, float, str]:
        """计算双移动平均线并判断金叉死叉"""
        if len(prices) < self.config.MA_SLOW_PERIOD:
            return 0, 0, "NEUTRAL"
            
        ma_fast = np.mean(prices[-self.config.MA_FAST_PERIOD:])
        ma_slow = np.mean(prices[-self.config.MA_SLOW_PERIOD:])
        
        # 判断交叉信号
        prev_ma_fast = np.mean(prices[-self.config.MA_FAST_PERIOD-1:-1])
        prev_ma_slow = np.mean(prices[-self.config.MA_SLOW_PERIOD-1:-1])
        
        if prev_ma_fast <= prev_ma_slow and ma_fast > ma_slow:
            cross_signal = "GOLDEN_CROSS"
        elif prev_ma_fast >= prev_ma_slow and ma_fast < ma_slow:
            cross_signal = "DEAD_CROSS"
        else:
            cross_signal = "NO_CROSS"
            
        return ma_fast, ma_slow, cross_signal
    
    def calculate_bollinger_bands(self, prices: List[float]) -> Tuple[float, float, float, str]:
        """计算布林带和价格位置"""
        if len(prices) < self.config.BB_PERIOD:
            return 0, 0, 0, "MIDDLE"
            
        sma = np.mean(prices[-self.config.BB_PERIOD:])
        std = np.std(prices[-self.config.BB_PERIOD:])
        
        upper_band = sma + (std * 2)
        lower_band = sma - (std * 2)
        current_price = prices[-1]
        
        # 判断价格在布林带中的位置
        if current_price <= lower_band:
            position = "OVERSOLD"
        elif current_price >= upper_band:
            position = "OVERBOUGHT"
        elif current_price > sma + std:
            position = "UPPER"
        elif current_price < sma - std:
            position = "LOWER"
        else:
            position = "MIDDLE"
            
        return upper_band, sma, lower_band, position
    
    def calculate_macd(self, prices: List[float]) -> Tuple[float, float, float, str]:
        """计算MACD指标"""
        if len(prices) < self.config.MACD_SLOW:
            return 0, 0, 0, "NEUTRAL"
            
        # 计算EMA
        def calculate_ema(data, period):
            weights = np.exp(np.linspace(-1., 0., period))
            weights /= weights.sum()
            ema = np.convolve(data, weights, mode='valid')
            return ema[-1] if len(ema) > 0 else np.mean(data)
        
        ema_fast = calculate_ema(prices, self.config.MACD_FAST)
        ema_slow = calculate_ema(prices, self.config.MACD_SLOW)
        macd_line = ema_fast - ema_slow
        
        # 计算信号线
        macd_values = [calculate_ema(prices[i-self.config.MACD_SIGNAL:i], self.config.MACD_SIGNAL) 
                      for i in range(self.config.MACD_SIGNAL, len(prices)+1)]
        signal_line = macd_values[-1] if macd_values else 0
        histogram = macd_line - signal_line
        
        # 判断MACD信号
        if macd_line > signal_line and histogram > 0:
            signal = "BULLISH"
        elif macd_line < signal_line and histogram < 0:
            signal = "BEARISH"
        else:
            signal = "NEUTRAL"
            
        return macd_line, signal_line, histogram, signal
    
    def calculate_support_resistance(self, prices: List[float], window: int = 20) -> Tuple[float, float]:
        """计算支撑阻力位"""
        if len(prices) < window:
            return 0, 0
            
        recent_prices = prices[-window:]
        resistance = max(recent_prices)
        support = min(recent_prices)
        
        return support, resistance
    
    def analyze_trend(self, prices: List[float]) -> Dict:
        """综合分析趋势"""
        if len(prices) < 50:
            return {"trend": "SIDEWAYS", "strength": 0}
            
        # 计算多个时间段的收益率
        returns_5 = (prices[-1] / prices[-5] - 1) if len(prices) >= 5 else 0
        returns_10 = (prices[-1] / prices[-10] - 1) if len(prices) >= 10 else 0
        returns_20 = (prices[-1] / prices[-20] - 1) if len(prices) >= 20 else 0
        
        # 加权计算趋势强度
        trend_strength = (returns_5 * 0.4 + returns_10 * 0.3 + returns_20 * 0.3) * 100
        
        if trend_strength > 1.0:
            trend = "UPTREND"
        elif trend_strength < -1.0:
            trend = "DOWNTREND"
        else:
            trend = "SIDEWAYS"
            
        return {"trend": trend, "strength": abs(trend_strength)}
    
    def comprehensive_analysis(self, prices: List[float]) -> Dict:
        """综合技术分析"""
        if len(prices) < 30:
            return {"signal": "HOLD", "confidence": 0, "reason": "INSUFFICIENT_DATA"}
            
        current_price = prices[-1]
        
        # 计算各项指标
        rsi = self.calculate_rsi(prices)
        ma_fast, ma_slow, ma_cross = self.calculate_moving_averages(prices)
        bb_upper, bb_middle, bb_lower, bb_position = self.calculate_bollinger_bands(prices)
        macd_line, macd_signal, macd_hist, macd_signal_str = self.calculate_macd(prices)
        support, resistance = self.calculate_support_resistance(prices)
        trend_analysis = self.analyze_trend(prices)
        
        # 初始化信号分数
        buy_signals = 0
        sell_signals = 0
        total_confidence = 0
        
        # RSI 信号
        if rsi < self.config.RSI_OVERSOLD:
            buy_signals += 1
            total_confidence += (self.config.RSI_OVERSOLD - rsi) / self.config.RSI_OVERSOLD
        elif rsi > self.config.RSI_OVERBOUGHT:
            sell_signals += 1
            total_confidence += (rsi - self.config.RSI_OVERBOUGHT) / (100 - self.config.RSI_OVERBOUGHT)
        
        # 移动平均线信号
        if ma_cross == "GOLDEN_CROSS":
            buy_signals += 1
            total_confidence += 0.3
        elif ma_cross == "DEAD_CROSS":
            sell_signals += 1
            total_confidence += 0.3
        
        # 布林带信号
        if bb_position == "OVERSOLD":
            buy_signals += 1
            total_confidence += 0.2
        elif bb_position == "OVERBOUGHT":
            sell_signals += 1
            total_confidence += 0.2
        
        # MACD 信号
        if macd_signal_str == "BULLISH":
            buy_signals += 1
            total_confidence += 0.2
        elif macd_signal_str == "BEARISH":
            sell_signals += 1
            total_confidence += 0.2
        
        # 趋势信号
        if trend_analysis["trend"] == "UPTREND":
            buy_signals += 1
            total_confidence += min(0.3, trend_analysis["strength"] / 10)
        elif trend_analysis["trend"] == "DOWNTREND":
            sell_signals += 1
            total_confidence += min(0.3, trend_analysis["strength"] / 10)
        
        # 计算最终信号和信心度
        signal_count = buy_signals + sell_signals
        if signal_count == 0:
            return {"signal": "HOLD", "confidence": 0, "reason": "NO_CLEAR_SIGNAL"}
        
        confidence = total_confidence / signal_count
        
        if buy_signals > sell_signals and confidence >= self.config.ENTRY_CONFIDENCE:
            signal = "BUY"
            reason = f"STRONG_BUY_SIGNALS({buy_signals}/{signal_count})"
        elif sell_signals > buy_signals and confidence >= self.config.ENTRY_CONFIDENCE:
            signal = "SELL"
            reason = f"STRONG_SELL_SIGNALS({sell_signals}/{signal_count})"
        else:
            signal = "HOLD"
            reason = f"WEAK_SIGNALS(B:{buy_signals},S:{sell_signals},C:{confidence:.2f})"
        
        return {
            "signal": signal,
            "confidence": min(0.95, confidence),
            "reason": reason,
            "indicators": {
                "rsi": rsi,
                "ma_fast": ma_fast,
                "ma_slow": ma_slow,
                "ma_cross": ma_cross,
                "bb_position": bb_position,
                "macd_signal": macd_signal_str,
                "trend": trend_analysis,
                "support": support,
                "resistance": resistance,
                "current_price": current_price
            }
        }