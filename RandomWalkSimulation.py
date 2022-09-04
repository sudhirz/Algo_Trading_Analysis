# Monte Carlo simulation
import yfinance as yf
import pandas as pd
import datetime as dt
import numpy as np
import matplotlib.pyplot as plt

start = dt.datetime(2021,1,1)
end = dt.datetime(2022,1,1)

stock_data = yf.download('MSFT', start, end)


# Estimation of Daily Volatility of Stock

returns = stock_data['Adj Close'].pct_change()
daily_vol = returns.std()
# https://medium.com/the-handbook-of-coding-in-finance/simulating-random-walk-of-stock-prices-with-monte-carlo-simulation-in-python-6e233d841e

# 1. Use of pct_change method to obtain percentage changes of the adjusted close prices of the current
#    day compated with the resulting percentage of price changes are know as stock returns
# 2. The daily volatility of the stock is equivalent to the standard deviation of the stock returns.
#    We can use the std methond to calculate the standard deviation of the stock returns.


# Running singe simulation

T = 252
# count = 0
# price_list = []
last_price = stock_data['Adj Close'][-1]
#
# price = last_price * (1 + np.random.normal(0, daily_vol))
# price_list.append(price)
#
# for y in range(T):
#     if count == 252:
#         break
#     price = price_list[count] * (1 + np.random.normal(0, daily_vol))
#     price_list.append(price)
#     count += 1
#
# plt.plot(price_list)
# plt.show()

# Line 1-4: Initialize the variables with an initial value, respectively. The variable T refers to the
#           numbers of trading days while the count variable will be used as a required counter to
#           ensure the simulated stock prices are only generated for 252 days. The price_list will hold
#           the list of simulated stock prices and the last_price stores final value of the adjusted
#           close price of the stock data.

# Line 6-7: Use the Numpy normal method to draw random samples from a Normal Distribution with mu=0
#           and sigma = daily volatility. Multiply the drawn random samples with the last price to
#           generate a simulated stock price. Append the simulated price to the price_list. By now we
#           have already generated a simulated stock price just for one day trading.

# Line 9-14: Create a loop to repeat the process of generating simulated stock prices for subsequent
#            251 days. Each simulated stock price will be added to the price_list.

# Line 16-17: Create a line chart to visualize our first simulated stock prices for 252 trading days.


NUM_SIMULATIONS = 1000
df = pd.DataFrame()
last_price_list = []
for x in range(NUM_SIMULATIONS):
    count = 0
    price_list = []
    price = last_price * (1 + np.random.normal(0, daily_vol))
    price_list.append(price)

    for y in range(T):
        if count == 251:
            break
        price = price_list[count] * (1 + np.random.normal(0, daily_vol))
        price_list.append(price)
        count += 1

    df[x] = price_list
    last_price_list.append(price_list[-1])

fig = plt.figure()
fig.suptitle("Monte Carlo Simulation: MSFT")
plt.plot(df)
plt.xlabel('Day')
plt.ylabel('Price')
plt.show()

print("Expected price: ", round(np.mean(last_price_list),2))
print("Quantile (5%): ",np.percentile(last_price_list,5))
print("Quantile (95%): ",np.percentile(last_price_list,95))

plt.hist(last_price_list,bins=100)
plt.axvline(np.percentile(last_price_list,5), color='r', linestyle='dashed', linewidth=2)
plt.axvline(np.percentile(last_price_list,95), color='r', linestyle='dashed', linewidth=2)
plt.show()
