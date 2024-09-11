from analysis_utils import *
from tvDatafeed import Interval
from config import *
from tqdm import tqdm
import time
fvgs = FVGS()
data_agent = DataAgent()
crucial_levels_json = {}

def is_within_range(level, current_price, percentage):
    if current_price * (1 - percentage) < level < current_price * (1 + percentage):
        return True
    return False

def is_not_purged(level, prices, datetime):
    for i in range(len(prices)):
        if prices[i]['datetime'] > datetime:
            if prices[i]['high'] > level and prices[i]['low'] < level:
                return False
    return True

def get_filtered_bisis(stock, candles_to_look, percentage, time_frame):
    try:
        crude_bisis = fvgs.get_bisis(stock, time_frame, candles=candles_to_look)
        current_price = data_agent.get_ohlc_data(stock, Interval.in_1_minute, 1)[0]['close']
        prices = data_agent.get_ohlc_data(stock, time_frame, candles_to_look)
    except:
        print('sleeping for 5...')
        time.sleep(5)
        return get_filtered_bisis(stock, candles_to_look, percentage, time_frame)
    filtered_bisi_levels = []
    if time_frame == Interval.in_weekly:
        printing_time_frame = 'weekly'
    elif time_frame == Interval.in_daily:
        printing_time_frame = 'daily'
    elif time_frame == Interval.in_monthly:
        printing_time_frame = 'monthly'
    for bisi in crude_bisis:
        if is_within_range(bisi['low'], current_price, percentage) and is_not_purged(bisi['low'], prices, bisi['datetime']):
            filtered_bisi_levels.append([bisi['low'], f'{printing_time_frame} BISI LOW'])
        if is_within_range(bisi['high'], current_price, percentage) and is_not_purged(bisi['high'], prices, bisi['datetime']):
            filtered_bisi_levels.append([bisi['high'], f'{printing_time_frame} BISI HIGH'])
        if is_within_range((bisi['low']+bisi['high'])/2, current_price, percentage) and is_not_purged((bisi['low']+bisi['high'])/2, prices, bisi['datetime']):
            filtered_bisi_levels.append([(bisi['low']+bisi['high'])/2, f'{printing_time_frame} BISI MID'])

    return filtered_bisi_levels


def get_filtered_sibis(stock, candles_to_look, percentage, time_frame):
    try:
        crude_sibis = fvgs.get_sibis(stock, time_frame, candles=candles_to_look)
        current_price = data_agent.get_ohlc_data(stock, Interval.in_1_minute, 1)[0]['close']
        prices = data_agent.get_ohlc_data(stock, time_frame, candles_to_look)
    except:
        print('sleeping for 20')
        time.sleep(20)
        return get_filtered_bisis(stock, candles_to_look, percentage, time_frame)
    filtered_sibi_levels = []
    if time_frame == Interval.in_weekly:
        printing_time_frame = 'weekly'
    elif time_frame == Interval.in_daily:
        printing_time_frame = 'daily'
    elif time_frame == Interval.in_monthly:
        printing_time_frame = 'monthly'

    for sibi in crude_sibis:
        if is_within_range(sibi['low'], current_price, percentage) and is_not_purged(sibi['low'], prices, sibi['datetime']):
            filtered_sibi_levels.append([sibi['low'], f'{printing_time_frame} SIBI LOW'])
        if is_within_range(sibi['high'], current_price, percentage) and is_not_purged(sibi['high'], prices, sibi['datetime']):
            filtered_sibi_levels.append([sibi['high'], f'{printing_time_frame} SIBI HIGH'])
        if is_within_range((sibi['low'] + sibi['high']) / 2, current_price, percentage) and is_not_purged((sibi['low']+sibi['high'])/2, prices, sibi['datetime']):
            filtered_sibi_levels.append([(sibi['low'] + sibi['high']) / 2, f'{printing_time_frame} SIBI MID'])

    return filtered_sibi_levels

def get_weekly_fvgs(stock):
    weekly_bisis = get_filtered_bisis(stock, 200, 0.05, Interval.in_weekly)
    weekly_sibis = get_filtered_sibis(stock, 200, 0.05, Interval.in_weekly)
    weekly_levels = weekly_bisis + weekly_sibis
    return weekly_levels

def get_daily_fvgs(stock):
    daily_bisis = get_filtered_bisis(stock, 200, 0.05, Interval.in_daily)
    daily_sibis = get_filtered_sibis(stock, 200, 0.05, Interval.in_daily)
    daily_levels = daily_bisis + daily_sibis
    return daily_levels

for i in tqdm(range(len(stocks_to_track))):
    stock = stocks_to_track[i]
    weekly_levels = get_weekly_fvgs(stock)
    daily_levels = get_daily_fvgs(stock)

    crucial_levels_json[stock] = {'daily': daily_levels, 'weekly': weekly_levels}


with open('updated_crucial_levels.json', 'w') as f:
    json.dump(crucial_levels_json, f)