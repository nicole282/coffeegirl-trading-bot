#!/usr/bin/env python3
"""
Horus数据集成模块
为交易机器人提供高级市场数据
"""

import requests
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta

class HorusData:
    """Horus数据客户端"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.horusdata.xyz"
        self.session = requests.Session()
        self.session.headers.update({
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        })
    
    def get_market_sentiment(self, symbol: str) -> Dict:
        """获取市场情绪数据"""
        try:
            # 获取社交媒体情绪（Twitter, Reddit等）
            response = self.session.get(
                f"{self.base_url}/sentiment/{symbol.replace('USDT', '')}",
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                return {
                    "sentiment_score": data.get("score", 0.5),  # 0-1, 0.5中性
                    "mentions_24h": data.get("mentions", 0),
                    "bullish_ratio": data.get("bullish_ratio", 0.5),
                    "bearish_ratio": data.get("bearish_ratio", 0.5)
                }
        except Exception as e:
            print(f"Horus情绪数据获取失败: {e}")
        
        return {"sentiment_score": 0.5, "mentions_24h": 0, "bullish_ratio": 0.5, "bearish_ratio": 0.5}
    
    def get_whale_activity(self, symbol: str) -> Dict:
        """获取鲸鱼活动数据"""
        try:
            response = self.session.get(
                f"{self.base_url}/whales/{symbol.replace('USDT', '')}",
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                return {
                    "large_buys_24h": data.get("large_buys", 0),
                    "large_sells_24h": data.get("large_sells", 0),
                    "net_flow": data.get("net_flow", 0),  # 正数表示净流入
                    "whale_confidence": data.get("confidence", 0.5)
                }
        except Exception as e:
            print(f"Horus鲸鱼数据获取失败: {e}")
        
        return {"large_buys_24h": 0, "large_sells_24h": 0, "net_flow": 0, "whale_confidence": 0.5}
    
    def get_market_metrics(self, symbol: str) -> Dict:
        """获取高级市场指标"""
        try:
            response = self.session.get(
                f"{self.base_url}/metrics/{symbol.replace('USDT', '')}",
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                return {
                    "volatility_24h": data.get("volatility", 0.02),
                    "volume_ratio": data.get("volume_ratio", 1.0),  # 相对于平均
                    "liquidity_score": data.get("liquidity", 0.5),
                    "market_trend": data.get("trend", "neutral")  # bullish/bearish/neutral
                }
        except Exception as e:
            print(f"Horus市场指标获取失败: {e}")
        
        return {"volatility_24h": 0.02, "volume_ratio": 1.0, "liquidity_score": 0.5, "market_trend": "neutral"}
    
    def get_cross_exchange_data(self, symbol: str) -> Dict:
        """获取跨交易所数据"""
        try:
            response = self.session.get(
                f"{self.base_url}/arbitrage/{symbol.replace('USDT', '')}",
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                return {
                    "binance_price": data.get("binance", 0),
                    "huobi_price": data.get("huobi", 0),
                    "okx_price": data.get("okx", 0),
                    "price_disparity": data.get("disparity", 0)  # 最大价格差异百分比
                }
        except Exception as e:
            print(f"Horus跨交易所数据获取失败: {e}")
        
        return {"binance_price": 0, "huobi_price": 0, "okx_price": 0, "price_disparity": 0}
    
    def get_historical_patterns(self, symbol: str, pattern_type: str = "similar") -> Dict:
        """获取历史模式识别"""
        try:
            response = self.session.get(
                f"{self.base_url}/patterns/{symbol.replace('USDT', '')}",
                params={"type": pattern_type},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                return {
                    "pattern_confidence": data.get("confidence", 0.5),
                    "expected_direction": data.get("direction", "neutral"),  # up/down/neutral
                    "similarity_score": data.get("similarity", 0.5),
                    "success_rate": data.get("success_rate", 0.5)
                }
        except Exception as e:
            print(f"Horus历史模式获取失败: {e}")
        
        return {"pattern_confidence": 0.5, "expected_direction": "neutral", "similarity_score": 0.5, "success_rate": 0.5}