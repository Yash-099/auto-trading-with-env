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

def show_notification(title, message):
    os.system(f"osascript -e 'display notification \"{message}\" with title \"{title}\"'")
    send_notification.notify(title, message)

def alert(time, instrument, level):
    message = f'{instrument}: broke the market structure from {level}'
    log_message = f'{time}: '+message
    print(log_message)
    file = open('log_file.txt', 'a')
    file.write(log_message+'\n')
    file.close()
    show_notification(instrument, message)


def detect_shift(level, direction, instrument, exchange, futures=False, mohawk_allowed=0.002):
    data_agent = DataAgent()
    analysis_agent = AnalysisAgent()
    try:
        while True:
            try:
                crude_data = data_agent.get_ohlc_data(instrument, Interval.in_5_minute, 100, exchange=exchange, futures=futures)
                if direction == 'up':
                    _, closest = analysis_agent.get_swings(crude_data, 'up')
                    # market shifted and alert sent
                    if crude_data[-1]['close'] > closest:
                        print('market_shifted')
                        alert(datetime.now(), instrument, level)
                        break
                    # market not respecting the level
                    if crude_data[-1]['close'] < level* (1-mohawk_allowed):
                        print('level breached')
                        break
                else:
                    _, closest = analysis_agent.get_swings(crude_data, 'down')
                    # market shifted and alert sent
                    if crude_data[-1]['close'] < closest:
                        print('market_shifted')
                        alert(datetime.now(), instrument, level)
                        break
                    # market not respecting the level
                    if crude_data[-1]['close'] > level* (1+mohawk_allowed):
                        print('level breached')
                        break

            except Exception as e:
                print('error:', e)
            time.sleep(60)
    except KeyboardInterrupt:
        print('stopping')
        exit(0)