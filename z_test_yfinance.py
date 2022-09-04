import yfinance as yf
import pandas as pd
from csv import writer


data = yf.download('AAPL', start='2021-12-01')

print(data.head())
print(data.tail())

#data.to_csv('SMA_History.csv', mode='a', header=False)

# with open('CSV_History.csv', 'a', newline='') as SMA:
#     writer_object = writer(SMA)
#     writer_object.writerow(data)
#     SMA.close()


