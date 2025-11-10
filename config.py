import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # ==================== 团队配置 ====================
    TEAM_NAME = "coffeegirl"
    BOT_NAME = "coffeegirl_trading_bot"
    
    # ==================== API配置 ====================
    BASE_URL = os.getenv("ROOSTOO_BASE_URL", "https://api.roostoo.com/simulator")
    API_KEY = os.getenv("ROOSTOO_API_KEY", "你的Roostoo API密钥")
    SECRET_KEY = os.getenv("ROOSTOO_SECRET_KEY", "你的Roostoo Secret密钥")
    
    # Horus API配置
# ==================== Horus API配置 ====================
    HORUS_API_KEY = os.getenv("HORUS_API_KEY", "你的Horus API密钥")
    HORUS_BASE_URL = os.getenv("HORUS_BASE_URL", "https://api.horusdata.xyz")
    
    # ==================== 交易配置 ====================
    SYMBOLS = ["BTCUSDT", "ETHUSDT", "ADAUSDT", "DOTUSDT", "LINKUSDT", "BNBUSDT"]
    BASE_TIMEFRAME = "5m"
    TIMEFRAMES = ["5m", "15m", "1h"]
    
    # ==================== Horus增强策略配置 ====================
    SENTIMENT_WEIGHT = 0.15
    WHALE_WEIGHT = 0.20
    PATTERN_WEIGHT = 0.15
    MARKET_METRICS_WEIGHT = 0.10
    
    BULLISH_SENTIMENT_THRESHOLD = 0.6
    BEARISH_SENTIMENT_THRESHOLD = 0.4
    STRONG_WHALE_BUY = 3
    STRONG_WHALE_SELL = 3
    NET_FLOW_THRESHOLD = 1000000
    
    # ==================== 风险控制配置 ====================
    MAX_PORTFOLIO_RISK = 0.015
    MAX_POSITION_SIZE = 0.12
    STOP_LOSS_PCT = 0.015
    TAKE_PROFIT_PCT = 0.030
    TRAILING_STOP_PCT = 0.008
    MAX_TRADES_PER_HOUR = 3
    
    # ==================== 策略配置 ====================
    RSI_PERIOD = 14
    RSI_OVERSOLD = 32
    RSI_OVERBOUGHT = 68
    MA_FAST_PERIOD = 8
    MA_SLOW_PERIOD = 21
    BB_PERIOD = 20
    MACD_FAST = 12
    MACD_SLOW = 26
    MACD_SIGNAL = 9
    
    ENTRY_CONFIDENCE = 0.65
    EXIT_CONFIDENCE = 0.55
    
    # ==================== 执行配置 ====================
    EXECUTION_INTERVAL = 45
    RETRY_ATTEMPTS = 3
    TIMEOUT = 15
    
    # ==================== 监控配置 ====================
    LOG_LEVEL = "INFO"
    PERFORMANCE_TRACKING = True
    SAVE_TRADE_LOGS = True