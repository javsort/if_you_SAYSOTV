FROM python:3.12.13-slim

WORKDIR /app

COPY data/purchase_data.json /app/data/

COPY python/reqs.txt .

RUN pip install --no-cache-dir -r reqs.txt

COPY python/get_btc_prices.py .

CMD ["python", "get_btc_prices.py"]