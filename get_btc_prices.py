import json
from yfinance import Ticker
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np

def get_purchase_data(purchase_data_path) -> dict:
    json_data = {}

    with open(purchase_data_path) as json_file:
        json_data = json.load(json_file)
     
    return json_data


def get_price_on_dates(btc_ticker, dates_to_check, purchase_data) -> dict:
    start = dates_to_check[0]
    end = next_day(dates_to_check[-1])

    all_hits = btc_ticker.history(start=start, end=end, interval="1d")
    if all_hits.empty:
        raise RuntimeError("No historical data returned from yfinance.")
    
    hist_by_day = {}
    for ts, row in all_hits.iterrows():
        hist_by_day[ts.strftime("%Y-%m-%d")] = float(row["Close"])

    #print(f"All hits by day: {json.dumps(hist_by_day, indent=4)}")
    for d in dates_to_check:
        close = hist_by_day.get(d)
        if close is None:
            print(f"Missing close for {d} (Yahoo gap).")
            continue

        purchase_data[d]["close_price"] = close

    #print(f"My dates hits: {json.dumps(purchase_data, indent=4)}")

    return purchase_data


def next_day(date_str: str) -> str:
    d = datetime.strptime(date_str, "%Y-%m-%d")
    return (d + timedelta(days=1)).strftime("%Y-%m-%d")


def get_today_price_from_history(btc_ticker) -> float:
    recent = btc_ticker.history(period="5d", interval="1d")
    if recent.empty:
        raise RuntimeError("No recent data for today's price.")
    return float(recent["Close"].iloc[-1])


def get_todays_comp(dates_n_prices, last_price) -> dict:
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

        #print(f"For date: {date}\n  - close_price: {C_price}  -  purchase_value: {P_val}\n  - last_price: '{T_price}'  -  current_value: {T_val}\n")

        dates_n_prices[date]["current_value"] = T_val

    full_json = dates_n_prices.copy()
    return full_json

def order_values(dates_n_prices, value_2_pick):
    ordered_values = []

    for date, content in dates_n_prices.items():
        curr_val = content[value_2_pick]

        ordered_values.append(curr_val)

    return ordered_values

def plot_data(dates, dates_n_prices):

    x = dates
    y = []

    purchase_value_arr = order_values(dates_n_prices=dates_n_prices, value_2_pick="purchase_value")
    current_value_arr = order_values(dates_n_prices=dates_n_prices, value_2_pick="current_value")

    # 
    plt.plot(dates, purchase_value_arr, marker='o')
    plt.title('Purchase History')
    plt.xlabel('Dates')
    plt.ylabel('Amt')
    plt.show()


    return


def main():
    btc_ticker = Ticker("BTC-EUR")
    # Fields returned by each check
    keys_to_ret = ['currency', 'dayHigh', 'dayLow', 'exchange', 
                   'fiftyDayAverage', 'lastPrice', 'lastVolume', 
                   'marketCap', 'open', 'previousClose', 'quoteType', 
                   'regularMarketPreviousClose', 'shares', 'tenDayAverageVolume', 
                   'threeMonthAverageVolume', 'timezone', 'twoHundredDayAverage', 
                   'yearChange', 'yearHigh', 'yearLow']
    
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

    dates_to_check = sorted(purchase_data.keys())
    dates_n_prices = get_price_on_dates(btc_ticker=btc_ticker, dates_to_check=dates_to_check, purchase_data=purchase_data)

    # Now get the current price:
    last_price = get_today_price_from_history(btc_ticker=btc_ticker)

    up_to_date = get_todays_comp(dates_n_prices=dates_n_prices, last_price=last_price)
    print(f"Overall findings: \n{json.dumps(up_to_date, indent=4)}")

    plot_data(dates_to_check, dates_n_prices)
    
    return

if __name__ == "__main__":
        main()