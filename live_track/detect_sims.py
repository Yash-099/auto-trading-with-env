from analysis_utils import *
from trade_utils import *
from tvDatafeed import Interval
from config import *
import time
from datetime import date, datetime
import os
from pathlib import Path
from argparse import ArgumentParser
from tqdm import tqdm
import pandas as pd
import logging
def show_notification(title, message):
    send_notification.notify(title, message, logger)

def alert(time, instrument, level, direction):
    message = 'NONE'
    if direction == 'up':
        message = f'Took buyside'
    elif direction == 'down':
        message = f'Took sellside'
    show_notification(instrument, message)

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


def detect_shift(level, direction, instrument, exchange, logger, futures=False, mohawk_allowed=0.002):
    data_agent = DataAgent()
    analysis_agent = AnalysisAgent()
    try:
        while True:
            try:
                data = data_agent.get_ohlc_data(instrument, Interval.in_5_minute, 100, exchange=exchange, futures=futures)
                if direction == 'up':
                    _, closest = analysis_agent.get_swings(data, 'up', strong=False)
                    logger.info(f'{instrument} closest swing high- {closest}')
                    # market shifted and alert sent
                    if data[-1]['high'] > closest:
                        logger.info(f'{instrument} shifted in the up side')
                        alert(datetime.now(), instrument, level, direction)
                        break
                    # market not respecting the level
                    if level:
                        if data[-1]['high'] < level* (1-mohawk_allowed):
                            logger.info('level breached going back to tracking')
                            break
                elif direction == 'down':
                    _, closest = analysis_agent.get_swings(data, 'down', strong=False)
                    logger.info(f'{instrument} closest swing low- {closest}')
                    # market shifted and alert sent
                    if data[-1]['low'] < closest:
                        logger.info(f'{instrument} shifted in the down side')
                        alert(datetime.now(), instrument, level, direction)
                        break
                    # market not respecting the level
                    if level:
                        if data[-1]['low'] > level* (1+mohawk_allowed):
                            logger.info('level breached going back to tracking')
                            break
                elif direction == 'both':
                    _, closest_high = analysis_agent.get_swings(data, 'up', strong=False)
                    _, closest_low = analysis_agent.get_swings(data, 'down', strong=False)
                    logger.info(f'{instrument} closest swing high- {closest_high}')
                    logger.info(f'{instrument} closest swing low- {closest_low}')
                    # market shifted and alert sent
                    if data[-1]['high'] > closest_high:
                        logger.info(f'{instrument} shifted in the up side')
                        alert(datetime.now(), instrument, level, 'up')
                        break
                    if data[-1]['low'] < closest_low:
                        logger.info(f'{instrument} shifted in the down side')
                        alert(datetime.now(), instrument, level, 'down')
                        break
                else:
                    logger.error('direction provided not known')
                    exit(0)

            except Exception as e:
                logger.error(e)
                print('error:', e)
            time.sleep(60)
    except KeyboardInterrupt:
        print('stopping')
        exit(0)


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    logging.basicConfig(filename='log_file.txt', level=logging.DEBUG, format='%(asctime)s %(message)s')

    parser = ArgumentParser()
    parser.add_argument("--instrument", dest='instrument',  help="instrument to track, supported USOIL and NIFTY")
    parser.add_argument("--level", dest='level',  help="level to track")
    parser.add_argument("--direction", dest='direction',  help="direction to track, up or down")
    args = parser.parse_args()
    instrument_config = {
        'USOIL': {'exchange': 'TVC', 
                  'futures':False, 
                  'start_time': datetime.strptime("22:00:00", "%H:%M:%S").time(), 
                  'end_time': datetime.strptime("20:00:00", "%H:%M:%S").time()},
        'NIFTY': {'exchange': 'NSE', 
                  'futures':False,
                  'start_time': datetime.strptime("09:15:00", "%H:%M:%S").time(), 
                  'end_time': datetime.strptime("15:30:00", "%H:%M:%S").time()}
    }
    instrument = args.instrument
    exchange = instrument_config[instrument]['exchange']
    futures = instrument_config[instrument]['futures']

    while True:
        if stop_tracking(args.instrument, instrument_config, datetime.now().time(), datetime.now().strftime("%A")):
            print(f'{instrument} is not trading today')
            continue

        detect_shift(None, args.direction, instrument, exchange, logger, futures=futures)
        time.sleep(300)