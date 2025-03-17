# code for sending pushbulltet notification of nifty futures contracr

from analysis_utils import *
from trade_utils import *
from tvDatafeed import Interval
from config import *
import time
from datetime import datetime
import os
from live_track.detect_sims import *
from argparse import ArgumentParser
import logging

def stop_tracking(instrument, instrument_config, time_now, day):
    if instrument == 'USOIL':
        if day == 'Saturday':
            return True
        elif day == 'Sunday': # on sunday trading starts at 22:00
            if time_now < instrument_config[instrument]['start_time']:
                return True
        elif day == 'Friday': # on friday unlike other weekdays trading does not start at 22:00
            if time_now > instrument_config[instrument]['end_time']:
                return True
        else: # week days
            if time_now < instrument_config[instrument]['start_time'] and time_now > instrument_config[instrument]['end_time']:
                return True
    elif instrument == 'NIFTY':
        if day == 'Saturday' or day == 'Sunday':
            return True
        else: # week days
            if time_now < instrument_config[instrument]['start_time'] or time_now > instrument_config[instrument]['end_time']:
                return True
    return False

def show_notification(title, message, logger):
    print('calling send notification')
    send_notification.notify(title, message, logger)

# code for sending pushbullet notification of nifty futures contract take reference from live_track_24hrs.py
if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    logging.basicConfig(filename='log_file.txt', level=logging.INFO)
    parser = ArgumentParser()
    parser.add_argument("--instrument", dest='instrument', help="instrument to track, supported USOIL and NIFTY")
    parser.add_argument("--upper", nargs='+', type=float, help="Upper levels to monitor")
    parser.add_argument("--lower", nargs='+', type=float, help="Lower levels to monitor")
    args = parser.parse_args()
    data_agent = DataAgent()
    mohawk_allowed = 0.002 # 0.2%
    instrument_config = {
        'NIFTY': {'exchange': 'NSE',
                  'start_time': datetime.strptime("10:30:00", "%H:%M:%S").time(), 
                  'end_time': datetime.strptime("15:05:00", "%H:%M:%S").time()}
    }
    instrument = args.instrument
    exchange = instrument_config[instrument]['exchange']
    futures = instrument_config[instrument]['futures']

    day = datetime.now().strftime("%A")
    
    breached_upper = [False] * len(args.upper)
    breached_lower = [False] * len(args.lower)
    
    try:
        while True:
            time_now = datetime.now().time()
            if stop_tracking(instrument, instrument_config, time_now, day):
                print('not tracking')
                break
            try:
                # this is in while loop because we want to keep checking the levels in real time
                data = data_agent.get_ohlc_data(instrument, Interval.in_5_minute, 3, exchange)
                high_price = data[1]["high"]
                low_price = data[1]["low"]
                
                # Check if the price breaches the specified upper levels
                for i, upper_level in enumerate(args.upper):
                    if high_price > upper_level and not breached_upper[i]:
                        show_notification(f'Level Breached', f'Price has breached the upper level: {upper_level}', logger)
                        breached_upper[i] = True
                
                # Check if the price breaches the specified lower levels
                for i, lower_level in enumerate(args.lower):
                    if low_price < lower_level and not breached_lower[i]:
                        show_notification(f'Level Breached', f'Price has breached the lower level: {lower_level}', logger)
                        breached_lower[i] = True
                
                # Existing notification logic
                show_notification(f'5min', f'change: {round(data[1]["close"] - data[0]["close"])} \nhigh: {round(data[1]["high"] - data[1]["close"])} \nclose: {data[1]["close"]} \nlow: {round(data[1]["low"] - data[1]["close"])}', logger)
                time.sleep(300)
            except Exception as e:
                print(e, 'error in main loop')
                logger.error(f'Error in main loop: {e}')
                time.sleep(5)
                continue

    except KeyboardInterrupt:
        print("Keyboard interrupt detected. Exiting...")
        exit(0)