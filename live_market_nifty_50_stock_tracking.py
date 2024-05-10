from analysis_utils import *
from trade_utils import *
from tvDatafeed import Interval
from config import *
import time
from datetime import date, datetime
import os
from pathlib import Path
from tqdm import tqdm


if __name__ == '__main__':
    def preactions():
        make_log_file()

    def make_log_file():
        file_path = f"{date.today}.txt"
        if os.path.exists(file_path):
            return
        else:
            file = open(f'{date.today}.txt', 'w')

    def show_notification(title, message):
        os.system(f"osascript -e 'display notification \"{message}\" with title \"{title}\"'")

    def alert(time, stock, action, fvg, last_tick, gap):
        message = f'{last_tick} action-{action}, reason - near {fvg}, GAP: {gap}'
        log_message = f'{time}: {stock}'+message
        print(log_message)
        file = open(f'{date.today}.txt', 'a')
        file.write(log_message)
        file.close()
        show_notification(stock, message)

    how_close = 1/100 # 0.25 percent
    
    fvgs = FVGS()
    stock_weekly_fvg_map = {}
    stock_monthly_fvg_map = {}
    print('getting fvgs data (one time activity)')
    for i in tqdm(range(len(nifty_50_stocks))):
        stock_weekly_fvg_map[nifty_50_stocks[i]] = fvgs.get_bisis(nifty_50_stocks[i], 'weekly') + fvgs.get_sibis(nifty_50_stocks[i], 'weekly')
        stock_monthly_fvg_map[nifty_50_stocks[i]] = fvgs.get_bisis(nifty_50_stocks[i], 'monthly') + fvgs.get_sibis(nifty_50_stocks[i], 'monthly')
    print('got the fvgs data')

    preactions()
    data_agent = DataAgent()

    try:
        while True:
            for i in nifty_50_stocks:
                try:
                    last_tick = data_agent.get_ohlc_data(i, Interval.in_1_minute, 1)[0]['close']

                    for weekly_fvg in stock_weekly_fvg_map[i]:
                        now = datetime.now().strftime('%H:%M:%S')
                        high = weekly_fvg['high']
                        low = weekly_fvg['low']
                        mid = (high + low)/2

                        if abs(last_tick-high)/last_tick <= how_close:
                            alert(now, i, action='unkown', fvg=f'weekly fvg high {high}', last_tick=last_tick, gap=last_tick-high)

                        if abs(last_tick-low)/last_tick <= how_close:
                            alert(i, action='unkown', fvg=f'weekly fvg low {low}', last_tick=last_tick, gap=last_tick-low)

                        if abs(last_tick-mid)/last_tick <= how_close:
                            alert(i, action='unkown', fvg=f'weekly fvg mid {mid}', last_tick=last_tick, gap=last_tick-mid)

                    for monthly_fvg in stock_monthly_fvg_map[i]:
                        now = datetime.now().strftime('%H:%M:%S')
                        high = monthly_fvg['high']
                        low = monthly_fvg['low']
                        mid = (high + low)/2

                        if abs(last_tick-high)/last_tick <= how_close:
                            alert(now, i, action='unkown', fvg=f'monthly fvg high {high}', last_tick=last_tick, gap=last_tick-high)

                        if abs(last_tick-low)/last_tick <= how_close:
                            alert(i, action='unkown', fvg=f'monthly fvg low {low}', last_tick=last_tick, gap=last_tick-low)

                        if abs(last_tick-mid)/last_tick <= how_close:
                            alert(i, action='unkown', fvg=f'monthly fvg mid {mid}', last_tick=last_tick, gap=last_tick-mid)

                except Exception as e:
                    time.sleep(3)
                    continue
            print('\n')
    except KeyboardInterrupt:
        print("Keyboard interrupt detected. Exiting...")
