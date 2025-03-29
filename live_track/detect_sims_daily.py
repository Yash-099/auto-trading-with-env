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




def detect_shift(direction, logger):
    data_agent = DataAgent()
    analysis_agent = AnalysisAgent()
    stocks = {"nifty_50_stocks": nifty_50_stocks, "mid_cap_stocks": mid_cap_stocks, "small_cap_stocks": small_cap_stocks}
    filtered_stocks = {stock_list_name: [] for stock_list_name in stocks.keys()}
    try:
        for stock_list_name, stock_list in stocks.items():
            for stock in tqdm(stock_list):
                try:
                    data = data_agent.get_ohlc_data(stock, Interval.in_daily, 30, exchange='NSE')
                    if direction == 'up':
                        swings, _ = analysis_agent.get_swings(data, 'up')
                        # market shifted and alert sent
                        if len(swings) > 0 and data[-1]['high'] > swings[0]:
                            logger.info(f'{stock} shifted in the up side')
                            filtered_stocks[stock_list_name].append(stock)
                        
                    elif direction == 'down':
                        swings, _ = analysis_agent.get_swings(data, 'down')
                        logger.info(f'{stock} closest swing low- {swings[-1]}')
                        # market shifted and alert sent
                        if len(swings) > 0 and data[-1]['low'] < swings[-1]:
                            logger.info(f'{stock} shifted in the down side')
                            filtered_stocks[stock_list_name].append(stock)

                    else:
                        logger.error('direction provided not known')
                        exit(0)

                except Exception as e:
                    logger.error(e)
                    print('error:', e)
            print(f'{stock_list_name} filtered stocks:', filtered_stocks[stock_list_name])
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