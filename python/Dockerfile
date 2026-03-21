FROM python:3.12.13-slim

WORKDIR /app

COPY reqs.txt . 

RUN pip install --no-cache-dir -r reqs.txt

COPY get_btc_prices.py .

CMD ["python", "get_btc_prices.py"]