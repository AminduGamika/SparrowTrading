import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pandas as pd
from binance.client import Client
import logging
from config.settings import TOP_30_PAIRS, ALL_TIMEFRAMES

# Logging Setup (System එකේ සිදුවන දේ Terminal එකේ පැහැදිලිව පෙන්වීමට)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class HistoricalDataLoader:
    def __init__(self):
        # API Key නොමැතිව වුවද Binance Public Data ලබාගත හැක
        self.client = Client("", "")
        # Memory එකේ Data තබා ගැනීමට Dictionary එකක්
        self.memory_store = {}

    def fetch_klines(self, symbol: str, interval: str, limit: int = 200) -> pd.DataFrame:
        """
        Binance API මගින් නියමිත Pair එකට සහ Timeframe එකට අදාළ Historical Data ලබාගනී.
        """
        try:
            # Binance klines endpoint එකෙන් data ගැනීම
            klines = self.client.get_klines(symbol=symbol, interval=interval, limit=limit)
            
            if not klines:
                logger.warning(f"Data not found for {symbol} ({interval})")
                return pd.DataFrame()

            # Data structure එක Pandas DataFrame එකකට හැරවීම
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])

            # Numbers සෑදීම (Float conversion)
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df['open'] = df['open'].astype(float)
            df['high'] = df['high'].astype(float)
            df['low'] = df['low'].astype(float)
            df['close'] = df['close'].astype(float)
            df['volume'] = df['volume'].astype(float)

            # අවශ්‍ය Columns පමණක් තබා ගැනීම
            df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
            return df

        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol} [{interval}]: {e}")
            return pd.DataFrame()

    def load_lifetime_memory(self, symbols: list = None):
        """
        සියලුම Top Pairs වල Timeframes 8 හිම Data මුලින්ම Agent Memory එකට Load කරයි.
        """
        if symbols is None:
            symbols = TOP_30_PAIRS

        logger.info(f" Starting Lifetime Memory Load for {len(symbols)} Pairs across {len(ALL_TIMEFRAMES)} Timeframes...")

        total_tasks = len(symbols) * len(ALL_TIMEFRAMES)
        completed = 0

        for symbol in symbols:
            self.memory_store[symbol] = {}
            for tf in ALL_TIMEFRAMES:
                df = self.fetch_klines(symbol=symbol, interval=tf, limit=200)
                self.memory_store[symbol][tf] = df
                completed += 1
                if completed % 10 == 0 or completed == total_tasks:
                    logger.info(f"Progress: [{completed}/{total_tasks}] Timeframes Loaded.")

        logger.info(" All Lifetime Historical Data loaded successfully into Agent Memory!")
        return self.memory_store

if __name__ == "__main__":
    # Test Run: Code එක නිවැරදිව වැඩ කරන්නේදැයි පරීක්ෂා කිරීම
    loader = HistoricalDataLoader()
    # Test කිරීම සඳහා BTCUSDT වල historical data load කර බලමු
    test_data = loader.fetch_klines("BTCUSDT", "1h", limit=5)
    print("\n--- BTCUSDT 1H Test Sample Data ---")
    print(test_data)