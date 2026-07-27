class StrategyBenchmarker:
    """
    ප්‍රධාන Hedge Fund Strategies & Algorithm Archetypes සමග සසඳා Signal එක Optimize කිරීම.
    """
    @staticmethod
    def analyze_institutional_bias(df, funding_rate, orderbook_imbalance=0.0):
        """
        Market Archetype Benchmark:
        1. Grid/Range Trading Strategy (When Market is Side-ways)
        2. Momentum Breakout Strategy (High Volatility + Volume)
        3. Mean Reversion / Liquidity Grab Strategy (Institutional Stop Run)
        """
        latest = df.iloc[-1]
        atr = latest.get('atr', 0)
        close = latest['close']

        # Determine Market State
        is_trending = latest.get('adx', 0) > 25 if 'adx' in df.columns else False
        is_squeeze = (latest.get('bb_upper', 0) - latest.get('bb_lower', 0)) / close < 0.03 if 'bb_upper' in df.columns else False

        if is_squeeze:
            recommended_strategy = "Institutional Breakout Expansion Setup"
        elif not is_trending and funding_rate > 0.01:
            recommended_strategy = "Liquidity Sweep & Long Squeeze Reversal"
        elif is_trending:
            recommended_strategy = "Trend Continuation & Order Block Mitigation"
        else:
            recommended_strategy = "Range Bound Market-Making"

        return recommended_strategy