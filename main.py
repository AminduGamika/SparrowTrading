import asyncio
import logging
import pandas as pd
from data.historical_loader import HistoricalDataLoader
from data.websocket_engine import BinanceWebSocketManager
from analytics.confluence import ConfluenceEvaluator
from alerts.telegram_bot import TelegramAlertNotifier
from config.settings import TOP_30_PAIRS

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class CryptoAgentOrchestrator:
    def __init__(self):
        self.loader = HistoricalDataLoader()
        self.ws_manager = BinanceWebSocketManager()
        self.evaluator = ConfluenceEvaluator()
        self.notifier = TelegramAlertNotifier()
        self.memory = {}

    async def initialize(self):
        logger.info("🤖 Starting Sparrow Trading Agent Initialization...")
        # 1. Historical Memory Load
        self.memory = self.loader.load_lifetime_memory()
        
        # 2. WebSocket Connection Start in Background
        asyncio.create_task(self.ws_manager.connect())
        await asyncio.sleep(2)  # Wait for initial stream connection
        logger.info("⚡ Live Market Stream Connected!")

    async def run_scanning_loop(self):
        """
        24/7 Scanning Loop across Top 30 Pairs
        """
        logger.info("🚀 Agent Live Scanning Engine Started...")
        
        while True:
            try:
                for symbol in TOP_30_PAIRS:
                    # Timeframe 15m default analysis
                    df = self.memory.get(symbol, {}).get('15m', pd.DataFrame())
                    
                    if df.empty:
                        continue

                    # Update latest price from live websocket stream
                    live_ticker = self.ws_manager.live_prices.get(symbol, {})
                    if live_ticker and 'price' in live_ticker:
                        df.iloc[-1, df.columns.get_loc('close')] = live_ticker['price']

                    # Get live orderbook
                    ob_data = self.ws_manager.live_orderbook.get(symbol, {})

                    # Confluence 3/5 Evaluation
                    signal_res = self.evaluator.evaluate_signal(df, ob_data)

                    if signal_res['signal'] in ['BUY', 'SELL']:
                        logger.info(f"🎯 SIGNAL DETECTED: {symbol} [{signal_res['signal']}] Score: {signal_res['score']}/5")
                        await self.notifier.send_signal_alert(symbol, signal_res)

                # Scan every 10 seconds
                await asyncio.sleep(10)

            except Exception as e:
                logger.error(f"Error in Agent Scanning Loop: {e}")
                await asyncio.sleep(5)

async def main():
    agent = CryptoAgentOrchestrator()
    await agent.initialize()
    await agent.run_scanning_loop()

if __name__ == "__main__":
    asyncio.run(main())