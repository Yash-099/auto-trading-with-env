from utils.analysis_utils import *
from tvDatafeed import Interval
from data.config import *
from tqdm import tqdm
import json
import time
fvgs = FVGS()
obs = OBS()
data_agent = DataAgent()
analysis_agent = AnalysisAgent()
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

def get_filtered_orderblocks(stock, candles_to_look, percentage, time_frame):
    try:
        order_blocks = obs.get_bullish_orderblocks(stock, time_frame, candles=candles_to_look)
        current_price = data_agent.get_ohlc_data(stock, Interval.in_1_minute, 1)[0]['close']
        prices = data_agent.get_ohlc_data(stock, time_frame, candles_to_look)
    except:
        print('sleeping for 5...')
        time.sleep(5)
        return get_filtered_orderblocks(stock, candles_to_look, percentage, time_frame)
    filtered_orderblock_levels = []
    if time_frame == Interval.in_weekly:
        printing_time_frame = 'weekly'
    elif time_frame == Interval.in_daily:
        printing_time_frame = 'daily'
    elif time_frame == Interval.in_monthly:
        printing_time_frame = 'monthly'
    for order_block in order_blocks:
        ob_levels = [
            (order_block['high'], 'OB HIGH'),
            (order_block['open'], 'OB OPEN'),
            ((order_block['close'] + order_block['open']) / 2, 'OB MID'),
        ]
        for level, label in ob_levels:
            if is_within_range(level, current_price, percentage) and is_not_purged(level, prices, order_block['datetime']):
                filtered_orderblock_levels.append([level, f'{printing_time_frame} {label}'])

    return filtered_orderblock_levels


def get_filtered_upswings(stock, candles_to_look, percentage, time_frame):
    try:
        current_price = data_agent.get_ohlc_data(stock, Interval.in_1_minute, 1)[0]['close']
        prices = data_agent.get_ohlc_data(stock, time_frame, candles_to_look)
    except:
        print('sleeping for 5...')
        time.sleep(5)
        return get_filtered_upswings(stock, candles_to_look, percentage, time_frame)
    filtered_upswing_levels = []
    if time_frame == Interval.in_weekly:
        printing_time_frame = 'weekly'
    elif time_frame == Interval.in_daily:
        printing_time_frame = 'daily'
    elif time_frame == Interval.in_monthly:
        printing_time_frame = 'monthly'
    upswings, _ = analysis_agent.get_swings(prices, 'up')
    for swing_level in upswings:
        swing_datetime = None
        for candle in reversed(prices):
            if candle['high'] == swing_level:
                swing_datetime = candle['datetime']
                break
        if swing_datetime is None:
            continue
        if is_within_range(swing_level, current_price, percentage) and is_not_purged(swing_level, prices, swing_datetime):
            filtered_upswing_levels.append([swing_level, f'{printing_time_frame} UPSWING'])

    return filtered_upswing_levels


def _can_fetch_candles(stock, time_frame, n_bars):
    try:
        data = data_agent.get_ohlc_data_internal(stock, time_frame, n_bars)
        return len(data) == n_bars
    except Exception:
        return False

_max_candles_cache = {}

def max_number_of_candles(stock, time_frame, max_to_look_back):
    cache_key = (stock, time_frame)
    if cache_key in _max_candles_cache:
        return _max_candles_cache[cache_key]

    low, high = 1, max_to_look_back
    result = 1
    while low <= high:
        mid = (low + high) // 2
        if _can_fetch_candles(stock, time_frame, mid):
            result = mid
            low = mid + 1
        else:
            high = mid - 1

    _max_candles_cache[cache_key] = result
    return result

def get_weekly_levels(stock):
    candles = max_number_of_candles(stock, Interval.in_weekly, 500)
    return (
        get_filtered_bisis(stock, candles, 1, Interval.in_weekly)
        + get_filtered_orderblocks(stock, candles, 1, Interval.in_weekly)
        + get_filtered_upswings(stock, candles, 1, Interval.in_weekly)
    )

def get_monthly_levels(stock):
    candles = max_number_of_candles(stock, Interval.in_monthly, 200)
    return get_filtered_bisis(stock, candles, 1, Interval.in_monthly) + get_filtered_orderblocks(stock, candles, 1, Interval.in_monthly)

def get_daily_levels(stock):
    candles = max_number_of_candles(stock, Interval.in_daily, 500)
    return get_filtered_bisis(stock, candles, 1, Interval.in_daily) + get_filtered_upswings(stock, candles, 1, Interval.in_daily)

for i in tqdm(range(len(stocks_to_track))):
    stock = stocks_to_track[i]
    weekly_levels = get_weekly_levels(stock)
    daily_levels = get_daily_levels(stock)
    monthly_levels = get_monthly_levels(stock)
    crucial_levels_json[stock] = {'daily': daily_levels, 'weekly': weekly_levels, 'monthly': monthly_levels}


with open('updated_crucial_levels.json', 'w') as f:
    json.dump(crucial_levels_json, f)
