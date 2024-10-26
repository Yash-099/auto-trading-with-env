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

def read_levels(instrument):
    # read from the levels.py file
    import levels
    levels_to_return = []
    for tf in levels.levels[instrument]:
        levels_to_return += levels.levels[instrument][tf]
    return levels_to_return

def read_breached_levels(instrument):
    # read from the breached_levels.py file
    import breached_levels
    return breached_levels.breached_levels[instrument]


def show_notification(title, message):
    os.system(f"osascript -e 'display notification \"{message}\" with title \"{title}\"'")

def alert(time, instrument, level):
    message = f'{instrument}: near {level}'
    log_message = f'{time}: '+message
    print(log_message)
    file = open('log_file.txt', 'a')
    file.write(log_message+'\n')
    file.close()
    show_notification(instrument, message)

def check_for_triggers(levels, breached_levels, hour_high, hour_low):
    for level in levels:
        if hour_high >= level and hour_low <= level:
            if level not in breached_levels:
                breached_levels.append(level)
                alert(datetime.now(), 'crude', level)

def update_breached_levels(instrument, levels):
    import breached_levels
    print('updating breached levels', levels)
    breached_levels.breached_levels[instrument] = levels
    # write in the file
    with open('breached_levels.py', 'w') as f:
        f.write(f'breached_levels = {breached_levels.breached_levels}')

if __name__ == '__main__':
    
    data_agent = DataAgent()

    try:
        while True:
            try:
                crude_levels = read_levels('crude')
                nifty_levels = read_levels('nifty')
                print('crude levels', crude_levels)
                print('nifty levels', nifty_levels)
                breached_crude_levels = read_breached_levels('crude')
                breached_nifty_levels = read_breached_levels('nifty')
                
                crude_data = data_agent.get_ohlc_data("USOIL", Interval.in_1_hour, 1, exchange='TVC')
                print(crude_data)
                hour_high = crude_data[0]['high']
                hour_low = crude_data[0]['low']
                check_for_triggers(crude_levels, breached_crude_levels, hour_high, hour_low)
                print("breached_levels", breached_crude_levels)
                update_breached_levels('crude', breached_crude_levels)

                nifty_data = data_agent.get_ohlc_data("NIFTY", Interval.in_1_hour, 1, exchange='NSE', futures=True)
                print(nifty_data)
                hour_high = nifty_data[0]['high']
                hour_low = nifty_data[0]['low']
                check_for_triggers(nifty_levels, breached_nifty_levels, hour_high, hour_low)
                print("breached_levels", breached_nifty_levels)
                update_breached_levels('nifty', breached_nifty_levels)
                time.sleep(60) # check every minute

            except Exception as e:
                time.sleep(3)
                continue
            
    except KeyboardInterrupt:
        print("Keyboard interrupt detected. Exiting...")
        exit(0)
