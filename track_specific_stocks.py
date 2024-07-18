from analysis_utils import *
from trade_utils import *
from tvDatafeed import Interval
from config import *
import time
from datetime import date, datetime, timedelta
import os
from pathlib import Path
from tqdm import tqdm
import pandas as pd
import sys
from argparse import ArgumentParser
parser = ArgumentParser()

parser.add_argument("--server", dest='server', action='store_true', help="if code running on UTC timezone server")
args = parser.parse_args()

def preactions():
    make_log_file()

def make_log_file():
    file_path = f"{date.today()}.txt"
    if os.path.exists(file_path):
        return
    else:
        file = open(f'{date.today()}.txt', 'w')

def show_notification(title, message):
    if not args.server:
        os.system(f"osascript -e 'display notification \"{message}\" with title \"{title}\"'")

def alert(time, stock, last_tick, level, time_frame):
    message = f'{last_tick} near {time_frame} level {level}'
    log_message = f'{time}: {stock}'+message
    print(log_message, flush=True)
    file = open(f'{(date.today())}.txt', 'a')
    file.write(log_message+'\n')
    file.close()
    show_notification(stock, message)

def is_in_range(range: list, level):
    if level>= range[0] and level<= range[1]:
        return True
    return False

def has_breached_level(candle_low, candle_high, level):
    price_range = [level*0.999, level*1.001]
    if is_in_range(price_range, candle_high):
        return True
    elif is_in_range(price_range, candle_low):
        return True
    elif candle_low<price_range[0] and candle_high>price_range[1]:
        return True
    else:
        return False

def market_closed():
    # Get the current UTC time
    now_utc = datetime.utcnow()
    
    # IST is UTC + 5 hours 30 minutes
    ist_offset = timedelta(hours=5, minutes=30)
    
    # Convert current UTC time to IST
    now_ist = now_utc + ist_offset
    
    # Define the 3:30 PM time in IST
    three_thirty_pm_ist = now_ist.replace(hour=15, minute=30, second=0, microsecond=0)
    
    # Check if the current IST time is past 3:30 PM
    return now_ist > three_thirty_pm_ist


if __name__ == '__main__':
    how_close = 0.1/100 # 0.1 percent up and down
    print('started the tracking job', flush=True)
    print('running pre actions', flush=True)
    preactions()
    data_agent = DataAgent()

    try:
        while not market_closed():
            for i in list(temp_stock_to_track.keys()):
                stock = i
                crucial_prices = temp_stock_to_track[i]
                for time_frame in list(crucial_prices.keys()):
                    try:
                        data = data_agent.get_ohlc_data(stock, Interval.in_5_minute, 1)
                        five_min_high = data[0]['high']
                        five_min_low = data[0]['low']
                        last_tick = data[0]['close']

                        for crucial_price in crucial_prices[time_frame]:
                            if has_breached_level(five_min_low,five_min_high, crucial_price):
                                if args.server:
                                    time_now = datetime.now() + timedelta(hours=5, minutes=30)    
                                else:
                                    time_now = datetime.now()
                                alert(time_now.strftime('%H:%M'), i, last_tick, crucial_price, time_frame)
                    except Exception as e:
                        time.sleep(60)
                        continue
            
        exit(0)
    except KeyboardInterrupt:
        print("Keyboard interrupt detected. Exiting...", flush=True)
        exit(0)
