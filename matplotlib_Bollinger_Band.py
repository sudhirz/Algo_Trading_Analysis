# import needed libraries
from get_stock import get_stock
import matplotlib.pyplot as plt
import datetime
from get_bollinger_band import get_bollinger_band


ticker = input("Enter Ticker: ")
start_date = datetime.datetime.now() - datetime.timedelta(days=365)  # one year ago
interval = '1d'
period = '1yr'
stock_data = get_stock(ticker, start_date, interval, period)

# # Calculate 30 Day Moving Average, Std Deviation, Upper Band and Lower Band
#
# stock_data['30 Day MA'] = stock_data['Adj Close'].rolling(window=20).mean()
#
# # set .std(ddof=0) for population std instead of sample
# stock_data['30 Day STD'] = stock_data['Adj Close'].rolling(window=20).std()
#
# stock_data['Upper Band'] = stock_data['30 Day MA'] + (stock_data['30 Day STD'] * 2)
# stock_data['Lower Band'] = stock_data['30 Day MA'] - (stock_data['30 Day STD'] * 2)

stock_data['30 Day MA'], stock_data['Upper Band'], stock_data['Lower Band'] = get_bollinger_band(stock_data['Adj Close'])

# Simple 30 Day Bollinger Band for Facebook (2016-2017)
stock_data[['Adj Close', '30 Day MA', 'Upper Band', 'Lower Band']].plot(figsize=(12, 6))
plt.title('30 Day Bollinger Band' + ticker)
plt.ylabel('Price (USD)')
plt.show()