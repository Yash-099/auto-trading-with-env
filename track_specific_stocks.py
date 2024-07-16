from analysis_utils import *
from trade_utils import *
from tvDatafeed import Interval
from config import *
import time
from datetime import date, datetime
import os
from pathlib import Path
from tqdm import tqdm
import pandas as pd
def preactions():
    make_log_file()

def make_log_file():
    file_path = f"{date.today()}.txt"
    if os.path.exists(file_path):
        return
    else:
        file = open(f'{date.today()}.txt', 'w')

def show_notification(title, message):
    os.system(f"osascript -e 'display notification \"{message}\" with title \"{title}\"'")

def alert(time, stock, last_tick, level):
    message = f'{last_tick} near level {level}'
    log_message = f'{time}: {stock}'+message
    print(log_message)
    file = open(f'{(date.today())}.txt', 'a')
    file.write(log_message+'\n')
    file.close()
    show_notification(stock, message)

def is_in_range(range: list, level):
    if level>= range[0] and level<= range[1]:
        return True
    return False

def has_breached_level(candle_low, candle_high, level):
    price_range = [level*0.999, level*1.0001]
    if is_in_range(price_range, candle_high):
        return True
    elif is_in_range(price_range, candle_low):
        return True
    elif candle_low<price_range[0] and candle_high>price_range[1]:
        return True
    else:
        return False

if __name__ == '__main__':
    how_close = 0.1/100 # 0.1 percent up and down
    
    preactions()
    data_agent = DataAgent()

    try:
        while True:
            for i in list(temp_stock_to_track.keys()):
                crucial_prices = temp_stock_to_track[i]
                try:
                    data = data_agent.get_ohlc_data(i, Interval.in_5_minute, 1)
                    five_min_high = data[0]['high']
                    five_min_low = data[0]['low']
                    last_tick = data[0]['close']

                    for crucial_price in crucial_prices:
                        if has_breached_level(five_min_low,five_min_high, crucial_price):
                            alert(datetime.now().strftime('%H:%M:%S'), i, last_tick, crucial_price)
                except Exception as e:
                    time.sleep(3)
                    continue
            print('\n')
    except KeyboardInterrupt:
        print("Keyboard interrupt detected. Exiting...")
        exit(0)
