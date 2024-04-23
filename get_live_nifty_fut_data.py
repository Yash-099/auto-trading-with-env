from analysis_utils import *
from tvDatafeed import Interval
import time
from datetime import datetime

if __name__=='__main__':
    data_agent = DataAgent()
    while True:
        live_feed = data_agent.get_ohlc_data('NIFTY', interval=Interval.in_1_minute, n_bars=1, futures=True)
        print(datetime.now(),live_feed[0]['close'])
        time.sleep(5)