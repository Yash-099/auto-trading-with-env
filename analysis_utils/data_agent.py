from tvDatafeed import TvDatafeed
import pandas
import json

class DataAgent:
    def __init__(self) -> None:
        self.tv_agent = TvDatafeed()

    def get_ohlc_data(self, symbol, interval, n_bars, exchange='NSE'):
        stock_history_data = self.tv_agent.get_hist(symbol=symbol, exchange=exchange,interval=interval, n_bars=n_bars)
        stock_history_data_json = []
        for i in range(n_bars):
            try:
                k = stock_history_data.iloc[i,:].name
            except:
                print(symbol)
            k = k.to_pydatetime().strftime('%m/%d/%Y')
            stock_history_data_json.append({"symbol":stock_history_data.iloc[i,:].symbol, 
                                "open":stock_history_data.iloc[i,:].open,
                                "low":stock_history_data.iloc[i,:].low,
                                "close":stock_history_data.iloc[i,:].close,
                                "high":stock_history_data.iloc[i,:].high,
                                "datetime":k})
        return stock_history_data_json

    def get_avg_graph(self,data_json):
        avg = []
        for i in data_json:
            avg.append((i['low']+i['high'])/2)
        return avg
