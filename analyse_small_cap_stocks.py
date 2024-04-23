from analysis_utils import *
from trade_utils import *
from tvDatafeed import Interval
from config import *
import time
from datetime import date
import os
from pathlib import Path


if __name__=='__main__':
    data_agent = DataAgent()
    file = open(f'daily_analysis/small_cap_stocks/{date.today()}.txt', 'w')
    file.close()

    # Path(f'daily_analyso/small_cap_stocks/{date.today()}.txt').touch()
    for i in small_cap_stocks:
        file = open(f'daily_analysis/small_cap_stocks/{date.today()}.txt', 'a')
        retry_count = 3
        got_data = False
        retry_num = 1
        while (not got_data) and (retry_num < retry_count):
            try:
                data = data_agent.get_ohlc_data(i, Interval.in_weekly, 100)
                got_data = True
            except:
                time.sleep(20)
                retry_num += 1

        analysis_agent = AnalysisAgent()
        sellsides = analysis_agent.find_sellside_liquidity(data, 3)
        nearest_sellside = analysis_agent.get_if_near_sellside(data, percentage=5, num_neighbours=3)
        nearest_sellside_price = nearest_sellside['nearest_liquidity_in_range']

        if nearest_sellside_price!=0:
            file.write(f'Stock {i} is near its liquidity pool at price {nearest_sellside_price} current price is {data[-1]["close"]}')
            file.close()
            print(f'Stock {i} is near its liquidity pool at price {nearest_sellside_price} current price is {data[-1]["close"]}')
        time.sleep(20)