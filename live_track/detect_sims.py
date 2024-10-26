from analysis_utils import *
from trade_utils import *
from tvDatafeed import Interval
from config import *
import time
from datetime import date, datetime
import os
from pathlib import Path
from tqdm import tqdm
import pandas as pd

if __name__ == '__main__':
        data_agent = DataAgent()
        analysis_agent = AnalysisAgent()
        try:
            while True:
                try:
                    crude_data = data_agent.get_ohlc_data("USOIL", Interval.in_5_minute, 100, exchange='TVC')
                    swings, closest = analysis_agent.get_swings(crude_data, 'down')
                    
                except Exception as e:
                    print('error:', e)
                time.sleep(60)
        except KeyboardInterrupt:
            print('stopping')
            exit(0)