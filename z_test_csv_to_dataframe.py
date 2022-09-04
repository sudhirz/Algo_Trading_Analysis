import pandas as pd
pd.set_option('display.max_rows', None)

df = pd.read_csv("stockanalysis_dot_com.csv")

for item in df['ticker']:
    print(item)