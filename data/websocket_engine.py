import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
import json
import logging
import websockets
from config.settings import TOP_30_PAIRS

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class BinanceWebSocketManager:
    def __init__(self, symbols=None):
        self.symbols = [s.lower() for s in (symbols or TOP_30_PAIRS)]
        self.ws_url = "wss://stream.binance.com:9443/ws"
        self.live_prices = {}
        self.live_orderbook = {}
        self.is_running = False

    def _build_stream_url(self) -> str:
        """
        Top 30 Pairs වල Ticker + Order Book (Depth 10) streams සකස් කරයි.
        """
        streams = []
        for symbol in self.symbols:
            streams.append(f"{symbol}@ticker")        # Live Price & 24h Stats
            streams.append(f"{symbol}@depth10@100ms")  # Top 10 Bids/Asks Order Book
        
        stream_path = "/".join(streams)
        return f"wss://stream.binance.com:9443/stream?streams={stream_path}"

    async def connect(self):
        """
        WebSocket Stream එක ආරම්භ කර Auto-reconnect පහසුකම ලබා දෙයි.
        """
        url = self._build_stream_url()
        self.is_running = True
        logger.info(f"Connecting to Binance Multi-WebSocket Stream for {len(self.symbols)} pairs...")

        while self.is_running:
            try:
                async with websockets.connect(url, ping_interval=20, ping_timeout=10) as websocket:
                    logger.info("⚡ WebSocket Connection Established! Live streaming data...")
                    
                    while self.is_running:
                        message = await websocket.recv()
                        data = json.loads(message)
                        self._process_message(data)

            except Exception as e:
                logger.error(f"WebSocket disconnected: {e}. Reconnecting in 5 seconds...")
                await asyncio.sleep(5)

    def _process_message(self, data: dict):
        """
        ලැබෙන Real-time Data processing කර Memory එකේ තබයි.
        """
        if 'data' not in data:
            return

        stream_name = data.get('stream', '')
        payload = data.get('data', {})

        # Ticker Data (Live Price)
        if '@ticker' in stream_name:
            symbol = payload.get('s')
            price = float(payload.get('c', 0))
            volume = float(payload.get('v', 0))
            high = float(payload.get('h', 0))
            low = float(payload.get('l', 0))
            
            self.live_prices[symbol] = {
                'price': price,
                'volume': volume,
                'high': high,
                'low': low
            }

        # Order Book Data (Depth 10)
        elif '@depth10' in stream_name:
            symbol = stream_name.split('@')[0].upper()
            bids = payload.get('bids', [])  # Buy orders
            asks = payload.get('asks', [])  # Sell orders
            
            self.live_orderbook[symbol] = {
                'bids': [[float(p), float(q)] for p, q in bids],
                'asks': [[float(p), float(q)] for p, q in asks]
            }

    def stop(self):
        self.is_running = False

async def main():
    # Test Run
    ws_manager = BinanceWebSocketManager(symbols=["BTCUSDT", "ETHUSDT", "SOLUSDT"])
    
    # Background එකේ stream එක run කිරීමට task එකක් සාදයි
    asyncio.create_task(ws_manager.connect())
    
    # තත්පර 3ක් රැඳී සිට Live Data Print කර බලමු
    await asyncio.sleep(3)
    
    logger.info("--- Live WebSocket Prices Test ---")
    for symbol, data in ws_manager.live_prices.items():
        print(f"🪙 {symbol}: ${data['price']} | Vol: {data['volume']}")
    
    ws_manager.stop()

if __name__ == "__main__":
    asyncio.run(main())