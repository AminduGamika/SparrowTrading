import os
from dotenv import load_dotenv

# .env file එක load කිරීම
load_dotenv()

BINANCE_API_KEY = os.getenv("BINANCE_API_KEY", "")
BINANCE_SECRET_KEY = os.getenv("BINANCE_SECRET_KEY", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# Default Top 30 USDT Pairs
TOP_30_PAIRS = [
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT",
    "ADAUSDT", "AVAXUSDT", "DOGEUSDT", "DOTUSDT", "LINKUSDT",
    "MATICUSDT", "NEARUSDT", "UNIUSDT", "LTCUSDT", "APTUSDT",
    "ATOMUSDT", "ETCUSDT", "FILUSDT", "ARBUSDT", "OPUSDT",
    "INJUSDT", "SUIUSDT", "RNDRUSDT", "TIAUSDT", "SEIUSDT",
    "FETUSDT", "STXUSDT", "AAVEUSDT", "GRTUSDT", "GALAUSDT"
]

# Timeframes for analysis
ALL_TIMEFRAMES = ["15m", "30m", "1h", "2h", "4h", "1d", "1w", "1m"]
SIGNAL_TIMEFRAMES = ["1h", "2h", "4h", "1d", "1w"]

# Risk & PnL Math ($10 Capital @ 10x Leverage)
BASE_CAPITAL = 10.0   # $10
DEFAULT_LEVERAGE = 10 # 10x

DB_PATH = "sqlite:///quant_agent.db"