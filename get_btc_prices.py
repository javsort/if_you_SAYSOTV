import json
from yfinance import Ticker
from datetime import datetime, timedelta

def get_purchase_data(purchase_data_path):
    json_data = {}

    with open(purchase_data_path) as json_file:
        json_data = json.load(json_file)
     
    return json_data


def get_price_on_dates(btc_ticker, dates_to_check, purchase_data):

    for x in dates_to_check:
        day_4_ticker = btc_ticker.history(start=x, end=next_day(x), interval="1d")
        if day_4_ticker.empty:
            print(f"Found nothing for: {x}")
            continue

        #print(f"Price for '{x}'\n{day_4_ticker}\n")

        close_price = float(day_4_ticker["Close"].iloc[0])
        #print(f"Close price: {close_price}")

        if x in purchase_data:
            purchase_data[x]["close_price"] = close_price
     
    return purchase_data


def next_day(date_str: str) -> str:
    d = datetime.strptime(date_str, "%Y-%m-%d")
    return (d + timedelta(days=1)).strftime("%Y-%m-%d")


def get_fast_info(btc_ticker, keys_to_ret):
     
    fast_info = btc_ticker.get_fast_info()
    last_price = fast_info['lastPrice']

    #print(f"BTC Info: {json.dumps(, indent=4)}")
    #print(f"Fast info: {fast_info}")
    # for key in keys_to_ret:
    #     if key in fast_info:
    #         current_element = fast_info[key]
    #         print(f"For key '{key}':\n{current_element}\n---------------")

    return last_price


def get_todays_comp(dates_n_prices, last_price):
    """
    Purchase value - P_val      -     Bought at close price - C_price
    Current value -  T_val      -     Today's Price - T_price
    
    Formula: X = (P_val * T_price) / C_price
    """
    full_json = {}
    
    T_price = last_price
    for date, content in dates_n_prices.items():
        P_val = float(content["purchase_value"])
        C_price = content["close_price"]

        T_val = (P_val * T_price) / C_price

        print(f"For date: {date}\n  - close_price: {C_price}  -  purchase_value: {P_val}\n  - last_price: '{T_price}'  -  current_value: {T_val}\n")

        dates_n_prices[date]["current_value"] = T_val

    full_json = dates_n_prices.copy()
    return full_json


def main():
    btc_ticker = Ticker("BTC-EUR")
    keys_to_ret = ['currency', 'dayHigh', 'dayLow', 'exchange', 'fiftyDayAverage', 
                   'lastPrice', 'lastVolume', 'marketCap', 'open', 'previousClose', 
                   'quoteType', 'regularMarketPreviousClose', 'shares', 'tenDayAverageVolume', 
                   'threeMonthAverageVolume', 'timezone', 'twoHundredDayAverage', 'yearChange', 
                   'yearHigh', 'yearLow']
    
    """
    # Open up the json file with the purchase info
    # Format of json:
    # {
    #     "YYYY-MM-DD": {
    #         "purchase_value": 0,
    #         "current_value": 0,
    #         "btc_quantity": 0,
    #         "close_price": 0
    #     },
    #     ...
    # }
    """
    purchase_data_path = "purchase_data.json"

    purchase_data = get_purchase_data(purchase_data_path=purchase_data_path)

    dates_to_check = purchase_data.keys()
    dates_n_prices = get_price_on_dates(btc_ticker=btc_ticker, dates_to_check=dates_to_check, purchase_data=purchase_data)


    # Now get the current price:
    last_price = get_fast_info(btc_ticker=btc_ticker, keys_to_ret=keys_to_ret)

    up_to_date = get_todays_comp(dates_n_prices=dates_n_prices, last_price=last_price)
    print(f"Overall findings: \n{json.dumps(up_to_date, indent=4)}")
    
    return

if __name__ == "__main__":
        main()