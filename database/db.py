import sqlite3
import json
from datetime import datetime

DB_PATH = "sparrow_memory.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Trade Memory Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS trade_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT,
        side TEXT,
        entry_price REAL,
        exit_price REAL,
        outcome TEXT, -- 'TP' or 'SL'
        pnl_usdt REAL,
        trigger_reasons TEXT,
        timestamp DATETIME
    )
    """)
    
    # 2. Dynamic Weights Memory Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS factor_weights (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        factor_name TEXT UNIQUE,
        weight REAL,
        updated_at DATETIME
    )
    """)
    
    # Default Weights
    default_weights = {
        'smc_ob': 1.5,
        'liquidity_sweep': 1.5,
        'ema_trend': 1.0,
        'rsi_macd': 1.0,
        'volume_poc': 1.2,
        'funding_rate': 0.8
    }
    
    for factor, weight in default_weights.items():
        cursor.execute("""
        INSERT OR IGNORE INTO factor_weights (factor_name, weight, updated_at) 
        VALUES (?, ?, ?)
        """, (factor, weight, datetime.now()))
        
    conn.commit()
    conn.close()

def save_trade(symbol, side, entry, exit_price, outcome, pnl, reasons):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO trade_history (symbol, side, entry_price, exit_price, outcome, pnl_usdt, trigger_reasons, timestamp)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (symbol, side, entry, exit_price, outcome, pnl, json.dumps(reasons), datetime.now()))
    conn.commit()
    conn.close()

def get_weights():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT factor_name, weight FROM factor_weights")
    weights = dict(cursor.fetchall())
    conn.close()
    return weights

def update_weight(factor_name, new_weight):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE factor_weights SET weight = ?, updated_at = ? WHERE factor_name = ?
    """, (new_weight, datetime.now(), factor_name))
    conn.commit()
    conn.close()