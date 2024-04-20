from analysis_utils import *
from trade_utils import *
from tvDatafeed import Interval
from config import *


if __name__=='__main__':
    data_agent = DataAgent()
    for i in nifty_50_stocks:
        data = data_agent.get_ohlc_data(i, Interval.in_weekly, 100)

        analysis_agent = AnalysisAgent()
        sellsides = analysis_agent.find_sellside_liquidity(data, 10)
        nearest_sellside = analysis_agent.get_if_near_sellside(data, 5, 3)
        nearest_sellside_price = nearest_sellside['nearest_liquidity_in_range']

        if nearest_sellside_price!=0:
            print(f'Stock {i} is near its liquidity pool at price {nearest_sellside_price} current price is {data[-1]["close"]}')
        