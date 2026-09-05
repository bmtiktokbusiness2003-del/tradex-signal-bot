import sys
import random
import asyncio
import requests
import threading
from telegram import Bot

# ==========================================
# ⚙️ CONFIGURATION
# ==========================================
BOT_TOKEN = "8630297168:AAGqMdxODDoGXuVO9AQcIceQOt6-MaRutc4"
CHANNEL_ID = -1003962679297
SITE_API_URL = "https://tradex.forex/api/update-package-profit"
API_KEY = "TradexAutoSync2026SecureKey"

IMAGE_1 = "signal1.jpg.png.png"
IMAGE_2 = "signal2.jpg.png.png"
IMAGE_3 = "signal3.jpg.png.png"

# Database Plan Names Mapping
PACKAGE_MAP = {
    1: "SOL",
    2: "Gold",
    3: "BTC"
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
        "signal_id": 1,
        "profit_range": (0.50, 1.20)  # STRICT SAFETY LIMIT (0.5% - 1.2%)
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
        "signal_id": 2,
        "profit_range": (0.50, 1.20)  # STRICT SAFETY LIMIT (0.5% - 1.2%)
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
        "signal_id": 3,
        "profit_range": (0.50, 1.20)  # STRICT SAFETY LIMIT (0.5% - 1.2%)
    },
    "3_reset": {"type": "reset", "signal_id": 3}
}

def sync_site_profit(package_name, profit_value=0, action="update"):
    """
    STRICT API SYNC WITH DYNAMIC PRE-SIGNAL RESTORE
    """
    profit_float = float(profit_value)

    # SAFETY CAPPING FILTER (0.5% - 1.2%)
    if action == "update":
        if profit_float < 0.50:
            profit_float = 0.50
        elif profit_float > 1.20:
            profit_float = 1.20

    headers = {
        'Content-Type': 'application/json',
        'X-Api-Key': API_KEY,
        'User-Agent': 'Mozilla/5.0'
    }
    
    payload = {
        'plan_name': str(package_name), 
        'profit': round(profit_float, 2),
        'action': action,
        'api_key': API_KEY
    }
    
    for attempt in range(3):
        try:
            res = requests.post(SITE_API_URL, json=payload, headers=headers, timeout=25)
            print(f"[{action.upper()}] Site Sync Status for {package_name}: {res.status_code} - {res.text}")
            if res.status_code == 200:
                return True
        except Exception as e:
            print(f"Attempt {attempt+1} - Site Sync Error for {package_name}: {e}")
    return False

def schedule_auto_reset(package_name, delay_seconds=7200):
    """
    2-HOUR (7200 Seconds) AUTO RESET TIMER
    """
    def do_reset():
        print(f"⏰ [2-HOUR TIMER EXPIRED] Restoring '{package_name}' back to pre-signal Admin rate.")
        sync_site_profit(package_name, profit_value=0, action="reset")

    timer = threading.Timer(delay_seconds, do_reset)
    timer.daemon = True
    timer.start()
    print(f"⏳ Auto-reset timer scheduled for '{package_name}' in {delay_seconds/3600} hours.")

async def send_telegram_post(key):
    cfg = CONFIGS.get(key)
    
    if not cfg:
        print(f"Invalid Signal Key: '{key}'")
        return

    # 🔄 MANUAL RESET CALL VIA ARGUMENT
    if cfg["type"] == "reset":
        sig_id = int(cfg['signal_id'])
        pkg_name = PACKAGE_MAP.get(sig_id, "Gold")
        print(f"Executing Manual Reset to Admin Rate for: {pkg_name}")
        sync_site_profit(pkg_name, profit_value=0, action="reset")
        return

    bot = Bot(token=BOT_TOKEN)

    # 🚨 WARNING MESSAGE (ONLY TEXT)
    if cfg["type"] == "warning":
        try:
            await bot.send_message(
                chat_id=CHANNEL_ID,
                text=WARNING_TEMPLATE,
                read_timeout=60,
                write_timeout=60,
                connect_timeout=60
            )
            print(f"Warning Post [{key}] Sent Successfully!")
        except Exception as e:
            print(f"Telegram Post Error [{key}]: {e}")
        return

    # 📊 MAIN SIGNAL MESSAGE
    sig_id = cfg["signal_id"]
    package_name = PACKAGE_MAP.get(sig_id, "Gold")

    # Generate Safety Cap Profit (Strictly 0.5% - 1.2%)
    min_p, max_p = cfg.get("profit_range", (0.50, 1.20))
    random_profit = round(random.uniform(min_p, max_p), 2)
    
    caption_text = get_main_signal_text(
        pair=cfg["pair"],
        open_time=cfg["open_time"],
        start_time=cfg["start_time"],
        profit=random_profit
    )

    # 1. Update Signal Profit (And automatically backup Admin's current rate)
    sync_site_profit(package_name, random_profit, action="update")

    # 2. Schedule 2-Hour Auto Reset Timer (7200 Seconds)
    schedule_auto_reset(package_name, delay_seconds=7200)

    # 3. Post to Telegram Channel
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
