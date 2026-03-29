CREATE TABLE IF NOT EXISTS sayso_purchases (
    id SERIAL PRIMARY KEY,
    date DATE UNIQUE,
    purchase_value FLOAT,
    current_value FLOAT,
    btc_quantity FLOAT,
    close_price FLOAT
);

CREATE TABLE IF NOT EXISTS sayso_btc_eur_price_hist (
    date DATE PRIMARY KEY,
    btc_value FLOAT
);