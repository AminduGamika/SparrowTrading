import requests

class MarketStudyEngine:
    """
    BTC.D, Global Crypto MarketCap, Volatility Index (VIX/MOVE) සහ Market Correlation Study කිරීම.
    """
    @staticmethod
    def fetch_global_market_metrics():
        try:
            # Global Market Data / Trend sentiment
            res = requests.get("https://api.coingecko.com/api/v3/global", timeout=5).json()
            data = res.get('data', {})
            
            btc_dominance = data.get('market_cap_percentage', {}).get('btc', 0.0)
            eth_dominance = data.get('market_cap_percentage', {}).get('eth', 0.0)
            market_cap_change_24h = data.get('market_cap_change_percentage_24h_usd', 0.0)
            
            # Market Regime Detection
            regime = "NORMAL"
            if btc_dominance > 55 and market_cap_change_24h < -2:
                regime = "ALTCOIN_BLEED"  # Altcoins dump heavily when BTC dominance rises in a dip
            elif btc_dominance < 40 and market_cap_change_24h > 2:
                regime = "ALTSEASON"
            elif abs(market_cap_change_24h) > 5:
                regime = "HIGH_VOLATILITY"

            return {
                "btc_dominance": btc_dominance,
                "eth_dominance": eth_dominance,
                "market_cap_change_24h": market_cap_change_24h,
                "regime": regime
            }
        except Exception:
            return {"btc_dominance": 50.0, "eth_dominance": 15.0, "market_cap_change_24h": 0.0, "regime": "NEUTRAL"}