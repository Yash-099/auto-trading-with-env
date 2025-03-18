# code for sending pushbulltet notification of nifty spot

from analysis_utils import *
from trade_utils import *
from tvDatafeed import Interval
from config import *
import time
from datetime import datetime, timedelta
import os
from live_track.detect_sims import *
from argparse import ArgumentParser
import logging


def show_notification(title, message, logger):
    print('calling send notification')
    send_notification.notify(title, message, logger)

def get_time_now():
    # add a shift of n hours and p minutes to the current time
    return (datetime.now()+timedelta(hours=5, minutes=30)).time()

def get_date_now():
    return (datetime.now()+timedelta(hours=5, minutes=30)).date()

def set_market_condition(condition):
    print(f"Setting market condition: {condition}")
    with open("market_condition.txt", "w") as file:
        file.write(condition)

def reset_market_condition():
    with open("market_condition.txt", "w") as file:
        file.write("none")

if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    logging.basicConfig(filename='log_file.txt', level=logging.INFO)
    parser = ArgumentParser()
    parser.add_argument("--instrument", dest='instrument', help="instrument to track, supported USOIL and NIFTY")
    parser.add_argument("--upper", nargs='+', type=float, help="Upper levels to monitor")
    parser.add_argument("--lower", nargs='+', type=float, help="Lower levels to monitor")
    args = parser.parse_args()
    data_agent = DataAgent()
    instrument_config = {
        'NIFTY': {'exchange': 'NSE',
                  'start_time': datetime.strptime("10:30:00", "%H:%M:%S").time(), 
                  'end_time': datetime.strptime("15:05:00", "%H:%M:%S").time(),
                  'session_times': [datetime.strptime("9:30:00", "%H:%M:%S").time(),
                                    datetime.strptime("11:00:00", "%H:%M:%S").time(),
                                    datetime.strptime("12:30:00", "%H:%M:%S").time(),
                                    datetime.strptime("14:00:00", "%H:%M:%S").time()]}
    }
    instrument = args.instrument
    exchange = instrument_config[instrument]['exchange']

    day = datetime.now().strftime("%A")
    
    def market_closed():
        if day in ['Saturday', 'Sunday']:
            return True
        if get_time_now().hour < 9 or get_time_now().hour > 15:
            return True
        return False
    
    i = 0
    # mock_data = data_agent.get_ohlc_data(instrument, Interval.in_5_minute, 75, exchange)
    try:
        while True:
            if market_closed():
                print('market closed')
                time.sleep(10)
                continue
            #start tracking at session + 5mins
            highest_candle_data = {}
            lowest_candle_data = {}
            session_high = 0
            session_low = 1000000000000000
            time_now = get_time_now()
            session_start = datetime.combine(get_date_now(), instrument_config[instrument]['session_times'][i])
            session_start_plus_5 = session_start + timedelta(minutes=5)
            session_start_plus_50 = session_start + timedelta(minutes=50)
            current_time = datetime.combine(get_date_now(), time_now)
            breached_downside = False
            breached_upside = False
            print(current_time)
            print(day)
            if current_time > session_start_plus_5 and day not in ['Saturday', 'Sunday']:
                print('tracking')
                try:
                    while True:
                        time_now = get_time_now()
                        # this is in while loop because we want to keep checking the levels in real time
                        data = data_agent.get_ohlc_data(instrument, Interval.in_5_minute, 2, exchange)
                        print(data)
                        candle_data = data[0]
                        if candle_data["close"] - candle_data["open"] > 0 and candle_data['close']>session_high: # green highest candle
                            session_high = candle_data["close"]
                            highest_candle_data = candle_data
                            breached_downside = False
                        elif candle_data["close"] - candle_data["open"] < 0 and candle_data['close']<session_low: # red lowest candle
                            session_low = candle_data["close"]
                            lowest_candle_data = candle_data
                            breached_upside = False

                        if session_high - session_low > 0: # meaning both are set
                            if candle_data["close"] > lowest_candle_data["high"] and not breached_upside:
                                show_notification(f'Breached to the upside', f'sample text', logger)
                                breached_upside = True
                                set_market_condition(f"buy @ {candle_data['close']}")
                            if candle_data["close"] < highest_candle_data["low"] and not breached_downside:
                                show_notification(f'Breached to the downside', f'sample text', logger)
                                breached_downside = True
                                set_market_condition(f"sell @ {candle_data['close']}")

                        current_time = datetime.combine(get_date_now(), time_now)
                        if current_time > session_start_plus_50:
                            break # break the session loop after 50 mins
                        time.sleep(300)
                        reset_market_condition()
                    i = (i + 1) % 4
                except Exception as e:
                    print(e)
                    print(e, 'error in main loop')
                    logger.error(f'Error in main loop: {e}')
                    time.sleep(5)
                    continue
            else:
                print('not tracking')
                time.sleep(10)
    except KeyboardInterrupt:
        print("Keyboard interrupt detected. Exiting...")
        exit(0)