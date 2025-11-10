import requests
import time
import hmac
import hashlib
import json
from typing import Dict, List, Optional
from config import Config

class RoostooAPI:
    """Roostoo交易所API封装"""
    
    def __init__(self, config: Config):
        self.config = config
        self.base_url = config.BASE_URL
        self.api_key = config.API_KEY
        self.secret_key = config.SECRET_KEY
        self.session = requests.Session()
        self.session.headers.update({"X-API-KEY": self.api_key})
        
    def _generate_signature(self, params: Dict) -> str:
        """生成API签名"""
        query_string = '&'.join([f"{k}={v}" for k, v in sorted(params.items())])
        return hmac.new(
            self.secret_key.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def _request(self, method: str, endpoint: str, params: Dict = None, signed: bool = False) -> Dict:
        """发送API请求"""
        url = f"{self.base_url}{endpoint}"
        
        if params is None:
            params = {}
            
        if signed:
            params['timestamp'] = int(time.time() * 1000)
            params['signature'] = self._generate_signature(params)
        
        for attempt in range(self.config.RETRY_ATTEMPTS):
            try:
                if method.upper() == "GET":
                    response = self.session.get(url, params=params, timeout=self.config.TIMEOUT)
                elif method.upper() == "POST":
                    response = self.session.post(url, json=params, timeout=self.config.TIMEOUT)
                else:
                    raise ValueError(f"不支持的HTTP方法: {method}")
                
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.RequestException as e:
                print(f"API请求失败 (尝试 {attempt + 1}/{self.config.RETRY_ATTEMPTS}): {e}")
                if attempt == self.config.RETRY_ATTEMPTS - 1:
                    return {}
                time.sleep(1)  # 重试前等待
        
        return {}
    
    def get_account_info(self) -> Dict:
        """获取账户信息"""
        return self._request("GET", "/account", signed=True)
    
    def get_ticker_price(self, symbol: str) -> float:
        """获取最新价格"""
        data = self._request("GET", f"/ticker/price", {"symbol": symbol})
        return float(data.get('price', 0)) if data else 0
    
    def get_klines(self, symbol: str, interval: str = "5m", limit: int = 100) -> List[Dict]:
        """获取K线数据"""
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }
        return self._request("GET", "/klines", params) or []
    
    def get_order_book(self, symbol: str, limit: int = 20) -> Dict:
        """获取订单簿"""
        params = {"symbol": symbol, "limit": limit}
        return self._request("GET", "/depth", params) or {}
    
    def get_24h_ticker(self, symbol: str) -> Dict:
        """获取24小时行情"""
        params = {"symbol": symbol}
        return self._request("GET", "/ticker/24hr", params) or {}
    
    def place_order(self, symbol: str, side: str, quantity: float, 
                   order_type: str = "MARKET") -> Dict:
        """下单"""
        params = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": round(quantity, 6)  # 确保精度
        }
        return self._request("POST", "/order", params, signed=True)
    
    def get_order(self, symbol: str, order_id: str) -> Dict:
        """查询订单"""
        params = {"symbol": symbol, "orderId": order_id}
        return self._request("GET", "/order", params, signed=True)
    
    def cancel_order(self, symbol: str, order_id: str) -> Dict:
        """取消订单"""
        params = {"symbol": symbol, "orderId": order_id}
        return self._request("DELETE", "/order", params, signed=True)
    
    def get_open_orders(self, symbol: str = None) -> List[Dict]:
        """获取未成交订单"""
        params = {"symbol": symbol} if symbol else {}
        return self._request("GET", "/openOrders", params, signed=True) or []
    
    def get_market_data(self, symbol: str) -> Dict:
        """获取综合市场数据（用于Horus数据对比）"""
        try:
            price = self.get_ticker_price(symbol)
            klines = self.get_klines(symbol, "5m", 50)
            orderbook = self.get_order_book(symbol, 10)
            
            return {
                "symbol": symbol,
                "current_price": price,
                "price_change": self._calculate_price_change(klines) if klines else 0,
                "volume_24h": self._calculate_volume(klines) if klines else 0,
                "orderbook_depth": self._calculate_orderbook_depth(orderbook),
                "timestamp": int(time.time() * 1000)
            }
        except Exception as e:
            print(f"获取市场数据失败 {symbol}: {e}")
            return {}
    
    def _calculate_price_change(self, klines: List[Dict]) -> float:
        """计算价格变化"""
        if len(klines) < 2:
            return 0
        current_price = float(klines[-1][4])  # 收盘价
        previous_price = float(klines[0][4])
        return ((current_price - previous_price) / previous_price) * 100
    
    def _calculate_volume(self, klines: List[Dict]) -> float:
        """计算成交量"""
        if not klines:
            return 0
        total_volume = sum(float(k[5]) for k in klines)  # 成交量
        return total_volume
    
    def _calculate_orderbook_depth(self, orderbook: Dict) -> Dict:
        """计算订单簿深度"""
        if not orderbook or 'bids' not in orderbook or 'asks' not in orderbook:
            return {"bid_depth": 0, "ask_depth": 0, "spread": 0}
        
        bids = orderbook['bids']
        asks = orderbook['asks']
        
        bid_depth = sum(float(bid[1]) for bid in bids[:5])  # 前5档买单深度
        ask_depth = sum(float(ask[1]) for ask in asks[:5])  # 前5档卖单深度
        
        best_bid = float(bids[0][0]) if bids else 0
        best_ask = float(asks[0][0]) if asks else 0
        spread = best_ask - best_bid if best_ask and best_bid else 0
        
        return {
            "bid_depth": bid_depth,
            "ask_depth": ask_depth,
            "spread": spread,
            "spread_percentage": (spread / best_bid * 100) if best_bid else 0
        }
    
    def validate_api_connection(self) -> bool:
        """验证API连接是否正常"""
        try:
            # 测试获取价格（不需要签名的简单请求）
            price = self.get_ticker_price(self.config.SYMBOLS[0])
            if price > 0:
                print("✅ Roostoo API连接正常")
                return True
            else:
                print("❌ Roostoo API连接失败：无法获取价格")
                return False
        except Exception as e:
            print(f"❌ Roostoo API连接异常: {e}")
            return False
    
    def get_trading_pairs_info(self) -> List[Dict]:
        """获取可交易对信息"""
        pairs_info = []
        for symbol in self.config.SYMBOLS:
            try:
                price = self.get_ticker_price(symbol)
                klines = self.get_klines(symbol, "1h", 24)
                
                if price > 0 and klines:
                    # 计算24小时波动率
                    prices = [float(k[4]) for k in klines]  # 收盘价
                    volatility = self._calculate_volatility(prices)
                    
                    pairs_info.append({
                        "symbol": symbol,
                        "price": price,
                        "volatility_24h": volatility,
                        "status": "TRADING"
                    })
                else:
                    pairs_info.append({
                        "symbol": symbol,
                        "price": 0,
                        "volatility_24h": 0,
                        "status": "UNAVAILABLE"
                    })
                    
            except Exception as e:
                print(f"获取交易对信息失败 {symbol}: {e}")
                pairs_info.append({
                    "symbol": symbol,
                    "price": 0,
                    "volatility_24h": 0,
                    "status": "ERROR"
                })
        
        return pairs_info
    
    def _calculate_volatility(self, prices: List[float]) -> float:
        """计算价格波动率"""
        if len(prices) < 2:
            return 0
        
        returns = []
        for i in range(1, len(prices)):
            if prices[i-1] > 0:
                returns.append((prices[i] - prices[i-1]) / prices[i-1])
        
        if not returns:
            return 0
            
        return (max(returns) - min(returns)) * 100  # 百分比波动率