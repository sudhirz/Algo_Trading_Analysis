import yfinance as yf

def get_stock(ticker, start_date, interval, period):
    stock_data = yf.download(ticker, start=start_date, interval=interval, period=period)
    return stock_data

