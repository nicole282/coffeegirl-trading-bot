import requests
import time
import hmac
import hashlib
from typing import Dict, List, Optional
from config import Config

class RoostooAPI:
    """Roostoo交易所API封装（修复版）"""

    def __init__(self, config: Config):
        self.config = config
        self.base_url = config.BASE_URL
        self.api_key = config.API_KEY
        self.secret_key = config.SECRET_KEY
        self.session = requests.Session()

    def _get_timestamp(self) -> str:
        """获取13位毫秒时间戳"""
        return str(int(time.time() * 1000))

    def _generate_signature(self, params: Dict) -> str:
        """生成HMAC SHA256签名"""
        sorted_keys = sorted(params.keys())
        total_params = "&".join([f"{k}={params[k]}" for k in sorted_keys])

        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            total_params.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        return signature

    def _get_signed_headers(self, params: Dict) -> tuple:
        """生成签名头部"""
        params['timestamp'] = self._get_timestamp()
        signature = self._generate_signature(params)

        headers = {
            'RST-API-KEY': self.api_key,
            'MSG-SIGNATURE': signature
        }

        return headers, params

    def _request(self, method: str, endpoint: str, params: Dict = None, signed: bool = False) -> Dict:
        """发送API请求"""
        url = f"{self.base_url}{endpoint}"

        if params is None:
            params = {}

        headers = {}
        data = None

        if signed:
            headers, signed_params = self._get_signed_headers(params)
            if method.upper() == "POST":
                headers['Content-Type'] = 'application/x-www-form-urlencoded'
                sorted_keys = sorted(signed_params.keys())
                data = "&".join([f"{k}={signed_params[k]}" for k in sorted_keys])
                params = {}
            else:
                params = signed_params
        else:
            if endpoint == "/v3/ticker":
                params['timestamp'] = self._get_timestamp()

        for attempt in range(self.config.RETRY_ATTEMPTS):
            try:
                if method.upper() == "GET":
                    response = self.session.get(url, params=params, headers=headers, timeout=self.config.TIMEOUT)
                elif method.upper() == "POST":
                    response = self.session.post(url, data=data, params=params, headers=headers, timeout=self.config.TIMEOUT)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                response.raise_for_status()
                return response.json()

            except requests.exceptions.RequestException as e:
                print(f"API请求失败 (尝试 {attempt + 1}/{self.config.RETRY_ATTEMPTS}): {e}")
                if e.response:
                    print(f"错误响应: {e.response.text}")
                if attempt == self.config.RETRY_ATTEMPTS - 1:
                    return {"Success": False, "ErrMsg": str(e)}
                time.sleep(1)

        return {"Success": False, "ErrMsg": "All retry attempts failed"}

    def get_server_time(self) -> Dict:
        return self._request("GET", "/v3/serverTime")

    def get_exchange_info(self) -> Dict:
        return self._request("GET", "/v3/exchangeInfo")

    def get_ticker(self, pair: str = None) -> Dict:
        params = {}
        if pair:
            if "USDT" in pair:
                pair = pair.replace("USDT", "/USD")
            params['pair'] = pair
        return self._request("GET", "/v3/ticker", params)

    def get_balance(self) -> Dict:
        return self._request("GET", "/v3/balance", {}, signed=True)

    def get_pending_count(self) -> Dict:
        return self._request("GET", "/v3/pending_count", {}, signed=True)


    def place_order(self, pair: str, side: str, order_type: str = "MARKET", quantity: float = None, price: float = None) -> Dict:
        """下单 - 修复数量格式"""
        # 确保符号格式正确
        if "USDT" in pair:
            pair = pair.replace("USDT", "/USD")
        elif "/" not in pair:
            pair = f"{pair}/USD"

        print(f"   🔄 转换交易对: {pair}")
        print(f"   📦 下单数量: {quantity} (类型: {type(quantity).__name__})")

        # 确保数量是数字类型
        # 最终数量清理
        if quantity is not None:
            # 转换为字符串并清理
            if isinstance(quantity, float) and quantity.is_integer():
                quantity_str = str(int(quantity))
            else:
                quantity_str = str(quantity)

            # 移除不必要的尾随零和小数点
            if '.' in quantity_str:
                quantity_str = quantity_str.rstrip('0').rstrip('.') if '.'in quantity_str else quantity_str
        else:
            quantity_str = "0"

        print(f"   🎯 最终数量字符串: '{quantity_str}'")
        if quantity is not None:
            quantity_str = str(quantity)
            # 如果是整数，去掉小数部分
            if quantity_str.endswith('.0'):
                quantity_str = quantity_str[:-2]
        else:
            quantity_str = "0"

        params = {
            'pair': pair,
            'side': side.upper(),
            'type': order_type.upper(),
            'quantity': quantity_str
        }

        if order_type.upper() == "LIMIT" and price is not None:
            params['price'] = str(price)

        print(f"   📤 发送参数: {params}")
        return self._request("POST", "/v3/place_order", params, signed=True)

    def query_order(self, order_id: str = None, pair: str = None, pending_only: bool = None) -> Dict:
        params = {}
        if order_id:
            params['order_id'] = order_id
        elif pair:
            if "USDT" in pair:
                pair = pair.replace("USDT", "/USD")
            params['pair'] = pair
            if pending_only is not None:
                params['pending_only'] = 'TRUE' if pending_only else 'FALSE'

        return self._request("POST", "/v3/query_order", params, signed=True)

    def cancel_order(self, order_id: str = None, pair: str = None) -> Dict:
        params = {}
        if order_id:
            params['order_id'] = order_id
        elif pair:
            if "USDT" in pair:
                pair = pair.replace("USDT", "/USD")
            params['pair'] = pair

        return self._request("POST", "/v3/cancel_order", params, signed=True)

    # 兼容性方法
    def get_account_info(self) -> Dict:
        return self.get_balance()


    def get_ticker_price(self, symbol: str) -> float:
        """获取最新价格 - 修复版"""
        # 转换符号格式
        if "USDT" in symbol:
            pair = symbol.replace("USDT", "/USD")
        else:
            pair = symbol

        data = self.get_ticker(pair)
        print(f"   🔍 {symbol} 原始数据: {data}")

        if data.get("Success") and "Data" in data:
            # 尝试从Data中获取价格
            if pair in data["Data"]:
                last_price = data["Data"][pair].get("LastPrice", 0)
                print(f"   💰 解析到价格: {last_price}")
                return float(last_price)
            elif data["Data"]:
                # 如果没有精确匹配，取第一个交易对的价格
                first_pair = list(data["Data"].keys())[0]
                last_price = data["Data"][first_pair].get("LastPrice", 0)
                print(f"   💰 使用第一个交易对价格: {last_price}")
                return float(last_price)

        print(f"   ❌ 无法解析价格，返回0")
        return 0.0

    def get_klines(self, symbol: str, interval: str = "5m", limit: int = 100) -> List[Dict]:
        print(f"⚠️ K线数据需要从Horus API获取: {symbol}")
        return []

    def validate_api_connection(self) -> bool:
        try:
            time_data = self.get_server_time()
            if "ServerTime" in time_data:
                print("✅ Roostoo API连接正常")
                return True
            else:
                print("❌ Roostoo API连接失败")
                return False
        except Exception as e:
            print(f"❌ Roostoo API连接异常: {e}")
            return False
