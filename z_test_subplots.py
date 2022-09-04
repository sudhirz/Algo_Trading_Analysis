# IMPORTING PACKAGES

import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from math import floor
import datetime
from termcolor import colored as cl

#plt.style.use('fivethirtyeight')
#plt.rcParams['figure.figsize'] = (20, 10)
#plt.rcParams['figure.figsize'] = (60, 40)


# EXTRACTING STOCK DATA

def get_historical_data(symbol, start_date):
    stock_data = yf.download(symbol, start=start_date)
    return stock_data


# ADX CALCULATION

def get_adx(High, Low, Close, lookback):
    plus_dm = High.diff()
    minus_dm = Low.diff()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm > 0] = 0

    tr1 = pd.DataFrame(High - Low)
    tr2 = pd.DataFrame(abs(High - Close.shift(1)))
    tr3 = pd.DataFrame(abs(Low - Close.shift(1)))
    frames = [tr1, tr2, tr3]
    tr = pd.concat(frames, axis=1, join='inner').max(axis=1)
    atr = tr.rolling(lookback).mean()

    plus_di = 100 * (plus_dm.ewm(alpha=1 / lookback).mean() / atr)
    minus_di = abs(100 * (minus_dm.ewm(alpha=1 / lookback).mean() / atr))
    dx = (abs(plus_di - minus_di) / abs(plus_di + minus_di)) * 100
    adx = ((dx.shift(1) * (lookback - 1)) + dx) / lookback
    adx_smooth = adx.ewm(alpha=1 / lookback).mean()
    return plus_di, minus_di, adx_smooth

# RSI CALCULATION

def get_rsi(Close, lookback):
    ret = Close.diff()
    up = []
    down = []

    for i in range(len(ret)):
        if ret[i] < 0:
            up.append(0)
            down.append(ret[i])
        else:
            up.append(ret[i])
            down.append(0)

    up_series = pd.Series(up)
    down_series = pd.Series(down).abs()

    up_ewm = up_series.ewm(com=lookback - 1, adjust=False).mean()
    down_ewm = down_series.ewm(com=lookback - 1, adjust=False).mean()

    rs = up_ewm / down_ewm
    rsi = 100 - (100 / (1 + rs))
    rsi_df = pd.DataFrame(rsi).rename(columns={0: 'rsi'}).set_index(Close.index)
    rsi_df = rsi_df.dropna()

    return rsi_df[3:]

def adx_rsi_strategy(prices, adx, pdi, ndi, rsi):
    buy_price = []
    sell_price = []
    adx_rsi_signal = []
    signal = 0

    for i in range(len(prices)):
        if adx[i] > 35 and pdi[i] < ndi[i] and rsi[i] < 50:
            if signal != 1:
                buy_price.append(prices[i])
                sell_price.append(np.nan)
                signal = 1
                adx_rsi_signal.append(signal)
            else:
                buy_price.append(np.nan)
                sell_price.append(np.nan)
                adx_rsi_signal.append(0)

        elif adx[i] > 35 and pdi[i] > ndi[i] and rsi[i] > 50:
            if signal != -1:
                buy_price.append(np.nan)
                sell_price.append(prices[i])
                signal = -1
                adx_rsi_signal.append(signal)
            else:
                buy_price.append(np.nan)
                sell_price.append(np.nan)
                adx_rsi_signal.append(0)
        else:
            buy_price.append(np.nan)
            sell_price.append(np.nan)
            adx_rsi_signal.append(0)

    return buy_price, sell_price, adx_rsi_signal

def get_benchmark(start_date, investment_value):
    spy = get_historical_data('SPY', start_date)['Close']
    benchmark = pd.DataFrame(np.diff(spy)).rename(columns={0: 'benchmark_returns'})

    investment_value = investment_value
    number_of_stocks = floor(investment_value / spy[0])
    benchmark_investment_ret = []

    for i in range(len(benchmark['benchmark_returns'])):
        returns = number_of_stocks * benchmark['benchmark_returns'][i]
        benchmark_investment_ret.append(returns)

    benchmark_investment_ret_df = pd.DataFrame(benchmark_investment_ret).rename(columns={0: 'investment_returns'})
    return benchmark_investment_ret_df

#Calculate the On Balance Volume
def calc_OBV(close, volume):
    OBV = []
    OBV.append(0)
    for i in range(1, len(close)):
        if close[i] > close[i-1]: #If the closing price is above the prior close price
              OBV.append(OBV[-1] + volume[i]) #then: Current OBV = Previous OBV + Current Volume
        elif close[i] < close[i-1]:
              OBV.append( OBV[-1] - volume[i])
        else:
              OBV.append(OBV[-1])
    return OBV

#Calculate OBV EMA
def calc_obv_ema(obv):
    #Store the OBV and OBV EMA into new columns
    return obv.ewm(com=20).mean()

start_date = datetime.datetime.now() - datetime.timedelta(days=365)
ticker = input("Enter ticker: ")
stock_data = get_historical_data(ticker, start_date)


stock_data['plus_di'] = pd.DataFrame(get_adx(stock_data['High'], stock_data['Low'], stock_data['Close'], 14)[0]).rename(columns={0: 'plus_di'})
stock_data['minus_di'] = pd.DataFrame(get_adx(stock_data['High'], stock_data['Low'], stock_data['Close'], 14)[1]).rename(
    columns={0: 'minus_di'})
stock_data['adx'] = pd.DataFrame(get_adx(stock_data['High'], stock_data['Low'], stock_data['Close'], 14)[2]).rename(columns={0: 'adx'})
stock_data = stock_data.dropna()
stock_data.tail()

# # ADX PLOT
#
# plot_data = stock_data[stock_data.index >= start_date]
#
# ax1 = plt.subplot2grid((11, 1), (0, 0), rowspan=5, colspan=1)
# ax2 = plt.subplot2grid((11, 1), (6, 0), rowspan=5, colspan=1)
# ax1.plot(plot_data['Close'], linewidth=2, color='#ff9800')
# ax1.set_title('stock_data CLOSING PRICE')
# ax2.plot(plot_data['plus_di'], color='#26a69a', label='+ DI 14', linewidth=3, alpha=0.3)
# ax2.plot(plot_data['minus_di'], color='#f44336', label='- DI 14', linewidth=3, alpha=0.3)
# ax2.plot(plot_data['adx'], color='#2196f3', label='ADX 14', linewidth=3)
# ax2.axhline(35, color='grey', linewidth=2, linestyle='--')
# ax2.legend()
# ax2.set_title('stock_data ADX 14')
# plt.show()


stock_data['rsi_14'] = get_rsi(stock_data['Close'], 14)
stock_data = stock_data.dropna()
stock_data.tail()

# # RSI PLOT
#
# plot_data = stock_data[stock_data.index >= start_date]
#
# ax1 = plt.subplot2grid((11, 1), (0, 0), rowspan=5, colspan=1)
# ax2 = plt.subplot2grid((11, 1), (6, 0), rowspan=5, colspan=1)
# ax1.plot(plot_data['Close'], linewidth=2.5)
# ax1.set_title(ticker + ' STOCK PRICES')
# ax2.plot(plot_data['rsi_14'], color='orange', linewidth=2.5)
# ax2.axhline(30, linestyle='--', linewidth=1.5, color='grey')
# ax2.axhline(70, linestyle='--', linewidth=1.5, color='grey')
# ax2.set_title(ticker + ' RSI 14')
# plt.show()


stock_data['OBV'] = calc_OBV(stock_data['Close'], stock_data['Volume'])
stock_data['OBV_EMA'] = calc_obv_ema(stock_data['OBV'])

# # OBV, OBV_EMA PLOT
# plot_data = stock_data[stock_data.index >= start_date]
#
# ax1 = plt.subplot2grid((11, 1), (0, 0), rowspan=5, colspan=1)
# ax2 = plt.subplot2grid((11, 1), (6, 0), rowspan=5, colspan=1)
# ax1.plot(plot_data['Close'], linewidth=2, color='#ff9800')
# ax1.set_title('stock_data CLOSING PRICE')
# ax2.plot(plot_data['OBV'], color='#26a69a', label='OBV', linewidth=3, alpha=0.3)
# ax2.plot(plot_data['OBV_EMA'], color='#f44336', label='OBV_EMA', linewidth=3, alpha=0.3)
# ax2.legend()
# ax2.set_title('stock_data OBV')
# plt.show()


# Calculate Bollinger Band

# Calculate 30 Day Moving Average, Std Deviation, Upper Band and Lower Band
stock_data['30 Day MA'] = stock_data['Adj Close'].rolling(window=20).mean()

# set .std(ddof=0) for population std instead of sample
stock_data['30 Day STD'] = stock_data['Adj Close'].rolling(window=20).std()

stock_data['Upper Band'] = stock_data['30 Day MA'] + (stock_data['30 Day STD'] * 2)
stock_data['Lower Band'] = stock_data['30 Day MA'] - (stock_data['30 Day STD'] * 2)



# ALL CHARTS
plot_date = datetime.datetime.now() - datetime.timedelta(days=183)
plot_data = stock_data[stock_data.index >= plot_date]

# ax1 = plt.subplot2grid((19, 1), (0, 0), rowspan=4, colspan=1)
# ax2 = plt.subplot2grid((19, 1), (4, 0), rowspan=4, colspan=1)
# ax3 = plt.subplot2grid((19, 1), (8, 0), rowspan=4, colspan=1)
# ax4 = plt.subplot2grid((19, 1), (12, 0), rowspan=4, colspan=1)
# ax5 = plt.subplot2grid((19, 1), (16, 0), rowspan=4, colspan=1)

fig, ((ax1, ax2), (ax3, ax4), (ax5, ax6)) = plt.subplots(nrows=3, ncols=2, figsize=(20, 10))
# ax1 = plt.subplot2grid((55, 5), (0, 0), rowspan=12, colspan=5)
# ax2 = plt.subplot2grid((55, 5), (12, 0), rowspan=12, colspan=5)
# ax3 = plt.subplot2grid((55, 5), (24, 0), rowspan=12, colspan=5)
# ax4 = plt.subplot2grid((55, 5), (36, 0), rowspan=12, colspan=5)
# ax5 = plt.subplot2grid((55, 5), (48, 0), rowspan=12, colspan=10)


ax1.plot(plot_data['Close'])
ax1.set_title(ticker + ' STOCK PRICES')
ax1.set_xlabel('Dates')
ax1.set_ylabel('Closing price')

ax2.plot(plot_data['Close'])
ax2.set_title(ticker + ' STOCK PRICES')
ax2.set_xlabel('Dates')
ax2.set_ylabel('Closing price')


ax3.plot(plot_data['rsi_14'], color='orange')
ax3.axhline(30, linestyle='--')
ax3.axhline(70, linestyle='--')
ax3.set_title('stock_data RSI 14')
ax3.set_xlabel('Dates')
ax3.set_xlabel('RSI 14')


ax4.plot(plot_data['plus_di'], color='#26a69a', label='+ DI 14', linewidth=3, alpha=0.3)
ax4.plot(plot_data['minus_di'], color='#f44336', label='- DI 14', linewidth=3, alpha=0.3)
ax4.plot(plot_data['adx'], color='#2196f3', label='ADX 14')
ax4.axhline(35, color='grey', linewidth=2, linestyle='--')
ax4.set_title(ticker + ' ADX 14')


ax5.plot(plot_data['OBV'], color='#26a69a', label='OBV')
ax5.plot(plot_data['OBV_EMA'], color='#f44336', label='OBV_EMA', linewidth=3, alpha=0.3)
ax5.set_title(ticker + ' OBV')


ax6.plot(stock_data['Adj Close'], color='#2196f3', label='Adj Close')
ax6.plot(stock_data['30 Day MA'], color='orange', label='30 day MA')
ax6.plot(stock_data['Upper Band'], color='green', label= 'Upper Band', alpha=0.3, linewidth=3)
ax6.plot(stock_data['Lower Band'], color='red', label='Lower Band', alpha=0.3, linewidth=3)
ax6.set_title(ticker + ' Bollinger Band')

plt.tight_layout()
plt.show()



