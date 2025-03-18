import asyncio
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import time
from datetime import datetime

from analysis_utils import *

# Replace with your bot token
TOKEN = "7876389744:AAFlaV8GwLgJV1waBDumi6mShqlcZNDq8b8"

# Replace with your trading API endpoint
TRADE_API_URL = "http://localhost:8000/trade"

# Replace with your Telegram user ID (optional, for private messages)
YOUR_TELEGRAM_CHAT_ID = 1458842927  # Replace with your chat ID

# Enable logging
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

data_agent = DataAgent()


def get_current_price():
    data = data_agent.get_ohlc_data("NIFTY", Interval.in_5_minute, 1, "NSE")
    current_price = data[0]["close"]
    return current_price

async def get_option_chain():
    current_price = get_current_price()
    NSE_URL = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Referer": "https://www.nseindia.com/"
    }

    """Fetches Nifty Option Chain data from NSE India and prints it."""
    session = requests.Session()
    
    # Make initial request to set cookies
    session.get("https://www.nseindia.com", headers=HEADERS)

    # Fetch Option Chain data
    response = session.get(NSE_URL, headers=HEADERS)

    if response.status_code != 200:
        print("⚠️ Failed to fetch data. Status Code:", response.status_code)
        return
    data = response.json()
    
    # Extract option chain records
    records = data["filtered"]["data"]
    
# get the call and put data for 2 strike prices above and below the current price
    call_data = []
    put_data = []
    for record in records:
        if "CE" in record and "PE" in record:
            call_data.append(record)
            put_data.append(record)
    # sort the call and put data by strike price
    call_data.sort(key=lambda x: x["strikePrice"])
    put_data.sort(key=lambda x: x["strikePrice"])
    # get the 2 strike prices above and below the current price
    current_price = get_current_price()
    # Round current price to nearest 50
    base_strike = round(current_price / 50) * 50
    
    # Get 3 strikes above and 3 below
    strikes_needed = [base_strike + (i * 50) for i in range(-3, 4)]
    
    filtered_call_data = []
    filtered_put_data = []
    
    for record in call_data:
        if record["strikePrice"] in strikes_needed:
            filtered_call_data.append(record)
            
    for record in put_data:
        if record["strikePrice"] in strikes_needed:
            filtered_put_data.append(record)
            
    formatted_data = []
    for record in filtered_call_data:
        formatted_data.append({
            'strike': record['strikePrice'],
            'ce_price': record['CE']['lastPrice'],
            'pe_price': record['PE']['lastPrice']
        })
    return formatted_data


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message when user starts the bot."""
    await update.message.reply_text("Welcome! I will notify you when a trade signal is triggered.")

async def send_trade_signal(context: ContextTypes.DEFAULT_TYPE, condition: str) -> None:
    """Sends a trade signal with Yes/No buttons."""
    option_chain = await get_option_chain()
    
    keyboard = []
    for option in option_chain:
        strike = option['strike']
        ce_price = option['ce_price']
        pe_price = option['pe_price']
        keyboard.append([
            InlineKeyboardButton(f"CE {strike} @ {ce_price}", callback_data=f"ce_{strike}"),
            InlineKeyboardButton(f"PE {strike} @ {pe_price}", callback_data=f"pe_{strike}")
        ])
    keyboard.append([
        InlineKeyboardButton("❌ Cancel", callback_data="cancel")
    ])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    print(option_chain)

    await context.bot.send_message(
        chat_id=YOUR_TELEGRAM_CHAT_ID,
        text=f"📈 Trade Signal Alert! {condition} NIFTY. Execute trade?",
        reply_markup=reply_markup
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles Yes/No button clicks and sends the decision to the trading system."""
    query = update.callback_query
    await query.answer()

    decision = query.data  # 'yes' or 'no'
    
    # Send the response to the trading application
    response = requests.post(TRADE_API_URL, json={"trade": "BTC/USDT", "action": decision})
    
    if response.status_code == 200:
        await query.edit_message_text(text=f"Trade decision recorded: {decision.upper()}")
    else:
        await query.edit_message_text(text="❌ Error sending trade decision.")

async def check_market_condition(application: Application) -> None:
    """Continuously checks for trade conditions and sends notifications when needed."""
    while True:
        # 🔥 Replace this with your actual condition check (e.g., get live market data)
        condition = some_market_check_function()
        if condition is not None:
            logger.info("Trade condition met! Sending notification...")
            await send_trade_signal(application, condition)
            time.sleep(60)
            # wait till time is not multiple of 5
            while datetime.now().minute % 5 != 0:
                await asyncio.sleep(10)
            time.sleep(10)
        else:
            logger.info("No trade condition met. Waiting for next check...")
        await asyncio.sleep(10)  # Check condition every 10 seconds (adjust as needed)

def some_market_check_function() -> bool:
    """Dummy function to simulate a market condition check. Replace with real logic."""
    # this will read market condition from a txt file
    return "buy @18000"
    with open("market_condition.txt", "r") as file:
        market_condition = file.read()
    if "buy" in market_condition or "sell" in market_condition:
        return market_condition
    else:
        return None

def main():
    """Start the bot."""
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback))

    # ✅ Schedule the market condition checker to run every 10 seconds
    app.job_queue.run_repeating(check_market_condition, interval=10, first=0)

    logger.info("Bot started...")
    app.run_polling()


if __name__ == "__main__":
    main()
