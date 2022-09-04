import pandas as pd

# filter the last month data from SMA_History.CSV based on df['date'] and count each ticker
# how many time they made it to CSV file

pd.set_option('display.max_rows', None)

df = pd.read_csv("SMA_History.csv")

print(df['ticker'].value_counts())

