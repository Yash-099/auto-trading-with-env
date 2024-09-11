from config import *
from argparse import ArgumentParser
from analysis_utils import *
from tqdm import tqdm
def is_ath_recent(prices, time):
    # time in months
    # prices will be monthly chart's ohlc data for last 10 years
    ath_months = 0
    ath = 0
    for i in range(len(prices)-1, -1, -1):
        if prices[i]['high'] > ath:
            ath_months = len(prices)-i
            ath = prices[i]['high']
    if time < ath_months:
        return False
    return True

if __name__=="__main__":
    parser = ArgumentParser()
    data_agent = DataAgent()
    parser.add_argument("--years", dest='years', help="number of years to consider for all time high", type=int)
    parser.add_argument("--stocks", dest='stocks',  help="Stocks to track take from the keys in all stocks variable in config")
    args = parser.parse_args()
    filtered = 0
    total = 0
    stocks_to_look = []
    for i in tqdm(range(len(all_stocks[args.stocks]))):
        stock = all_stocks[args.stocks][i]
        try:
            data = data_agent.get_ohlc_data(stock, Interval.in_monthly, 12*args.years)
        except Exception as error:
            print(f'skipping {stock}', error)
            continue
        total += 1
        if not is_ath_recent(data, 4):
            stocks_to_look.append(stock)
        else:
            filtered += 1
    print(stocks_to_look)
    print()
    print('out of', total, 'filtered', filtered)