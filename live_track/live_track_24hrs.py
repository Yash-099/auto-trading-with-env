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
    logging.basicConfig(filename='log_file.txt', encoding='utf-8', level=logging.DEBUG)
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
            logger.info(f'Tracking {instrument}... time: { datetime.now()}')
            try:
                # this is in while loop because we want to keep checking the levels in real time
                instrument_levels = read_levels(instrument)
                breached_levels = read_breached_levels(instrument)
                data = data_agent.get_ohlc_data(instrument, Interval.in_1_hour, 1, exchange, futures)
                hour_high = data[0]['high']
                hour_low = data[0]['low']
                level = check_for_triggers(instrument_levels, instrument, breached_levels, hour_high, hour_low)
                logger.info(f'Current levels: {level}')
                # start the code to check SIMS
                if level:
                    update_breached_levels(instrument, breached_levels)
                    data = data_agent.get_ohlc_data(instrument, Interval.in_1_hour, 2, exchange, futures)
                    if min(data[0]['high'], data[0]['low']) > level: # it is a support level
                        direction = 'up'
                    elif max(data[0]['high'], data[0]['low']) < level: # it is a resistance level
                        direction = 'down'
                    else: # our logic of previous candle based support resistance idea is wrong
                        logger.warning('Support resistance logic failed')

                    detect_shift(level, direction=direction, instrument=instrument, exchange=exchange, mohawk_allowed=mohawk_allowed)

                time.sleep(60) # check every minute

            except Exception as e:
                logger.error(f'Error in main loop: {e}')
                time.sleep(5)
                continue

    except KeyboardInterrupt:
        print("Keyboard interrupt detected. Exiting...")
        exit(0)
