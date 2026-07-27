import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import aiohttp
import logging
from config.settings import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class TelegramAlertNotifier:
    def __init__(self):
        self.token = TELEGRAM_BOT_TOKEN
        self.chat_id = TELEGRAM_CHAT_ID
        self.base_url = f"https://api.telegram.org/bot{self.token}/sendMessage"

    async def send_signal_alert(self, symbol: str, signal_data: dict):
        """
        Confluence Trigger එකක් ලැබුණු පසු Telegram එකට Signal එක Formatted Message එකක් ලෙස යවයි.
        $10 Margin x 10x Leverage Position Calculation ද සහිතයි.
        """
        if not self.token or not self.chat_id:
            logger.warning("Telegram Bot Token or Chat ID missing in .env! Skipping alert dispatch.")
            return

        signal = signal_data.get('signal', 'NEUTRAL')
        score = signal_data.get('score', 0)
        price = signal_data.get('price', 0.0)
        atr = signal_data.get('atr', price * 0.01)
        reasons = signal_data.get('reasons', [])

        # Futures Calculation Setup
        margin = 10.0      # $10
        leverage = 10      # 10x
        position_size = margin * leverage  # $100 total position size

        # Risk Management Rules (Stop Loss & Take Profit ATR මත)
        if signal == 'BUY':
            emoji = "🟢"
            sl = price - (atr * 1.5)
            tp1 = price + (atr * 2.0)
            tp2 = price + (atr * 4.0)
            
            # PnL Calculations for BUY
            tp1_pnl = position_size * ((tp1 - price) / price)
            tp2_pnl = position_size * ((tp2 - price) / price)
            sl_pnl = position_size * ((price - sl) / price)  # Loss amount
        else:
            emoji = "🔴"
            sl = price + (atr * 1.5)
            tp1 = price - (atr * 2.0)
            tp2 = price - (atr * 4.0)
            
            # PnL Calculations for SELL
            tp1_pnl = position_size * ((price - tp1) / price)
            tp2_pnl = position_size * ((price - tp2) / price)
            sl_pnl = position_size * ((sl - price) / price)  # Loss amount

        reasons_formatted = "\n".join([f"• {r}" for r in reasons])

        # Formatted Telegram Message
        message = (
            f"{emoji} **NEW TRADING SIGNAL DETECTED** {emoji}\n\n"
            f"📌 **Pair:** #{symbol}\n"
            f"⚡ **Action:** {signal}\n"
            f"📊 **Confluence Score:** {score}/5\n"
            f"💵 **Entry Price:** `${price:.4f}`\n\n"
            f"🎯 **Target 1 (TP1):** `${tp1:.4f}` | 💵 Profit: **+${tp1_pnl:.2f}**\n"
            f"🎯 **Target 2 (TP2):** `${tp2:.4f}` | 💵 Profit: **+${tp2_pnl:.2f}**\n"
            f"🛡️ **Stop Loss (SL):** `${sl:.4f}` | 🔻 Loss: **-${sl_pnl:.2f}**\n\n"
            f"💰 *[ Calculated for $10 Margin | 10x Leverage ]*\n\n"
            f"📝 **Confluence Factors:**\n"
            f"{reasons_formatted}\n\n"
            f"🤖 *Sparrow AI Institutional Agent*"
        )

        payload = {
            'chat_id': self.chat_id,
            'text': message,
            'parse_mode': 'Markdown'
        }

        try:
            # SSL Verification bypass enabled for smooth delivery
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
                async with session.post(self.base_url, json=payload) as resp:
                    if resp.status == 200:
                        logger.info(f"Telegram alert dispatched successfully for {symbol} [{signal}]!")
                    else:
                        logger.error(f"Failed to send Telegram alert: {await resp.text()}")
        except Exception as e:
            logger.error(f"Telegram Dispatch Error: {e}")

if __name__ == "__main__":
    import asyncio
    
    # Quick Test Run
    async def test_telegram():
        notifier = TelegramAlertNotifier()
        sample_signal = {
            'signal': 'BUY',
            'score': 4,
            'price': 67500.50,
            'atr': 450.0,
            'reasons': [
                "Price inside Bullish Order Block",
                "Bullish FVG Imbalance Present",
                "Price above EMA 200 (Overall Uptrend)",
                "Order Book Depth Heavy Buy Pressure"
            ]
        }
        await notifier.send_signal_alert("BTCUSDT", sample_signal)

    asyncio.run(test_telegram())