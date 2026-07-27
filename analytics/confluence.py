import pandas as pd

class ConfluenceEvaluator:
    def __init__(self):
        pass

    def evaluate_signal(self, df: pd.DataFrame, funding_rate: float = 0.0) -> dict:
        """
        Comprehensive 10-Factor Institutional Confluence Engine
        Entry Condition: Minimum 3 Conditions Matched
        """
        if df.empty or len(df) < 50:
            return {'signal': 'NEUTRAL', 'score': 0, 'reasons': []}

        latest = df.iloc[-1]
        price = latest['close']
        
        buy_score = 0
        sell_score = 0
        reasons_buy = []
        reasons_sell = []

        # 1. SMC Order Block & FVG
        if latest.get('is_order_block_bull', False) or latest.get('fvg_bullish', False):
            buy_score += 1
            reasons_buy.append("SMC Bullish Zone (OB/FVG)")
        if latest.get('is_order_block_bear', False) or latest.get('fvg_bearish', False):
            sell_score += 1
            reasons_sell.append("SMC Bearish Zone (OB/FVG)")

        # 2. Liquidity Sweep (Stop Hunt)
        if latest.get('liquidity_sweep_bull', False):
            buy_score += 1
            reasons_buy.append("Bullish Liquidity Sweep (Retail Stop-Hunt Cleared)")
        if latest.get('liquidity_sweep_bear', False):
            sell_score += 1
            reasons_sell.append("Bearish Liquidity Sweep (Retail Stop-Hunt Cleared)")

        # 3. Market Structure Shift (BOS / CHoCH)
        if latest.get('choch_bull', False):
            buy_score += 1
            reasons_buy.append("Bullish Market Structure Shift (CHoCH/BOS Breakout)")
        if latest.get('choch_bear', False):
            sell_score += 1
            reasons_sell.append("Bearish Market Structure Shift (CHoCH/BOS Breakdown)")

        # 4. Fibonacci Golden Zone (0.5 - 0.786)
        if 'fib_0_618' in latest and pd.notna(latest['fib_0_618']):
            if latest['fib_0_786'] <= price <= latest['fib_0_500']:
                if buy_score >= sell_score:
                    buy_score += 1
                    reasons_buy.append(f"Price in Fibonacci Golden Zone (${latest['fib_0_618']:.2f})")
                else:
                    sell_score += 1
                    reasons_sell.append(f"Fibonacci Rejection Zone (${latest['fib_0_618']:.2f})")

        # 5. EMA 200 Trend Alignment
        if 'ema_200' in latest and pd.notna(latest['ema_200']):
            if price > latest['ema_200']:
                buy_score += 1
                reasons_buy.append("Price Above EMA 200 (Macro Uptrend)")
            else:
                sell_score += 1
                reasons_sell.append("Price Below EMA 200 (Macro Downtrend)")

        # 6. Momentum (RSI & MACD Cross)
        if 'rsi' in latest and pd.notna(latest['rsi']):
            if 40 <= latest['rsi'] <= 60 and latest.get('macd', 0) > latest.get('macd_signal', 0):
                buy_score += 1
                reasons_buy.append("Bullish RSI & MACD Momentum Cross")
            elif latest['rsi'] > 60 and latest.get('macd', 0) < latest.get('macd_signal', 0):
                sell_score += 1
                reasons_sell.append("Bearish RSI & MACD Momentum Cross")

        # 7. Volume Profile Point of Control (POC)
        if 'volume_poc' in latest and pd.notna(latest['volume_poc']):
            if abs(price - latest['volume_poc']) / price < 0.005: # Within 0.5% of High Volume POC
                if buy_score >= sell_score:
                    buy_score += 1
                    reasons_buy.append(f"Price Rebounding off Volume POC (${latest['volume_poc']:.2f})")
                else:
                    sell_score += 1
                    reasons_sell.append(f"Price Resisting at Volume POC (${latest['volume_poc']:.2f})")

        # 8. Order Flow Delta Volume Spike
        if 'volume_sma_20' in latest and pd.notna(latest['volume_sma_20']):
            if latest['volume'] > (latest['volume_sma_20'] * 1.3):
                if latest.get('order_flow_delta', 0) > 0:
                    buy_score += 1
                    reasons_buy.append("Aggressive Buying Order Flow Delta Spike")
                else:
                    sell_score += 1
                    reasons_sell.append("Aggressive Selling Order Flow Delta Spike")

        # 9. Futures Funding Rate Bias
        if funding_rate < -0.01: # Negative Funding = Short Heavy (Bullish Squeeze likely)
            buy_score += 1
            reasons_buy.append(f"Negative Futures Funding Rate ({funding_rate:.4f}%) - Short Squeeze Bias")
        elif funding_rate > 0.03: # High Positive Funding = Overleveraged Longs (Long Flush likely)
            sell_score += 1
            reasons_sell.append(f"High Futures Funding Rate ({funding_rate:.4f}%) - Long Liquidation Bias")

        # 10. Volatility Breakout Expansion
        if latest.get('volatility_squeeze', False):
            if buy_score >= sell_score:
                buy_score += 1
                reasons_buy.append("Bollinger Volatility Squeeze Breakout (Bullish)")
            else:
                sell_score += 1
                reasons_sell.append("Bollinger Volatility Squeeze Breakdown (Bearish)")

        # 🔥 Minimum Threshold Filter: At least 3 Factors must match!
        MIN_CONFLUENCE = 3

        if buy_score >= MIN_CONFLUENCE and buy_score > sell_score:
            return {'signal': 'BUY', 'score': buy_score, 'price': price, 'atr': latest.get('atr', price*0.01), 'reasons': reasons_buy}
        elif sell_score >= MIN_CONFLUENCE and sell_score > buy_score:
            return {'signal': 'SELL', 'score': sell_score, 'price': price, 'atr': latest.get('atr', price*0.01), 'reasons': reasons_sell}
        else:
            final_score = max(buy_score, sell_score)
            reasons = reasons_buy if buy_score >= sell_score else reasons_sell
            return {'signal': 'NEUTRAL', 'score': final_score, 'price': price, 'atr': latest.get('atr', price*0.01), 'reasons': reasons}