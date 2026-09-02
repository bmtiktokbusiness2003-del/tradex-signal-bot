import sys
import random
import asyncio
import requests
from telegram import Bot

# ==========================================
# ⚙️ CONFIGURATION
# ==========================================
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN_HERE"  # 👈 ඔයාගේ Bot Token එක මෙතැනට දාන්න
CHANNEL_ID = -1003962679297                  # 👈 Channel ID එක
SITE_API_URL = "https://tradex.forex/api/update-package-profit"
BOT_SECRET_KEY = "TRADEX_SECRET_BOT_KEY_2026"

IMAGE_1 = "signal1.jpg"
IMAGE_2 = "signal2.jpg"
IMAGE_3 = "signal3.jpg"

# ==========================================
# 📄 EXACT TEMPLATES
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

def get_main_signal_text(open_time, start_time, profit):
    return f"""GET READY TRADEX COPY TRADING SIGNAL

Trade Open Time 
{open_time}

━━━━━━━━━━━━━━━━━━
TRADING SIGNAL
━━━━━━━━━━━━━━━━━━
Trading Pair: BTC (Bitcoin)
Copy Trade Starting Time: {start_time}
Expected Profit: {profit}%

━━━━━━━━━━━━━━━━━━
SIGNAL STATUS: ACTIVE
━━━━━━━━━━━━━━━━━━

TRADEX BROKERING & COPY TRADING
Trade Smarter. Copy Better.

Trade Open Two Hours...."""

CONFIGS = {
    "1_warning": {"type": "warning", "image": IMAGE_1},
    "1_main": {
        "type": "main", "image": IMAGE_1,
        "open_time": "07:00 AM UTC To 09:00 AM UTC",
        "start_time": "07:00 AM UTC"
    },
    "2_warning": {"type": "warning", "image": IMAGE_2},
    "2_main": {
        "type": "main", "image": IMAGE_2,
        "open_time": "10:00 AM UTC To 12:00 PM UTC",
        "start_time": "10:00 AM UTC"
    },
    "3_warning": {"type": "warning", "image": IMAGE_3},
    "3_main": {
        "type": "main", "image": IMAGE_3,
        "open_time": "02:00 PM UTC To 04:00 PM UTC",
        "start_time": "02:00 PM UTC"
    }
}

async def send_telegram_post(key):
    bot = Bot(token=BOT_TOKEN)
    cfg = CONFIGS.get(key)
    
    if not cfg:
        print("Invalid Signal Key!")
        return

    if cfg["type"] == "warning":
        caption_text = WARNING_TEMPLATE
    else:
        # Profit Auto-Randomization (0.9% - 2.8% අතර)
        random_profit = round(random.uniform(0.9, 2.8), 1)
        caption_text = get_main_signal_text(
            open_time=cfg["open_time"],
            start_time=cfg["start_time"],
            profit=random_profit
        )

        # 🌐 Site DB Auto-Sync (Main Signal එක යන වෙලාවට)
        signal_num = key.split('_')[0]
        try:
            headers = {'X-BOT-SECRET': BOT_SECRET_KEY}
            payload = {'signal_id': signal_num, 'profit': random_profit}
            res = requests.post(SITE_API_URL, json=payload, headers=headers, timeout=10)
            print(f"Site Sync Status: {res.status_code} - {res.text}")
        except Exception as e:
            print(f"Site Sync Error: {e}")

    # Send to Telegram Channel
    try:
        with open(cfg["image"], 'rb') as photo:
            await bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=photo,
                caption=caption_text
            )
        print(f"Post [{key}] Sent Successfully!")
    except Exception as e:
        print(f"Telegram Post Error [{key}]: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_key = sys.argv[1]
        asyncio.run(send_telegram_post(run_key))
