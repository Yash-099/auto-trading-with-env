from argparse import ArgumentParser
from analysis_utils import *
from trade_utils import *
from tvDatafeed import Interval
import time
from trade_utils.kite_api_call import fetch_positions, exit_position, place_kite_alert
from config import KITE_ENCTOKEN, QUANTITY

data_agent = DataAgent()

# Set SL and Target based on NIFTY Spot from command line arguments
parser = ArgumentParser()
parser.add_argument("--below", dest='below', type=float, help="BELOW trigger level on NIFTY spot")
parser.add_argument("--above", dest='above', type=float, help="ABOVE trigger level on NIFTY spot")
args = parser.parse_args()

BELOW = args.below  # Exit if NIFTY falls below this
ABOVE = args.above  # Exit if NIFTY rises above this

place_kite_alert(KITE_ENCTOKEN, "NIFTY 50", "INDICES", BELOW, "less_than")
place_kite_alert(KITE_ENCTOKEN, "NIFTY 50", "INDICES", ABOVE, "greater_than")

def monitor_and_exit():
    while True:
        try:
            # Fetch current positions
            positions = fetch_positions(KITE_ENCTOKEN)
            if not positions or 'net' not in positions['data']:
                print("No positions data available")
                time.sleep(5)
                continue

            # Find NIFTY position
            nifty_position = None
            for position in positions['data']['net']:
                if 'NIFTY' in position['tradingsymbol']:
                    nifty_position = position
                    break
            print("Nifty Position: ", nifty_position)

            if not nifty_position:
                print("No NIFTY position found")
                break

            # Fetch NIFTY Spot Price using OHLC data
            data = data_agent.get_ohlc_data('NIFTY', Interval.in_5_minute, 1, exchange='NSE')
            nifty_spot = data[-1]['close']  # Get latest close price
            print(f"Current NIFTY Spot Price: {nifty_spot}")

            # Stop-Loss Condition
            if nifty_spot <= BELOW:
                print("NIFTY hit SL level, exiting position...")
                exit_position(KITE_ENCTOKEN, nifty_position['tradingsymbol'], 
                            exchange=nifty_position['exchange'],
                            quantity=QUANTITY)
                print("NIFTY below level hit, exiting position...")
                break  # Exit the loop after placing the order

            # Target Condition
            if nifty_spot >= ABOVE:
                print("NIFTY hit Target level, exiting position...")
                exit_position(KITE_ENCTOKEN, nifty_position['tradingsymbol'],
                            exchange=nifty_position['exchange'], 
                            quantity=QUANTITY)
                print("NIFTY above level hit, exiting position...")
                break  # Exit the loop after placing the order

            time.sleep(2)  # Check every minute since we're using 5m data

        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)  # Wait before retrying

# Run the monitoring function
monitor_and_exit()
