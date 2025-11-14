import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # ==================== 团队配置 ====================
    TEAM_NAME = "coffeegirl"
    BOT_NAME = "coffeegirl_trading_bot"

    # ==================== API配置 ====================
    BASE_URL = os.getenv("ROOSTOO_BASE_URL", "https://mock-api.roostoo.com")
    API_KEY = os.getenv("ROOSTOO_API_KEY", "M9qW1eRtY3uI7oPaS0dF6gHjK2lL8ZxCV5bN9mQwE1rT4yUiP7oA3sDdF6gJ2hKl")
    SECRET_KEY = os.getenv("ROOSTOO_SECRET_KEY", "S5dF7gHjK9lL1ZxCV3bN5mQwE7rT9yUiP1oA3sDdF5gJ7hKlZ9xC1vBnM3qW")

    # Horus API配置
    HORUS_API_KEY = os.getenv("HORUS_API_KEY", "b0f507665085984b9c0b3b1f79d672825f07fe8caae37f3d3f1fb18d86e0a70a")
    HORUS_BASE_URL = os.getenv("HORUS_BASE_URL", "https://api.horusdata.xyz")

    # ==================== 交易配置 ====================
    SYMBOLS = ["BTCUSDT", "ETHUSDT", "ADAUSDT", "DOTUSDT", "LINKUSDT", "BNBUSDT"]
    BASE_TIMEFRAME = "4h"
    TIMEFRAMES = ["4h", "1d"]

    # ==================== 4小时趋势策略配置 ====================
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
    MAX_POSITION_SIZE = 0.25
    STOP_LOSS_PCT = 0.020
    TAKE_PROFIT_PCT = 0.010
    MAX_HOLD_HOURS = 12

    # ==================== 策略配置 ====================
    RSI_PERIOD = 21
    RSI_OVERSOLD = 40
    RSI_OVERBOUGHT = 60
    MA_FAST_PERIOD = 50
    MA_SLOW_PERIOD = 100
    BB_PERIOD = 50
    MACD_FAST = 12
    MACD_SLOW = 26
    MACD_SIGNAL = 9

    ENTRY_CONFIDENCE = 0.25
    EXIT_CONFIDENCE = 0.25

    # ==================== 执行配置 ====================
    EXECUTION_INTERVAL = 7200
    MAX_TRADES_PER_DAY = 10
    RETRY_ATTEMPTS = 3
    TIMEOUT = 15

    # ==================== 存储优化配置 ====================
    MAX_DATA_POINTS = 5000
    MAX_LOG_SIZE_MB = 1024
    CLEANUP_INTERVAL = 86400
    BACKUP_RETENTION_DAYS = 3
    SAVE_TRADE_LOGS = True
    COMPRESS_HISTORICAL_DATA = True
    DELETE_OLD_KLINES = True
    KLINE_RETENTION_DAYS = 7

    # ==================== 监控配置 ====================
    LOG_LEVEL = "INFO"
    PERFORMANCE_TRACKING = True
