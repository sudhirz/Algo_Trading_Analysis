from get_stock import get_stock
from get_rsi import get_rsi
import yfinance as yf
import datetime
from matplotlib import pyplot as plt

plt.style.use('fivethirtyeight')
plt.rcParams['figure.figsize'] = (20, 10)


ticker = input("Enter Ticker: ")
start_date = datetime.datetime.now() - datetime.timedelta(days=365)  # one year ago
interval = '1d'
period = '1yr'
stock_data = get_stock(ticker, start_date, interval, period)

stock_data['rsi_14'] = get_rsi(stock_data['Close'], 14)

ax1 = plt.subplot2grid((19, 1), (0, 0), rowspan=10, colspan=1)
ax2 = plt.subplot2grid((19,1), (10, 0), rowspan=10, colspan=1)

ax1.plot(stock_data['Close'], label='Closing Price', linewidth=2.5)
ax1.set_title(ticker + ' STOCK PRICES')
ax1.legend()

ax2.plot(stock_data['rsi_14'], label='RSI 14', color='orange', linewidth=2.5)
ax2.axhline(30, linestyle='--', linewidth=1.5, color='grey')
ax2.axhline(70, linestyle='--', linewidth=1.5, color='grey')
ax2.legend()
ax2.set_title('stock_data RSI 14')

plt.show()
