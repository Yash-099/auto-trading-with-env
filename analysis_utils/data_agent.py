from tvDatafeed import TvDatafeed
import pandas
import json
import time
from datetime import datetime

class DataAgent:
    def __init__(self) -> None:
        self.tv_agent = TvDatafeed()
    def get_ohlc_data_internal(self, symbol, interval, n_bars, exchange='NSE', futures=False):
        if futures:
                stock_history_data = self.tv_agent.get_hist(symbol=symbol, exchange=exchange,interval=interval, n_bars=n_bars, fut_contract=1)
        else:
            stock_history_data = self.tv_agent.get_hist(symbol=symbol, exchange=exchange,interval=interval, n_bars=n_bars)
        stock_history_data_json = []
        for i in range(n_bars):
            k = stock_history_data.iloc[i,:].name
            # k = k.to_pydatetime().strftime('%m/%d/%Y')
            stock_history_data_json.append({"symbol":stock_history_data.iloc[i,:].symbol, 
                                "open":stock_history_data.iloc[i,:].open,
                                "low":stock_history_data.iloc[i,:].low,
                                "close":stock_history_data.iloc[i,:].close,
                                "high":stock_history_data.iloc[i,:].high,
                                "datetime":k})
        return stock_history_data_json

    def get_ohlc_data(self, symbol, interval, n_bars, exchange='NSE', futures=False):
        try:
            return self.get_ohlc_data_internal(symbol, interval, n_bars, exchange, futures)
        except Exception as e:
            if "out of range" in str(e) or "out-of-bounds" in str(e):
                print(f'not sufficient data dropping {symbol}')
                return []
            time.sleep(3)
            return self.get_ohlc_data_internal(symbol, interval, n_bars, exchange, futures)

    def get_avg_graph(self,data_json):
        avg = []
        for i in data_json:
            avg.append((i['low']+i['high'])/2)
        return avg

    def get_ohlc_data_test(self, symbol, interval, n_bars, exchange='NSE', futures=False, date_now=None, time_now=None, data=None):
        for i in range(len(data)-1, 0, -1):
            if datetime.combine(date_now, time_now) > data[i]['datetime']:
                return [data[i-1], data[i]]
