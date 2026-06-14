from dhanhq import dhanhq
from config import *
from datetime import date
import arrow
def get_dhan():
    dhan = dhanhq(client_id,access_token)
    return dhan

def get_present_date():
    return arrow.now().format('YYYY-MM-DD')

def get_historical_data(symbol, from_data, dhan):
    return dhan.historical_daily_data(
    symbol=symbol,
    exchange_segment=equity_exchange,
    instrument_type='EQUITY',
    expiry_code=0,
    from_date=from_data,
    to_date=get_present_date()
)


if __name__=="__main__":
    dhan = get_dhan()
    all_orders = dhan.get_order_list()
    funds_limit = dhan.get_fund_limits()
    print(get_historical_data('TCS', '2024-03-20', dhan=dhan))


