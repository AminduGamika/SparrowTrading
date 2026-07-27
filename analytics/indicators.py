import pandas as pd
import numpy as np

class TechnicalIndicators:
    @staticmethod
    def add_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
        if df.empty or len(df) < 50:
            return df

        # 1. Standard EMAs (20, 50, 200)
        df['ema_20'] = df['close'].ewm(span=20, adjust=False).mean()
        df['ema_50'] = df['close'].ewm(span=50, adjust=False).mean()
        df['ema_200'] = df['close'].ewm(span=200, adjust=False).mean()

        # 2. RSI (14)
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / (loss + 1e-10)
        df['rsi'] = 100 - (100 / (1 + rs))

        # 3. MACD
        ema12 = df['close'].ewm(span=12, adjust=False).mean()
        ema26 = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = ema12 - ema26
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()

        # 4. ATR
        high_low = df['high'] - df['low']
        high_close = (df['high'] - df['close'].shift()).abs()
        low_close = (df['low'] - df['close'].shift()).abs()
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        df['atr'] = ranges.max(axis=1).rolling(14).mean()

        # 5. Volume SMA & Delta Pressure Proxy
        df['volume_sma_20'] = df['volume'].rolling(20).mean()
        df['order_flow_delta'] = np.where(df['close'] >= df['open'], df['volume'], -df['volume'])

        # 6. Fibonacci Retracement (Lookback 100 Candles)
        recent_100 = df.tail(100)
        high_p = recent_100['high'].max()
        low_p = recent_100['low'].min()
        diff = high_p - low_p
        df['fib_0_500'] = high_p - (0.500 * diff)
        df['fib_0_618'] = high_p - (0.618 * diff) # Golden Pocket
        df['fib_0_786'] = high_p - (0.786 * diff)

        # 7. 🔥 Liquidity Sweeps Detection (Stop Hunts)
        df['prev_high_20'] = df['high'].shift(1).rolling(20).max()
        df['prev_low_20'] = df['low'].shift(1).rolling(20).min()
        
        # Bullish Sweep: Price breaks below previous low but closes above it
        df['liquidity_sweep_bull'] = (df['low'] < df['prev_low_20']) & (df['close'] > df['prev_low_20'])
        # Bearish Sweep: Price breaks above previous high but closes below it
        df['liquidity_sweep_bear'] = (df['high'] > df['prev_high_20']) & (df['close'] < df['prev_high_20'])

        # 8. 🔥 Structure Shift (BOS & CHoCH)
        df['choch_bull'] = (df['close'] > df['prev_high_20']) & (df['close'].shift(1) <= df['prev_high_20'])
        df['choch_bear'] = (df['close'] < df['prev_low_20']) & (df['close'].shift(1) >= df['prev_low_20'])

        # 9. 🔥 Bollinger Band Volatility Squeeze
        df['bb_mid'] = df['close'].rolling(20).mean()
        df['bb_std'] = df['close'].rolling(20).std()
        df['bb_upper'] = df['bb_mid'] + (2 * df['bb_std'])
        df['bb_lower'] = df['bb_mid'] - (2 * df['bb_std'])
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_mid']
        df['volatility_squeeze'] = df['bb_width'] < df['bb_width'].rolling(50).min() * 1.15

        # 10. 🔥 Volume Profile POC (Point of Control)
        # Price level with highest volume over last 50 bars
        poc_price = df.tail(50).groupby(pd.cut(df.tail(50)['close'], bins=10))['volume'].sum().idxmax().mid
        df['volume_poc'] = poc_price

        return df

if __name__ == "__main__":
    # Quick Test with Dummy Data
    dates = pd.date_range(start="2026-01-01", periods=100, freq="1h")
    dummy_data = pd.DataFrame({
        'timestamp': dates,
        'open': np.random.uniform(60000, 65000, 100),
        'high': np.random.uniform(65000, 67000, 100),
        'low': np.random.uniform(58000, 60000, 100),
        'close': np.random.uniform(60000, 65000, 100),
        'volume': np.random.uniform(100, 1000, 100)
    })

    result = TechnicalIndicators.add_all_indicators(dummy_data)
    print("--- Indicators Calculated Successfully ---")
    print(result[['close', 'ema_20', 'rsi', 'macd', 'atr']].tail())