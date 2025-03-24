import requests

# 🔹 Zerodha API Endpoints
POSITIONS_URL = "https://kite.zerodha.com/oms/portfolio/positions"
ORDER_URL = "https://kite.zerodha.com/oms/orders"
ALERT_URL = "https://kite.zerodha.com/oms/alerts"

def fetch_positions(enctoken):
    """
    Fetches open positions from Zerodha.
    
    Args:
        enctoken (str): Zerodha enctoken from browser cookies
    """
    headers = {
        "Authorization": f"enctoken {enctoken}"
    }
    
    response = requests.get(POSITIONS_URL, headers=headers)
    
    if response.status_code == 200:
        positions = response.json()
        # print("[📊] Positions:", positions)
        return positions
    else:
        print("[❌] Failed to fetch positions!", response.text)
        return None

def exit_position(enctoken, tradingsymbol, exchange="NFO", quantity=50):
    """
    Exits a position by placing a SELL order.
    
    Args:
        enctoken (str): Zerodha enctoken from browser cookies
        tradingsymbol (str): Trading symbol of the position to exit
        exchange (str): Exchange name (default: NFO)
        quantity (int): Quantity to exit (default: 50)
    """
    headers = {
        "Authorization": f"enctoken {enctoken}",
        "accept": "application/json, text/plain, */*",
        "content-type": "application/x-www-form-urlencoded",
        "x-kite-version": "3.0.0"
    }

    order_data = {
        "variety": "regular",
        "tradingsymbol": tradingsymbol,
        "exchange": exchange,
        "transaction_type": "BUY", # because we do option selling
        "order_type": "MARKET",
        "quantity": quantity,
        "price": 0,
        "product": "NRML", 
        "validity": "DAY",
        "disclosed_quantity": 0,
        "trigger_price": 0,
        "squareoff": 0,
        "stoploss": 0,
        "trailing_stoploss": 0
    }

    response = requests.post(ORDER_URL, headers=headers, data=order_data)

    if response.status_code == 200:
        print(f"[✅] Exit Order Placed for {tradingsymbol}!")
        print(response.json())
    else:
        print(f"[❌] Failed to exit {tradingsymbol}!", response.text)

def place_kite_alert(enctoken, tradingsymbol, exchange, price, condition="greater_than"):
    """
    Places a price alert in Zerodha Kite.
    
    :param tradingsymbol: The symbol of the stock (e.g., "NIFTY 50", "RELIANCE")
    :param exchange: "NSE", "BSE", "NFO" (for options)
    :param price: The price level for the alert
    :param condition: "greater_than" (above) or "less_than" (below)
    """

    HEADERS = {
        "Authorization": f"enctoken {enctoken}",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json, text/plain, */*",
        "X-Kite-Version": "3.0.0"
    }

    operator = ">=" if condition == "greater_than" else "<="
    
    alert_data = {
        "name": tradingsymbol,
        "lhs_exchange": exchange,
        "lhs_tradingsymbol": tradingsymbol,
        "lhs_attribute": "LastTradedPrice",
        "operator": operator,
        "rhs_type": "constant",
        "type": "simple",
        "rhs_constant": price
    }

    response = requests.post(ALERT_URL, headers=HEADERS, data=alert_data)

    if response.status_code == 200:
        print(f"[✅] Alert placed for {tradingsymbol} at {price}!")
        print(response.json())
    else:
        print(f"[❌] Failed to place alert!", response.text)