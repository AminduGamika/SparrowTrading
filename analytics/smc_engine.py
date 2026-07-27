import pandas as pd
import numpy as np

class SMCEngine:
    def __init__(self):
        pass

    @staticmethod
    def detect_fvg(df: pd.DataFrame) -> pd.DataFrame:
        """
        Fair Value Gap (FVG) / Imbalance Detector
        Bullish FVG: Current High < High of 2 candles ago
        Bearish FVG: Current Low > Low of 2 candles ago
        """
        if len(df) < 3:
            return df

        df = df.copy()
        df['bullish_fvg'] = False
        df['bearish_fvg'] = False

        # Bullish FVG (Candle 3 High < Candle 1 Low)
        bullish_mask = df['low'].shift(-2) > df['high']
        df.loc[bullish_mask, 'bullish_fvg'] = True

        # Bearish FVG (Candle 3 Low > Candle 1 High)
        bearish_mask = df['high'].shift(-2) < df['low']
        df.loc[bearish_mask, 'bearish_fvg'] = True

        return df

    @staticmethod
    def detect_order_blocks(df: pd.DataFrame, window: int = 5) -> dict:
        """
        Smart Money Order Blocks Detector
        """
        if len(df) < window + 2:
            return {'bullish_ob': None, 'bearish_ob': None}

        recent_df = df.tail(window + 2)
        
        # Bullish OB: Last down candle before a strong move up
        bullish_ob = None
        bearish_ob = None

        for i in range(len(recent_df) - 2):
            candle = recent_df.iloc[i]
            next_candle = recent_df.iloc[i+1]

            # Bullish Move Check
            if candle['close'] < candle['open'] and next_candle['close'] > candle['high']:
                bullish_ob = {
                    'top': candle['high'],
                    'bottom': candle['low'],
                    'timestamp': candle['timestamp']
                }

            # Bearish Move Check
            if candle['close'] > candle['open'] and next_candle['close'] < candle['low']:
                bearish_ob = {
                    'top': candle['high'],
                    'bottom': candle['low'],
                    'timestamp': candle['timestamp']
                }

        return {
            'bullish_ob': bullish_ob,
            'bearish_ob': bearish_ob
        }

if __name__ == "__main__":
    # Quick Test
    dates = pd.date_range(start="2026-01-01", periods=10, freq="1h")
    dummy_df = pd.DataFrame({
        'timestamp': dates,
        'open': [100, 102, 101, 108, 107, 105, 104, 102, 98, 99],
        'high': [103, 104, 102, 110, 108, 106, 105, 103, 100, 101],
        'low':  [99,  100, 98,  105, 104, 102, 101, 97,  96,  97],
        'close':[102, 101, 107, 107, 105, 103, 102, 98,  99,  100],
        'volume':[10, 15, 80, 50, 20, 15, 30, 90, 40, 30]
    })

    smc = SMCEngine()
    df_fvg = smc.detect_fvg(dummy_df)
    obs = smc.detect_order_blocks(dummy_df)

    print("--- SMC Engine Test Success ---")
    print("Detected Order Blocks:", obs)