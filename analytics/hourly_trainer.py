import time
import threading
import sqlite3
import json
from database.db import get_weights, update_weight, DB_PATH

def run_hourly_training():
    """
    සෑම පැයකට වරක් පසුගිය Trades අධ්‍යයනය කර
    Accuracy එක වැඩි කිරීමට Factor Weights Auto-Adjust කරයි.
    """
    while True:
        try:
            print("🧠 [Sparrow AI] Starting Hourly Self-Training Loop...")
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # පසුගිය පැය 24 ඇතුළත සිදු වූ Trades ගන්න
            cursor.execute("SELECT outcome, trigger_reasons FROM trade_history ORDER BY id DESC LIMIT 50")
            trades = cursor.fetchall()
            conn.close()

            if len(trades) >= 5: # අවම වශයෙන් Trades 5ක් වත් තිබිය යුතුය
                weights = get_weights()
                
                for outcome, reasons_json in trades:
                    reasons = json.loads(reasons_json)
                    reasons_str = " ".join(reasons)

                    # Trade එක SL (Loss) වුණා නම්, එම Trade එකට දායක වූ Indicator වල Weight එක අඩු කරයි
                    if outcome == 'SL':
                        if "RSI" in reasons_str or "Momentum" in reasons_str:
                            weights['rsi_macd'] = max(0.5, weights.get('rsi_macd', 1.0) - 0.02)
                        if "EMA 200" in reasons_str:
                            weights['ema_trend'] = max(0.5, weights.get('ema_trend', 1.0) - 0.02)
                            
                    # Trade එක TP (Profit) වුණා නම්, සාර්ථක වූ Indicator වල Weight එක වැඩි කරයි
                    elif outcome == 'TP':
                        if "SMC" in reasons_str or "Order Block" in reasons_str:
                            weights['smc_ob'] = min(2.5, weights.get('smc_ob', 1.5) + 0.02)
                        if "Volume POC" in reasons_str:
                            weights['volume_poc'] = min(2.5, weights.get('volume_poc', 1.2) + 0.02)

                # අලුත් Weights Database එකට Save කිරීම
                for f, w in weights.items():
                    update_weight(f, w)
                
                print("✅ [Sparrow AI] Hourly Self-Training Completed! Weights Optimized.")
            else:
                print("ℹ️ [Sparrow AI] Not enough trade history yet for training.")

        except Exception as e:
            print(f"❌ Training Error: {e}")

        # පැයක් (තත්පර 3600) Sleep කර නැවත Run වේ
        time.sleep(3600)

def start_background_training():
    # Background Thread එකක් ලෙස Run කිරීම
    training_thread = threading.Thread(target=run_hourly_training, daemon=True)
    training_thread.start()