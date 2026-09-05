import sys
import random
import asyncio
import requests
from telegram import Bot

# ==========================================
# ⚙️ CONFIGURATION
# ==========================================
BOT_TOKEN = "8630297168:AAGqMdxODDoGXuVO9AQcIceQOt6-MaRutc4"
CHANNEL_ID = -1003962679297
SITE_API_URL = "https://tradex.forex/api/update-package-profit"
BOT_SECRET_KEY = "TRADEX_SECRET_BOT_KEY_2026"

IMAGE_1 = "signal1.jpg.png.png"
IMAGE_2 = "signal2.jpg.png.png"
IMAGE_3 = "signal3.jpg.png.png"

# 🔄 Entry time (පැය 2) ඉවර වුණාම Auto-Reset වන Standard Profit % values:
RESET_PROFIT_MAP = {
    1: 0.7,   # SOL Package Standard Default %
    2: 1.0,   # Gold Package Standard Default %
    3: 0.9    # BTC Package Standard Default %
}

# ==========================================
# 📄 TEMPLATES
# ==========================================
WARNING_TEMPLATE = """🚨 IMPORTANT WARNING — COPY TRADE SIGNAL ALERT — 1 HOUR TO GO!

The Copy Trade Signal will be released within approximately 1 hour.

IMPORTANT:
Once the signal is released, you will have ONLY 2 HOURS to enter the Copy Trade. DO NOT WAIT UNTIL THE LAST MINUTE.
If you miss the 2-hour entry window, you may miss this trading opportunity.

PROFIT CYCLE:
The trade is planned to run for up to 24 hours, with profit targeted within that period.

AFFILIATE INCOME:
Eligible affiliate income will be credited at the same time as the applicable profit distribution.

GET READY NOW.
Check your account → Prepare your capital → Stay connected → WAIT FOR THE SIGNAL

2-HOUR ENTRY WINDOW — DON’T MISS IT!"""

def get_main_signal_text(pair, open_time, start_time, profit):
    return f"""🚨 GET READY TRADEX COPY TRADING SIGNAL

Trade Open Time 
{open_time}

━━━━━━━━━━━━━━━━━━
📊 TRADING SIGNAL
━━━━━━━━━━━━━━━━━━
Trading Pair: {pair}
Copy Trade Starting Time: {start_time}
Expected Profit: {profit}%

━━━━━━━━━━━━━━━━━━
⚡ SIGNAL STATUS: ACTIVE
━━━━━━━━━━━━━━━━━━

TRADEX BROKERING & COPY TRADING
Trade Smarter. Copy Better.

Trade Open Two Hours...."""

CONFIGS = {
    # 🔴 SOL (Package ID: 1)
    "1_warning": {"type": "warning"},
    "1_main": {
        "type": "main", 
        "image": IMAGE_1,
        "pair": "SOL (Solana)",
        "open_time": "07:00 AM UTC To 09:00 AM UTC",
        "start_time": "07:00 AM UTC",
        "profit_range": (1.2, 1.8)
    },
    "1_reset": {"type": "reset", "signal_id": 1},

    # 🟡 Gold (Package ID: 2)
    "2_warning": {"type": "warning"},
    "2_main": {
        "type": "main", 
        "image": IMAGE_2,
        "pair": "XAU/USD (Gold)",
        "open_time": "10:00 AM UTC To 12:00 PM UTC",
        "start_time": "10:00 AM UTC",
        "profit_range": (1.5, 2.5)
    },
    "2_reset": {"type": "reset", "signal_id": 2},

    # 🔵 BTC (Package ID: 3)
    "3_warning": {"type": "warning"},
    "3_main": {
        "type": "main", 
        "image": IMAGE_3,
        "pair": "BTC (Bitcoin)",
        "open_time": "02:00 PM UTC To 04:00 PM UTC",
        "start_time": "02:00 PM UTC",
        "profit_range": (1.2, 2.0)
    },
    "3_reset": {"type": "reset", "signal_id": 3}
}

def sync_site_profit(signal_id, profit_value):
    headers = {
        'X-BOT-SECRET': BOT_SECRET_KEY,
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }
    
    payload = {
        'signal_id': int(signal_id), 
        'profit': float(profit_value)
    }
    
    for attempt in range(3):
        try:
            res = requests.post(SITE_API_URL, json=payload, headers=headers, timeout=25)
            print(f"Site Sync Status: {res.status_code} - {res.text}")
            if res.status_code == 200:
                return True
        except Exception as e:
            print(f"Attempt {attempt+1} - Site Sync Error: {e}")
    return False

async def send_telegram_post(key):
    cfg = CONFIGS.get(key)
    
    if not cfg:
        print(f"Invalid Signal Key: '{key}'")
        return

    # 🔄 2-HOUR WINDOW EXPIRED RESET (පරණ තිබුණු Normal Default % එකට Revert වීම)
    if cfg["type"] == "reset":
        sig_id = int(cfg['signal_id'])
        default_profit = RESET_PROFIT_MAP.get(sig_id, 1.0)
        print(f"Executing 2-Hour Reset for Package ID: {sig_id} -> Reverting back to default {default_profit}%")
        sync_site_profit(sig_id, default_profit)
        return

    bot = Bot(token=BOT_TOKEN)

    # 🚨 WARNING MESSAGE (ONLY TEXT - NO PHOTO)
    if cfg["type"] == "warning":
        try:
            await bot.send_message(
                chat_id=CHANNEL_ID,
                text=WARNING_TEMPLATE,
                read_timeout=60,
                write_timeout=60,
                connect_timeout=60
            )
            print(f"Warning Post [{key}] Sent Successfully (Text Only)!")
        except Exception as e:
            print(f"Telegram Post Error [{key}]: {e}")
        return

    # 📊 MAIN SIGNAL MESSAGE (WITH IMAGE + LIVE SITE SYNC)
    min_p, max_p = cfg.get("profit_range", (1.2, 2.0))
    random_profit = round(random.uniform(min_p, max_p), 1)
    
    caption_text = get_main_signal_text(
        pair=cfg["pair"],
        open_time=cfg["open_time"],
        start_time=cfg["start_time"],
        profit=random_profit
    )

    # Site DB Auto-Sync (Live Profit Setting)
    signal_num = int(key.split('_')[0])
    sync_site_profit(signal_num, random_profit)

    # Send Photo + Text to Telegram Channel
    try:
        with open(cfg["image"], 'rb') as photo:
            await bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=photo,
                caption=caption_text,
                read_timeout=60,
                write_timeout=60,
                connect_timeout=60,
                pool_timeout=60
            )
        print(f"Main Signal Post [{key}] Sent Successfully with Image!")
    except Exception as e:
        print(f"Telegram Post Error [{key}]: {e}")

if __name__ == "__main__":
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
        
    if len(sys.argv) > 1:
        run_key = sys.argv[1]
        asyncio.run(send_telegram_post(run_key))
