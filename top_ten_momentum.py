import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf


ticker_file = open(r"C:\Users\sudhi\Documents\Algorithmic_Trading\NYSE.txt","r")
ticker_list = []
for item in ticker_file:
    ticker = item.split()[0]
    ticker_list.append(ticker)
print(ticker_list)

# use yfinance to collect the data
share_data = yf.download(ticker_list, period="3mo", interval="1d", auto_adjust=True, back_adjust=True, prepost=True)

# select just Apple from the multi index to eyeball data
share_data.head()
#unquote the line below to save all data in your local drive
#share_data.to_csv('share_data.csv')

# select the close column for each ticker
data_close = share_data['Close']

#calculate the daily percentage change
data_returns = data_close.pct_change(1)

#eyeball the data
data_returns.head()

# getting rid of rows that grew by more than 90% in a day
#set the growth thresold
daily_growth_thresold = 0.9

# keep only the columns without a daily growth that big
data_returns = data_returns.loc[:, ~(data_returns>=daily_growth_thresold).any()]

#calculate cumulative daily growth
data_cum_returns = (1 + data_returns).cumprod() -1

# take the last row
latest = data_cum_returns.tail(1).T.mul(100)

# label the column
latest.columns = ['% change']

#show the top ten
topten = round(latest.sort_values(by='% change', ascending=False)[:10],2)
print(topten)

# plot the current top ten
data_cum_returns[list(topten.index)].mul(100).plot(subplots=True,
                                          layout=(5, 2),
                                          figsize=(12,12),
                                          sharex=True,
                                          ylabel='%',
                                          title='The Current Top Ten Momentum Stocks')
# tweek the layout
plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.show()





