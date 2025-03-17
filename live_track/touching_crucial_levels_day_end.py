# we will be checking monthly fvgs touching/breaching for now
from analysis_utils import *
from tqdm import tqdm
from tvDatafeed import Interval
from config import *

if __name__=="__main__":
    stocks = nifty_50_stocks + mid_cap_stocks# + small_cap_stocks
    filtered_stocks = []
    fvgs = FVGS()
    analysis_agent = AnalysisAgent()
    data_agent = DataAgent()
    obs = OBS()

    for i in tqdm(range(len(stocks))):
        try:
            stock = stocks[i]
            # find nearest level
            monthly_bisis = fvgs.get_bisis(stock, Interval.in_monthly, 50)
            monthly_bullish_obs = obs.get_bullish_orderblocks(stock, Interval.in_monthly, 50)
            crucial_levels = []
            for bisi in monthly_bisis:
                if not bisi['high_purged']:
                    crucial_levels.append(bisi['high'])
                if not bisi['low_purged']:
                    crucial_levels.append(bisi['low'])
                if not bisi['mid_purged']:
                    crucial_levels.append((bisi['low']+bisi['high'])/2)
            for order_block in monthly_bullish_obs:
                crucial_levels.append(order_block['high'])
                crucial_levels.append(order_block['open'])
                crucial_levels.append((order_block['close'] + order_block['open'])/2)
            if crucial_levels:
                daily_data = data_agent.get_ohlc_data(stock, Interval.in_daily, 2, exchange='NSE')
                yesterday_close = daily_data[0]['close']
                crucial_levels.sort(key=lambda x: -x)
                # print('sorted crucial levels:', crucial_levels)
                for level in crucial_levels:
                    if level < yesterday_close:
                        break
                if analysis_agent.if_level_purged_by_candle(daily_data[1]['high'], daily_data[1]['low'], level):
                    print(f'{stock} touched the level {level}')
                    filtered_stocks.append(f'{stock} touched the level {level}')
        except Exception as e:
            print(f'error in {stock}')
            print('error:', e)
    print('filtered stocks:', filtered_stocks)