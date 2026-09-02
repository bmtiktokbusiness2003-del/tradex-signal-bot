import sys
import random
import asyncio
import requests
from telegram import Bot

# ==========================================
# ⚙️ CONFIGURATION
# ==========================================
BOT_TOKEN = "8630297168:AAGqMdxODDoGXuVO9AQcIceQOt6-MaRutc4"  # 👈 ඔයාගේ Telegram Bot Token එක
CHANNEL_ID = -1003962679297                  # 👈 Channel ID එක
SITE_API_URL = "https://tradex.forex/api/update-package-profit"
BOT_SECRET_KEY = "TRADEX_SECRET_BOT_KEY_2026"

IMAGE_1 = "signal1.jpg.png"
IMAGE_2 = "signal2.jpg.png"
IMAGE_3 = "signal3.jpg.png"

# 🔄 Entry time (පැය 2) ඉවර වුණාම Auto-Reset වන පරණ Standard Profit % values:
RESET_PROFIT_MAP = {
    "1": 0.7,  # SOL Package Standard %
    "2": 1.0,  # Gold Package Standard %
    "3": 0.9   # BTC Package Standard %
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
    "1_warning": {"type": "warning", "image": IMAGE_1},
    "1_main": {
        "type": "main", 
        "image": IMAGE_1,
        "pair": "SOL (Solana)",
        "open_time": "07:00 AM UTC To 09:00 AM UTC",
        "start_time": "07:00 AM UTC"
    },
    "1_reset": {"type": "reset", "signal_id": "1"},

    # 🟡 Gold (Package ID: 2)
    "2_warning": {"type": "warning", "image": IMAGE_2},
    "2_main": {
        "type": "main", 
        "image": IMAGE_2,
        "pair": "XAU/USD (Gold)",
        "open_time": "10:00 AM UTC To 12:00 PM UTC",
        "start_time": "10:00 AM UTC"
    },
    "2_reset": {"type": "reset", "signal_id": "2"},

    # 🔵 BTC (Package ID: 3)
    "3_warning": {"type": "warning", "image": IMAGE_3},
    "3_main": {
        "type": "main", 
        "image": IMAGE_3,
        "pair": "BTC (Bitcoin)",
        "open_time": "02:00 PM UTC To 04:00 PM UTC",
        "start_time": "02:00 PM UTC"
    },
    "3_reset": {"type": "reset", "signal_id": "3"}
}

def sync_site_profit(signal_id, profit_value):
    headers = {
        'X-BOT-SECRET': BOT_SECRET_KEY,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }
    payload = {'signal_id': signal_id, 'profit': profit_value}
    
    # Retry Mechanism to prevent network timeout issues
    for attempt in range(3):
        try:
            res = requests.post(SITE_API_URL, json=payload, headers=headers, timeout=25)
            print(f"Site Sync Status: {res.status_code} - {res.text}")
            return True
        except Exception as e:
            print(f"Attempt {attempt+1} - Site Sync Error: {e}")
    return False

async def send_telegram_post(key):
    cfg = CONFIGS.get(key)
    
    if not cfg:
        print("Invalid Signal Key!")
        return

    # 🔄 ENTRY WINDOW EXPIRED RESET (පරණ තිබුණු Normal % එකට Revert වීම)
    if cfg["type"] == "reset":
        sig_id = cfg['signal_id']
        old_profit = RESET_PROFIT_MAP.get(sig_id, 0.5)
        print(f"Executing 2-Hour Reset for Package ID: {sig_id} -> Reverting back to {old_profit}%")
        sync_site_profit(sig_id, old_profit)
        return

    bot = Bot(token=BOT_TOKEN)

    if cfg["type"] == "warning":
        caption_text = WARNING_TEMPLATE
    else:
        # Profit Randomization (0.9% - 2.0%)
        random_profit = round(random.uniform(0.9, 2.0), 1)
        caption_text = get_main_signal_text(
            pair=cfg["pair"],
            open_time=cfg["open_time"],
            start_time=cfg["start_time"],
            profit=random_profit
        )

        # Site DB Auto-Sync (Live Profit Setting)
        signal_num = key.split('_')[0]
        sync_site_profit(signal_num, random_profit)

    # Send to Telegram Channel (Forced UTF-8 + High Timeout Limits)
    try:
        with open(cfg["image"], 'rb') as photo:
            await bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=photo,
                caption=caption_text.encode('utf-8').decode('utf-8'),
                read_timeout=60,
                write_timeout=60,
                connect_timeout=60,
                pool_timeout=60
            )
        print(f"Post [{key}] Sent Successfully!")
    except Exception as e:
        print(f"Telegram Post Error [{key}]: {e}")

if __name__ == "__main__":
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
        
    if len(sys.argv) > 1:
        run_key = sys.argv[1]
        asyncio.run(send_telegram_post(run_key))
