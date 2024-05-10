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

    def show_notification(title, message):
        os.system(f"osascript -e 'display notification \"{message}\" with title \"{title}\"'")

    how_close = 0.25/100 # 0.25 percent
    fvgs = FVGS()
    stock_weekly_fvg_map = {}
    stock_monthly_fvg_map = {}
    print('getting fvgs data (one time activity)')
    for i in tqdm(range(len(temp))):
        stock_weekly_fvg_map[temp[i]] = fvgs.get_bisis(temp[i], 'weekly') + fvgs.get_sibis(temp[i], 'weekly')
        stock_monthly_fvg_map[temp[i]] = fvgs.get_bisis(temp[i], 'monthly') + fvgs.get_sibis(temp[i], 'monthly')
    print('got the fvgs data')
    data_agent = DataAgent()

    try:
        while True:
            for i in temp:
                try:
                    last_tick = data_agent.get_ohlc_data(i, Interval.in_1_minute, 1)[0]['close']

                    for weekly_fvg in stock_weekly_fvg_map[i]:
                        now = datetime.now().strftime('%H:%M:%S')
                        high = weekly_fvg['high']
                        low = weekly_fvg['low']
                        mid = (high + low)/2
                        if abs(last_tick-high)/last_tick <= how_close:
                            print(f'{now}:{i}-{last_tick} is near weekly fvg high {high} :GAP - {last_tick-high} ')
                        if abs(last_tick-low)/last_tick <= how_close:
                            print(f'{now}:{i}-{last_tick} is near weekly fvg low {low} :GAP - {last_tick-low}')
                        if abs(last_tick-mid)/last_tick <= how_close:
                            print(f'{now}:{i}-{last_tick} is near weekly fvg mid {mid} :GAP - {last_tick-mid}')
                            show_notification(f"{i}", f'{now}:{i}-{last_tick} is near weekly fvg mid {mid} :GAP - {last_tick-mid}')

                    for monthly_fvg in stock_monthly_fvg_map[i]:
                        now = datetime.now().strftime('%H:%M:%S')
                        high = monthly_fvg['high']
                        low = monthly_fvg['low']
                        mid = (high + low)/2
                        if abs(last_tick-high)/last_tick <= how_close:
                            print(f'{now}:{i}-{last_tick} is near monthly fvg high {high} :GAP - {last_tick-high}')
                        if abs(last_tick-low)/last_tick <= how_close:
                            print(f'{now}:{i}-{last_tick} is near monthly fvg low {low} :GAP - {last_tick-low}')
                        if abs(last_tick-mid)/last_tick <= how_close:
                            print(f'{now}:{i}-{last_tick} is near monthly fvg mid {mid} :GAP - {last_tick-mid}')

                except Exception as e:
                    continue
                datetime.sleep(3)
            print('\n')
    except KeyboardInterrupt:
        print("Keyboard interrupt detected. Exiting...")
