from get_stock import get_stock
from matplotlib import pyplot as plt
import datetime
from get_adx import get_adx
import pandas as pd

ticker = input("Enter Ticker: ")
start_date = datetime.datetime.now() - datetime.timedelta(days=365)  # one year ago
interval = '1d'
period = '1yr'
stock_data = get_stock(ticker, start_date=start_date, interval=interval, period=period)


stock_data['adx_plus_di'] = pd.DataFrame(get_adx(stock_data['High'], stock_data['Low'], stock_data['Close'], 14)[0]).rename(columns={0: 'plus_di'})
stock_data['adx_minus_di'] = pd.DataFrame(get_adx(stock_data['High'], stock_data['Low'], stock_data['Close'], 14)[1]).rename(
    columns={0: 'minus_di'})
stock_data['adx'] = pd.DataFrame(get_adx(stock_data['High'], stock_data['Low'], stock_data['Close'], 14)[2]).rename(columns={0: 'adx'})
stock_data = stock_data.dropna()
stock_data.tail()


ax1 = plt.subplot2grid((19, 1), (0, 0), rowspan=10, colspan=1)
ax2 = plt.subplot2grid((19,1), (10, 0), rowspan=10, colspan=1)

ax1.plot(stock_data['Close'], label='Closing Price', color='blue')
ax1.set_title(ticker + ' STOCK PRICES')
ax1.legend()

ax2.plot(stock_data['adx_plus_di'], label='adx_plus_di', color='orange')
ax2.plot(stock_data['adx'], label='ADX', color='green')
ax2.plot(stock_data['adx_minus_di'], label='adx_minus', color='red')
ax2.legend()
ax2.set_title('ADX')

plt.show()