CREATE TABLE IF NOT EXISTS sayso_purchases (
    id SERIAL PRIMARY KEY,
    date DATE,
    purchase_value FLOAT,
    current_value FLOAT,
    btc_quantity FLOAT,
    close_price FLOAT
);