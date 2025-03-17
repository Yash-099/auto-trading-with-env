# we will be checking monthly fvgs touching/breaching for now
from analysis_utils import *
from tqdm import tqdm
from tvDatafeed import Interval
from config import *

def check_if_high_removed(stock, level):
        daily_data = data_agent.get_ohlc_data(stock, Interval.in_daily, 1, exchange='NSE')
        close = daily_data[0]['close']
        if close >= level:
            return True
        return False

def get_json_data(file_name):
    if not os.path.exists(file_name):
        return []
    with open(file_name, 'r') as f:
        return json.load(f)

def write_json_data(file_name, data):
    with open(file_name, 'w') as f:
        json.dump(data, f)

def needs_checking(stock):
    discarded_stocks = get_json_data('/Users/ybhavsar/Documents/personal/auto-trading/discarded_stocks.json')
    if stock['name'] in discarded_stocks or stock['high_removed']:
        return False
    return True

def get_current_crucial_level(stock):
    monthly_bisis = fvgs.get_bisis(stock, Interval.in_monthly, 50)
    monthly_bullish_obs = obs.get_bullish_orderblocks(stock, Interval.in_monthly, 50)
    crucial_levels = []
    for bisi in monthly_bisis:
        if not bisi['high_purged']:
            crucial_levels.append(bisi['high'])
        if not bisi['low_purged']:
            crucial_levels.append(bisi['low'])
    
    for order_block in monthly_bullish_obs:
        crucial_levels.append(order_block['high'])
        crucial_levels.append(order_block['open'])
        crucial_levels.append((order_block['close'] + order_block['open'])/2)
    if crucial_levels:
        daily_data = data_agent.get_ohlc_data(stock, Interval.in_daily, 2, exchange='NSE')
        yesterday_low = daily_data[0]['low']
        crucial_levels.sort(key=lambda x: -x)
        for level in crucial_levels:
            if level < yesterday_low:
                break
        if analysis_agent.if_level_purged_by_candle(daily_data[1]['high'], daily_data[1]['low'], level):
            print(f'-------------{stock} level purged by candle {level}-------------')
            return level
    return None

def check_if_we_have_lower_crucial_level(stock, current_crucial_level):
    new_crucial_level = get_current_crucial_level(stock)
    if new_crucial_level is None or new_crucial_level >= current_crucial_level:
        return False
    else:
        return True



if __name__=="__main__":
    stocks = nifty_50_stocks + mid_cap_stocks + small_cap_stocks
    filtered_stocks = []
    fvgs = FVGS()
    analysis_agent = AnalysisAgent()
    data_agent = DataAgent()
    obs = OBS()

    long_term_filtered_stocks = get_json_data('/Users/ybhavsar/Documents/personal/auto-trading/long_term_filtered_stocks.json')
    long_term_filtered_stocks_names = [stock['name'] for stock in long_term_filtered_stocks]
    print(long_term_filtered_stocks_names)

    # check if the high is removed
    for stock in long_term_filtered_stocks:
        if needs_checking(stock) and check_if_high_removed(stock['name'], stock['high']):
            print(f'----------------{stock} high removed----------------')
            stock['high_removed'] = True
            # long_term_filtered_stocks.append(stock)
    write_json_data('/Users/ybhavsar/Documents/personal/auto-trading/long_term_filtered_stocks.json', long_term_filtered_stocks)


    # check if we need to remove some values from the list
    # we will be removing when we have a new lower crucial level
    for stock in long_term_filtered_stocks:
        current_crucial_level = stock['crucial_level']
        if needs_checking(stock) and check_if_we_have_lower_crucial_level(stock['name'], current_crucial_level):
            stock['crucial_level'] = get_current_crucial_level(stock['name'])
            stock['lowest_close'] = data_agent.get_ohlc_data(stock['name'], Interval.in_daily, 1, exchange='NSE')[0]['close']
            stock['high'] = data_agent.get_ohlc_data(stock['name'], Interval.in_daily, 1, exchange='NSE')[0]['high']
            # filtered_stocks.append(stock)
    write_json_data('/Users/ybhavsar/Documents/personal/auto-trading/long_term_filtered_stocks.json', long_term_filtered_stocks)

    # if we need to update the low and high of the stock
    for stock in long_term_filtered_stocks:
        if needs_checking(stock):
            daily_data = data_agent.get_ohlc_data(stock['name'], Interval.in_daily, 1, exchange='NSE')
            if daily_data[0]['close'] <= stock['lowest_close']:
                stock['lowest_close'] = daily_data[0]['close']
                stock['high'] = daily_data[0]['high']
    write_json_data('/Users/ybhavsar/Documents/personal/auto-trading/long_term_filtered_stocks.json', long_term_filtered_stocks)


    for i in tqdm(range(len(stocks))):
        try:
            stock = stocks[i]
            if stock in long_term_filtered_stocks_names:
                continue
            crucial_level = get_current_crucial_level(stock)
            if crucial_level is None:
                continue
            else:
                daily_data = data_agent.get_ohlc_data(stock, Interval.in_daily, 1, exchange='NSE')
                temp = {'name': stock, 'crucial_level': crucial_level, 'lowest_close': daily_data[0]['close'], 'high': daily_data[0]['high'], 'high_removed': False}
                print(temp)
                long_term_filtered_stocks.append(temp)
        except Exception as e:
            print(f'error in {stock}')
            print('error:', e)
    
    with open('/Users/ybhavsar/Documents/personal/auto-trading/long_term_filtered_stocks.json', 'w') as f:
        json.dump(long_term_filtered_stocks, f)