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

def get_the_fvgs():
    def convert_timestamp(obj):
        if isinstance(obj, pd.Timestamp):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")
    def parse_timestamp(data):
        if 'timestamp' in data:
            data['timestamp'] = pd.Timestamp(data['timestamp'])
        return data
    fvgs = FVGS()
    stock_daily_fvg_map = {}
    stock_weekly_fvg_map = {}
    stock_monthly_fvg_map = {}
    print('getting fvgs data (one time activity)')
    if Path('stock_daily_fvg_map.json').exists():
        with open('stock_daily_fvg_map.json', 'r') as f:
            stock_daily_fvg_map = json.load(f, object_hook=parse_timestamp)
        with open('stock_weekly_fvg_map.json', 'r') as f:
            stock_weekly_fvg_map = json.load(f, object_hook=parse_timestamp)
        with open('stock_monthly_fvg_map.json', 'r') as f:
            stock_monthly_fvg_map = json.load(f, object_hook=parse_timestamp)
    else:
        for i in tqdm(range(len(nifty_50_stocks))):
            stock_daily_fvg_map[nifty_50_stocks[i]] = fvgs.get_bisis(nifty_50_stocks[i], Interval.in_daily) + fvgs.get_sibis(nifty_50_stocks[i], Interval.in_daily)
            stock_weekly_fvg_map[nifty_50_stocks[i]] = fvgs.get_bisis(nifty_50_stocks[i], Interval.in_weekly) + fvgs.get_sibis(nifty_50_stocks[i], Interval.in_weekly)
            stock_monthly_fvg_map[nifty_50_stocks[i]] = fvgs.get_bisis(nifty_50_stocks[i], Interval.in_monthly) + fvgs.get_sibis(nifty_50_stocks[i], Interval.in_monthly)

    with open('stock_daily_fvg_map.json', 'w') as f:
        json.dump(stock_daily_fvg_map, f, default=convert_timestamp)
    with open('stock_weekly_fvg_map.json', 'w') as f:
        json.dump(stock_weekly_fvg_map, f, default=convert_timestamp)
    with open('stock_monthly_fvg_map.json', 'w') as f:
        json.dump(stock_monthly_fvg_map, f, default=convert_timestamp)


    print('got the fvgs data')
    return [stock_daily_fvg_map, stock_weekly_fvg_map, stock_monthly_fvg_map]


def make_log_file():
    file_path = f"{date.today()}.txt"
    if os.path.exists(file_path):
        return
    else:
        file = open(f'{date.today()}.txt', 'w')

def show_notification(title, message):
    os.system(f"osascript -e 'display notification \"{message}\" with title \"{title}\"'")

def alert(time, stock, action, fvg, last_tick, gap):
    message = f'{last_tick} action-{action}, reason - near {fvg}, GAP: {gap}'
    log_message = f'{time}: {stock}'+message
    print(log_message)
    file = open(f'{(date.today())}.txt', 'a')
    file.write(log_message+'\n')
    file.close()
    show_notification(stock, message)

def check_closeness_to_fvg(fvg, fvg_time_frame, last_tick, how_close, now):
    high = fvg['high']
    low = fvg['low']
    mid = (high + low)/2
    fvg_type = fvg['type']
    action = 'buy' if fvg_type == 'bisi' else 'sell'

    if abs(last_tick-high)/last_tick <= how_close:
        alert(now, i, action=action, fvg=f'{fvg_time_frame} fvg high {high}', last_tick=last_tick, gap=last_tick-high)

    if abs(last_tick-low)/last_tick <= how_close:
        alert(i, action=action, fvg=f'{fvg_time_frame} fvg low {low}', last_tick=last_tick, gap=last_tick-low)

    if abs(last_tick-mid)/last_tick <= how_close:
        alert(i, action=action, fvg=f'{fvg_time_frame} fvg mid {mid}', last_tick=last_tick, gap=last_tick-mid)

if __name__ == '__main__':
    how_close = 0.25/100 # 0.25 percent
    
    preactions()
    stock_daily_fvg_map, stock_weekly_fvg_map, stock_monthly_fvg_map = get_the_fvgs()
    data_agent = DataAgent()

    try:
        while True:
            for i in nifty_50_stocks:
                try:
                    data = data_agent.get_ohlc_data(i, Interval.in_1_hour, 2)
                    two_hrs_high = max(data[0]['high'], data[1]['high'])
                    two_hrs_low = min(data[0]['low'], data[1]['low'])
                    last_tick = data[1]['close']

                    ## if the current price is closer to low of 2hours then the price is near low and has come down overall in last 2hours
                    if abs(last_tick-two_hrs_high)>abs(last_tick-two_hrs_low):
                        action = 'buy'
                    else:
                        action = 'sell'

                    for daily_fvg in stock_daily_fvg_map[i]:
                        now = datetime.now().strftime('%H:%M:%S')
                        check_closeness_to_fvg(daily_fvg, 'daily', last_tick, how_close, now)

                    for weekly_fvg in stock_weekly_fvg_map[i]:
                        now = datetime.now().strftime('%H:%M:%S')
                        check_closeness_to_fvg(weekly_fvg, 'weekly', last_tick, how_close, now)

                    for monthly_fvg in stock_monthly_fvg_map[i]:
                        now = datetime.now().strftime('%H:%M:%S')
                        check_closeness_to_fvg(monthly_fvg, 'monthly', last_tick, how_close, now)

                except Exception as e:
                    time.sleep(3)
                    continue
            print('\n')
    except KeyboardInterrupt:
        print("Keyboard interrupt detected. Exiting...")
        exit(0)
