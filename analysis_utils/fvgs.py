from analysis_utils import *
from tvDatafeed import Interval
from config import *
import time
from datetime import date
import os
from pathlib import Path
from tqdm import tqdm

class FVGS:
    def get_sibis(self, stock, time_frame, candles=10):
        data_agent = DataAgent()
        try:
            data = data_agent.get_ohlc_data(stock, time_frame, candles)
        except:
            time.sleep(5)
            return self.get_sibis(stock, time_frame, candles)

        analysis_agent = AnalysisAgent()
        
        return analysis_agent.find_fvg_sibi(data)
    
    def get_bisis(self, stock, time_frame, candles=10):
        data_agent = DataAgent()
        try:
            data = data_agent.get_ohlc_data(stock, time_frame, candles)
        except:
            time.sleep(5)
            return self.get_bisis(stock, time_frame, candles)

        analysis_agent = AnalysisAgent()
        
        return analysis_agent.find_fvg_bisi(data)


# if __name__=='__main__':
#     data_agent = DataAgent()
#     # file = open(f'daily_analysis/small_cap_stocks/{date.today()}.txt', 'w')
#     # file.close()
#     # today_date = date.today()

#     # Path(f'daily_analyso/small_cap_stocks/{date.today()}.txt').touch()
#     for i in tqdm(range(len(nifty_50_stocks))):
#         # file = open(f'daily_analysis/small_cap_stocks/{today_date}.txt', 'a')
#         retry_count = 100
#         got_data = False
#         retry_num = 1
#         skip = False
#         while (not got_data) and (retry_num < retry_count):
#             try:
#                 data = data_agent.get_ohlc_data(nifty_50_stocks[i], Interval.in_monthly, 10)
#                 got_data = True
#             except:
#                 if retry_num > 10:
#                     time.sleep(retry_num)
#                 retry_num += 1
#                 if retry_num > 30:
#                     skip = True
#                     print(f'skipping {nifty_50_stocks[i]}')
#                     break

#         if skip:
#             continue
#         analysis_agent = AnalysisAgent()
#         stock = nifty_50_stocks[i]
#         print(f'for stock {stock} {analysis_agent.find_fvg_bisi(data)}')