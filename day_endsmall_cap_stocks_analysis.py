from analysis_utils import *
from trade_utils import *
from tvDatafeed import Interval
from config import *
import time
from datetime import date
import os
from pathlib import Path
from tqdm import tqdm

if __name__=='__main__':
    data_agent = DataAgent()
    file = open(f'daily_analysis/small_cap_stocks/{date.today()}.txt', 'w')
    file.close()
    today_date = date.today()

    # Path(f'daily_analyso/small_cap_stocks/{date.today()}.txt').touch()
    for i in tqdm(range(len(skipped))):
        file = open(f'daily_analysis/small_cap_stocks/{today_date}.txt', 'a')
        retry_count = 100
        got_data = False
        retry_num = 1
        skip = False
        while (not got_data) and (retry_num < retry_count):
            try:
                data = data_agent.get_ohlc_data(skipped[i], Interval.in_weekly, 100)
                got_data = True
            except:
                if retry_num > 10:
                    time.sleep(retry_num)
                retry_num += 1
                if retry_num > 30:
                    skip = True
                    print(f'skipping {skipped[i]}')
                    break

        if skip:
            continue
        analysis_agent = AnalysisAgent()
        sellsides = analysis_agent.find_sellside_liquidity(data, 3)
        nearest_sellside = analysis_agent.get_if_near_sellside(data, percentage=5, num_neighbours=3)
        nearest_sellside_price = nearest_sellside['nearest_liquidity_in_range']

        if nearest_sellside_price!=0:
            file.write(f'Stock {skipped[i]} is near its liquidity pool at price {nearest_sellside_price} current price is {data[-1]["close"]}\n')
            file.close()
            # print(f'Stock {small_cap_stocks[i]} is near its liquidity pool at price {nearest_sellside_price} current price is {data[-1]["close"]}')
        time.sleep(0)