from analysis_utils import *
from tvDatafeed import Interval
import time
if __name__=='__main__':
    data_agent = DataAgent()
    while True:
        live_feed = data_agent.get_ohlc_data('NIFTY', interval=Interval.in_1_minute, n_bars=1, futures=True)
        print(live_feed[0]['close'])
        time.sleep(5)