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
parser.add_argument("--years", dest='years',  help="Number of years to track")
parser.add_argument("--stocks", dest='stocks',  help="Stocks to track take from the keys in all stocks variable in config")
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
    number_of_years_to_track = int(args.years)
    
    data_agent = DataAgent()
    num_retry = 3
    percentage_positive_map = {}
    stocks_tracked = []
    stocks = all_stocks[args.stocks]
    for i in tqdm(range(len(stocks))):
        retry_count = 0
        percentage_change = []
        stock = stocks[i]
        index_error = False
        while retry_count < num_retry:
            try:
                data = data_agent.get_ohlc_data(stock, Interval.in_monthly, 12*number_of_years_to_track + 1)
                stocks_tracked.append(stock)
                break
            except Exception as error:
                if isinstance(error, IndexError):
                    print(f'skipping {stock}', error)
                    index_error = True
                    break
                print(type(error))
                retry_count += 1
                print(error)
                print('retrying after 3...')
                time.sleep(3)
                if retry_count==num_retry:
                    print(f'skipping {stock}')
        if retry_count==num_retry or index_error:
            continue
        num_positive = 0
        for i in range(number_of_years_to_track):
            temp = i * 12
            change = (data[temp+1]['close'] - data[temp]['close'])/data[temp]['close'] * 100
            percentage_change.append(change)
            if change > 0:
                num_positive += 1
        percentage_positive = num_positive/number_of_years_to_track
        # print(percentage_change)
        percentage_positive_map[stock] = percentage_positive

    stocks_tracked.sort(key=lambda x:percentage_positive_map[x])
    for s in stocks_tracked:
        print(s, percentage_positive_map[s])