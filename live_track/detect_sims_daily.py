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

def alert(stock, direction):
    message = f'{stock}: broke the market structure in the {direction} side'
    # print(message)



def detect_shift(direction, logger):
    data_agent = DataAgent()
    analysis_agent = AnalysisAgent()
    stocks = nifty_50_stocks + mid_cap_stocks + small_cap_stocks
    filtered_stocks = []
    try:
        for i in tqdm(range(len(stocks))):
            try:
                stock = stocks[i]
                data = data_agent.get_ohlc_data(stock, Interval.in_daily, 100, exchange='NSE')
                if direction == 'up':
                    _, closest = analysis_agent.get_swings(data, 'up')
                    # market shifted and alert sent
                    if data[-1]['high'] > closest:
                        logger.info(f'{stock} shifted in the up side')
                        alert(stock, direction)
                        filtered_stocks.append(stock)
                    
                elif direction == 'down':
                    _, closest = analysis_agent.get_swings(data, 'down')
                    logger.info(f'{stock} closest swing low- {closest}')
                    # market shifted and alert sent
                    if data[-1]['low'] < closest:
                        logger.info(f'{stock} shifted in the down side')
                        alert(stock, direction)

                else:
                    logger.error('direction provided not known')
                    exit(0)

            except Exception as e:
                logger.error(e)
                print('error:', e)
        print('filtered stocks:', filtered_stocks)
    except KeyboardInterrupt:
        print('stopping')
        exit(0)


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    logging.basicConfig(filename='log_file.txt', level=logging.DEBUG, format='%(asctime)s %(message)s')

    parser = ArgumentParser()
    parser.add_argument("--direction", dest='direction',  help="direction to track, up or down")
    args = parser.parse_args()

    detect_shift(args.direction, logger)