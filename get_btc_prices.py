import json
import csv
from yfinance import Ticker
from datetime import datetime, timedelta


def get_fast_info(btc_ticker, keys_to_ret):
     
    fast_info = btc_ticker.get_fast_info()

    #print(f"BTC Info: {json.dumps(, indent=4)}")
    print(f"Fast info: {fast_info}")

    for key in keys_to_ret:
        if key in fast_info:
            current_element = fast_info[key]
            print(f"For key '{key}':\n{current_element}\n---------------")
            
        last_price = fast_info['lastPrice']
     
def get_price_on_dates(btc_ticker, dates_to_check):
    dates_n_prices = {}

    for x in dates_to_check:
        day_4_ticker = btc_ticker.history(start=x, end=next_day(x), interval="1d")
        #end_price = float(day_4_ticker["Close"].iloc[0])
        if day_4_ticker.empty:
            print(f"Found nothing for: {x}")
            continue

        #print(f"Price for '{x}'\n{day_4_ticker}\n")

        close_price = float(day_4_ticker["Close"].iloc[0])
        #print(f"Close price: {close_price}")

        if x not in dates_n_prices:
             dates_n_prices[x] = close_price
     
    return dates_n_prices

def get_purchase_data(dates_json_path):
    dates = []

    with open(dates_csv_path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')

        for row in csv_reader:
            current_date = row[0]
            dates.append(current_date)
     
    return dates

def main():

    btc_ticker = Ticker("BTC-EUR")
    
    keys_to_ret = ['currency', 'dayHigh', 'dayLow', 'exchange', 'fiftyDayAverage', 'lastPrice', 'lastVolume', 
                   'marketCap', 'open', 'previousClose', 'quoteType', 'regularMarketPreviousClose', 'shares', 
                   'tenDayAverageVolume', 'threeMonthAverageVolume', 'timezone', 'twoHundredDayAverage', 'yearChange', 
                   'yearHigh', 'yearLow']
    
    purchase_data_path = "purchase_data.json"

    purchase_data = get_purchase_data(purchase_data_path)

    #get_fast_info(btc_ticker=btc_ticker, keys_to_ret=keys_to_ret)

    dates_to_check = purchase_data.keys()
    dates_n_prices = get_price_on_dates(btc_ticker=btc_ticker, dates_to_check=dates_to_check)


    print(f"Overall findings: \n{json.dumps(dates_n_prices, indent=4)}")
    return

def next_day(date_str: str) -> str:
    d = datetime.strptime(date_str, "%Y-%m-%d")
    return (d + timedelta(days=1)).strftime("%Y-%m-%d")

if __name__ == "__main__":
        main()