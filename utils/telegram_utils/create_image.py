from data.config import DataAgent
from tvDatafeed import Interval
import matplotlib.pyplot as plt
import mplfinance as mpf
import os

def create_candle_chart(stock, exchange='NSE', interval=None, n_bars=30, image_path=None):
    """
    Creates a candlestick chart for the given stock using the ohlc function and saves it to the specified image path.

    Args:
        stock (str): Stock symbol.
        exchange (str): Exchange name. Default is 'NSE'.
        interval: Data interval (e.g., Interval.in_3_monthly).
        n_bars (int): Number of bars/candles to plot.
        image_path (str): Path to save the generated image.

    Returns:
        str: Path to the saved image.
    """

    # Import ohlc function from wherever it is defined
    from utils.analysis_utils import ohlc

    # Set default interval if not provided
    if interval is None:
        from tvDatafeed import Interval
        interval = Interval.in_3_monthly

    data_agent = DataAgent()
    # Use the provided interval or default to Interval.in_3_monthly
    _interval = interval if interval is not None else Interval.in_3_monthly
    df = data_agent.get_ohlc_data(stock, _interval, n_bars, exchange)

    if df is None or len(df) == 0:
        raise ValueError(f"No data found for {stock} on {exchange} with interval {_interval}")

    # Prepare data for mplfinance
    df = df.copy()
    df.index.name = 'Date'
    # Ensure columns are named as expected by mplfinance
    df = df[['open', 'high', 'low', 'close', 'volume']]
    df.columns = [col.capitalize() for col in df.columns]

    # Set image path if not provided
    if image_path is None:
        image_path = f"{stock}_{exchange}_{interval}_{n_bars}.png"
    else:
        # Ensure directory exists
        dir_name = os.path.dirname(image_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)

    # Plot candlestick chart
    mpf.plot(
        df,
        type='candle',
        style='charles',
        title=f"{stock} ({exchange}) - {interval} - Last {n_bars} Bars",
        ylabel='Price',
        ylabel_lower='Volume',
        volume=True,
        savefig=dict(fname=image_path, dpi=150, bbox_inches='tight')
    )

    return image_path
