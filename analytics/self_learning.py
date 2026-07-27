import pandas as pd
import numpy as np

class SparrowSelfLearningEngine:
    def __init__(self):
        # Default Weights for Confluence Factors
        self.factor_weights = {
            'smc_ob': 1.5,
            'liquidity_sweep': 1.5,
            'ema_trend': 1.0,
            'rsi_macd': 1.0,
            'volume_poc': 1.2,
            'funding_rate': 0.8
        }

    def evaluate_past_performance(self, trade_history: list):
        """
        පසුගිය Trades වල Success/Failure Analyze කර Confluence Factors වල Weights ස්වයංක්‍රීයව Adjust කිරීම (Self-Training).
        """
        if len(trade_history) < 10:
            return self.factor_weights  # Not enough data for self-training yet

        df_trades = pd.DataFrame(trade_history)
        
        # Calculate win rates for trades influenced by specific factors
        # If SL rate is high on a factor, reduce its weight dynamically
        tp_trades = df_trades[df_trades['outcome'] == 'TP']
        sl_trades = df_trades[df_trades['outcome'] == 'SL']
        
        win_rate = len(tp_trades) / len(df_trades) if len(df_trades) > 0 else 0
        
        # Adaptive Tuning Logic
        if win_rate < 0.5:
            # Shift focus to SMC & Liquidity Sweeps if general trend strategy fails
            self.factor_weights['smc_ob'] = min(2.5, self.factor_weights['smc_ob'] + 0.1)
            self.factor_weights['liquidity_sweep'] = min(2.5, self.factor_weights['liquidity_sweep'] + 0.1)
            self.factor_weights['ema_trend'] = max(0.5, self.factor_weights['ema_trend'] - 0.1)
        
        return self.factor_weights