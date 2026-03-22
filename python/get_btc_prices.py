import json
import os
import psycopg2
from yfinance import Ticker
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np

# Input stuff
DATE = "date"
PURCHASE_VAL = "purchase_value"
CURR_VAL = "current_value"
BTC_QTY = "btc_quantity"
CLOSE_PRICE = "close_price"

# DB STUFF
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Yfinance stuff
BTC_TICKER_NAME = "BTC-EUR"
KEYS_TO_RET = [
    'currency', 'dayHigh', 'dayLow', 'exchange', 'fiftyDayAverage', 
    'lastPrice', 'lastVolume', 'marketCap', 'open', 'previousClose', 
    'quoteType', 'regularMarketPreviousClose', 'shares', 'tenDayAverageVolume', 
    'threeMonthAverageVolume', 'timezone', 'twoHundredDayAverage', 
    'yearChange', 'yearHigh', 'yearLow'
    ]

def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def upload_to_db(purchases):
    sql = """
        INSERT INTO sayso_purchases (
            date,
            purchase_value,
            current_value,
            btc_quantity,
            close_price
        )
        VALUES (%s, %s, %s, %s, %s)
    """

    values = [
        {
            row[DATE],
            float(row[PURCHASE_VAL]),
            float(row[CURR_VAL]),
            float(row[BTC_QTY]),
            float(row[CLOSE_PRICE])
        }
        for row in purchases
    ]

    with get_connection() as db_conn:
        with db_conn.cursor() as db_cur:
            db_cur.executemany(sql, values)

            db_conn.commit()
            db_conn.close()


def get_purchase_data(purchase_data_path) -> dict:
    json_data = {}

    with open(purchase_data_path) as json_file:
        json_data = json.load(json_file)
     
    return json_data

def get_dates(purchase_data):
    dates_to_check = []
    curr_date = ""

    copy_to_check = purchase_data.copy()
    for x in copy_to_check["purchases"]:
        print(x)
        curr_date = x[DATE]
        dates_to_check.append(curr_date)

    return dates_to_check

def get_price_on_dates(btc_ticker, dates_to_check, purchase_data) -> dict:
    start = dates_to_check[0]
    end = next_day(dates_to_check[-1])

    #print(f"Purchase data: {json.dumps(purchase_data, indent=4)}")

    all_hits = btc_ticker.history(start=start, end=end, interval="1d")
    if all_hits.empty:
        raise RuntimeError("No historical data returned from yfinance.")
    
    hist_by_day = {}
    for ts, row in all_hits.iterrows():
        hist_by_day[ts.strftime("%Y-%m-%d")] = float(row["Close"])

    print(f"All hits by day: {json.dumps(hist_by_day, indent=4)}")

    for d in dates_to_check:
        close = hist_by_day.get(d)
        if close is None:
            print(f"Missing close for {d} (Yahoo gap).")
            continue

        purchase_data = insert_close_price_into_purchase_data(purchase_data, d, close)

    #print(f"My dates hits: {json.dumps(purchase_data, indent=4)}")
    return purchase_data

def insert_close_price_into_purchase_data(purchase_data, date, close_price):
    for purchase in purchase_data['purchases']:
        if purchase.get(DATE) == date:
            purchase[CLOSE_PRICE] = close_price
            break
    
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
    for purchase in dates_n_prices['purchases']:
        P_val = float(purchase[PURCHASE_VAL])
        C_price = purchase[CLOSE_PRICE]

        T_val = (P_val * T_price) / C_price

        #print(f"For date: {date}\n  - {CLOSE_PRICE}: {C_price}  -  {PURCHASE_VAL}: {P_val}\n  - last_price: '{T_price}'  -  {CURR_VAL}: {T_val}\n")

        purchase[CURR_VAL] = T_val

    full_json = dates_n_prices.copy()
    print(f"Full content: \n{json.dumps(full_json, indent=4)}")
    return full_json

def order_values(dates_n_prices):
    purchase_pts_at_og_price = []
    purchase_pts_now = []
    acc_purchase_at_og_price = [] 
    acc_purchase_now = []

    for purchase in dates_n_prices['purchases']:
        purchase_price = purchase[PURCHASE_VAL]
        current_price = purchase[CURR_VAL]

        purchase_pts_at_og_price.append(purchase_price)
        purchase_pts_now.append(current_price)

        # Do the build-up on the values at purchase price
        if len(acc_purchase_at_og_price) > 0:
            last_acc_purch_val_added = acc_purchase_at_og_price[-1]
            new_acc_purch_value = last_acc_purch_val_added + purchase_price
        else: 
            new_acc_purch_value = purchase_price
        acc_purchase_at_og_price.append(new_acc_purch_value)

        # Do the build-up on the values at purchase price
        if len(acc_purchase_now) > 0:
            last_acc_purch_now_added = acc_purchase_now[-1]
            new_acc_purch_now_value = last_acc_purch_now_added + current_price
        else: 
            new_acc_purch_now_value = current_price
        acc_purchase_now.append(new_acc_purch_now_value)

    set_of_ordered_values = {
        "purchase_pts_at_og_price": purchase_pts_at_og_price,
        "purchase_pts_now": purchase_pts_now,
        "acc_purchase_at_og_price": acc_purchase_at_og_price,
        "acc_purchase_now": acc_purchase_now
    }

    return set_of_ordered_values

def plot_data(dates, dates_n_prices):
    x = dates
    y = []

    purchases = order_values(dates_n_prices=dates_n_prices)
    
    og_points = purchases["purchase_pts_at_og_price"]
    curr_points = purchases["purchase_pts_now"]

    line_og_price = purchases["acc_purchase_at_og_price"] 
    line_curr_price = purchases["acc_purchase_now"]

    # Plot the lines
    plt.plot(dates, line_og_price, marker='o', label = "OG @ Purch $")
    plt.plot(dates, line_curr_price, marker='o', label = "Curr @ Purch $")

    # Plot individual purchase points as scatter plots for clarity
    plt.scatter(dates, og_points, color='blue', label="Purchase Points (OG $)")
    plt.scatter(dates, curr_points, color='orange', label="Purchase Points (Current $)")

    # --- ADD LABELS ABOVE POINTS ---
    for x, y in zip(dates, og_points):
        plt.annotate(f"{y:.2f}", (x, y), textcoords="offset points", xytext=(0,8), ha='center')

    for x, y in zip(dates, curr_points):
        plt.annotate(f"{y:.2f}", (x, y), textcoords="offset points", xytext=(0,-12), ha='center')

    # Make points also for the last entry in the line
    last_line_og_value = line_og_price[-1]
    last_line_curr_value = line_curr_price[-1]

    plt.annotate(f"{last_line_og_value}", (dates[-1], last_line_og_value), textcoords="offset points", xytext=(0,8), ha='center')
    plt.annotate(f"{last_line_curr_value}", (dates[-1], last_line_curr_value), textcoords="offset points", xytext=(0,-12), ha='center')

    plt.title('Purchase History')
    plt.xlabel('Dates')
    plt.ylabel('Amt')
    plt.legend()
    plt.grid()
    plt.show()


    return


def main():
    btc_ticker = Ticker(BTC_TICKER_NAME)
    # Fields returned by each check
    
    """
    # Open up the json file with the purchase info
    # Format of json:
    # {
    #     "purchases": [
    #         {
    #             "date": "YYYY-MM-DD",
    #             "purchase_value": 0.0,
    #             "current_value": 0.0,     # Can be empty
    #             "btc_quantity": 0.0,      
    #             "close_price": 0.0        # Can be empty
    #         },
    #         ...
    """


    purchase_data_path = "../data/purchase_data.json"

    purchase_data = get_purchase_data(purchase_data_path=purchase_data_path)

    dates_to_check = get_dates(purchase_data)
    dates_n_prices = get_price_on_dates(btc_ticker=btc_ticker, dates_to_check=dates_to_check, purchase_data=purchase_data)

    # Now get the current price:
    last_price = get_today_price_from_history(btc_ticker=btc_ticker)

    up_to_date_data = get_todays_comp(dates_n_prices=dates_n_prices, last_price=last_price)
    print(f"Overall findings: \n{json.dumps(up_to_date_data, indent=4)}")

    
    plot_data(dates_to_check, dates_n_prices)

    exit()
    print(f"Attempting data upload to DB: \n")
    try:
        purchase_rows = purchase_data['purchases']
        upload_to_db(purchase_rows)
    except Exception as e:
        print(f"Ran into an issue when uploading to DB... Error message: \n'{e}'")
        exit()

    print(f"Uploaded data successfully. Thanks for running!")

    
    return

if __name__ == "__main__":
        main()