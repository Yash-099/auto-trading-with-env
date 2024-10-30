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

def read_levels(instrument):
    # read from the levels.py file
    import levels
    levels_to_return = []
    for tf in levels.levels[instrument]:
        levels_to_return += levels.levels[instrument][tf]
    return levels_to_return

def read_breached_levels(instrument):
    # read from the breached_levels.py file
    import breached_levels
    return breached_levels.breached_levels[instrument]


def show_notification(title, message):
    os.system(f"osascript -e 'display notification \"{message}\" with title \"{title}\"'")
    send_notification.notify(title, message)

def alert(time, instrument, level):
    message = f'{instrument}: near {level}'
    log_message = f'{time}: '+message
    logger.info(log_message)
    file = open('log_file.txt', 'a')
    file.write(log_message+'\n')
    file.close()
    show_notification(instrument, message)

def check_for_triggers(levels, instrument, breached_levels, hour_high, hour_low):
    for level in levels:
        if hour_high >= level and hour_low <= level:
            if level not in breached_levels:
                breached_levels.append(level)
                alert(datetime.now(), instrument, level)
                return level
    return None

def update_breached_levels(instrument, levels):
    import breached_levels
    logger.info('updating breached levels '+ str(levels))
    breached_levels.breached_levels[instrument] = levels
    # write in the file
    with open('breached_levels.py', 'w') as f:
        f.write(f'breached_levels = {breached_levels.breached_levels}')

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

if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    logging.basicConfig(filename='log_file.txt', level=logging.INFO)
    parser = ArgumentParser()
    parser.add_argument("--instrument", dest='instrument',  help="instrument to track, supported USOIL and NIFTY")
    args = parser.parse_args()
    data_agent = DataAgent()
    mohawk_allowed = 0.002 # 0.2%
    instrument_config = {
        'USOIL': {'exchange': 'TVC', 
                  'futures':False, 
                  'start_time': datetime.strptime("22:00:00", "%H:%M:%S").time(), 
                  'end_time': datetime.strptime("20:00:00", "%H:%M:%S").time()},
        'NIFTY': {'exchange': 'NSE', 
                  'futures':True,
                  'start_time': datetime.strptime("03:45:00", "%H:%M:%S").time(), 
                  'end_time': datetime.strptime("10:00:00", "%H:%M:%S").time()}
    }
    instrument = args.instrument
    exchange = instrument_config[instrument]['exchange']
    futures = instrument_config[instrument]['futures']

    day = datetime.now().strftime("%A")
    time_now =  datetime.now().time()
    
    try:
        while True:
            if stop_tracking(instrument, instrument_config, time_now, day):
                continue
            try:
                # this is in while loop because we want to keep checking the levels in real time
                instrument_levels = read_levels(instrument)
                breached_levels = read_breached_levels(instrument)
                data = data_agent.get_ohlc_data(instrument, Interval.in_1_hour, 2, exchange, futures)
                # we took the max and min of two candles for the scenario when the level touching happens when we are not checking and the hour changes
                hour_high = max(data[0]['high'], data[1]['high'])
                hour_low = min(data[0]['low'], data[1]['low'])
                level = check_for_triggers(instrument_levels, instrument, breached_levels, hour_high, hour_low)
                # start the code to check SIMS
                if level:
                    update_breached_levels(instrument, breached_levels)
                    data = data_agent.get_ohlc_data(instrument, Interval.in_5_minute, 2, exchange, futures)
                    if min(data[0]['high'], data[0]['low']) > level: # it is a support level
                        logger.info('Support level detected, we look for SIMS now.')
                        direction = 'up'
                    elif max(data[0]['high'], data[0]['low']) < level: # it is a resistance level
                        logger.info('Resistance level detected, we look for SIMS now.')
                        direction = 'down'
                    else: # our logic of previous candle based support resistance idea is wrong
                        logger.warning('Level detected but not sure of the direction look for SIMS')

                    detect_shift(level, direction, instrument, exchange, logger, mohawk_allowed=mohawk_allowed)

                time.sleep(60) # check every minute

            except Exception as e:
                logger.error(f'Error in main loop: {e}')
                time.sleep(5)
                continue

    except KeyboardInterrupt:
        print("Keyboard interrupt detected. Exiting...")
        exit(0)
