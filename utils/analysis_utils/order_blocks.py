from utils.analysis_utils import *
from tvDatafeed import Interval
from data.config import *
from datetime import date
from pathlib import Path

class OBS:
    def get_bullish_orderblocks(self, stock, time_frame, candles=10):
        data_agent = DataAgent()
        try:
            data = data_agent.get_ohlc_data(stock, time_frame, candles)
        except Exception as e:
            if isinstance(e, IndexError):
                print(f'not sufficient data dropping {stock}')
                return []
            time.sleep(5)
            return self.get_bullish_orderblocks(stock, time_frame, candles)
        
        analysis_agent = AnalysisAgent()
        order_blocks = analysis_agent.find_bullish_orderblocks(data)
        return order_blocks
