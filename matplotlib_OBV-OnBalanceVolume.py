from get_stock import get_stock
import numpy as np
import matplotlib.pyplot as plt
import datetime
#plt.style.use('fivethirtyeight')

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

# Create a function to signal when to buy and sell an asset
# If OBV > OBV_EMA Then Buy
# If OBV < OBV_EMA Then Sell
# Else Do nothing
def buy_sell(signal, col1, col2):
    sigPriceBuy = []
    sigPriceSell = []
    flag = -1  # A flag for the trend upward/downward
    # Loop through the length of the data set
    for i in range(0, len(signal)):
        # if OBV > OBV_EMA  and flag != 1 then buy else sell
        if signal[col1][i] > signal[col2][i] and flag != 1:
            sigPriceBuy.append(signal['Close'][i])
            sigPriceSell.append(np.nan)
            flag = 1
        # else  if OBV < OBV_EMA  and flag != 0 then sell else buy
        elif signal[col1][i] < signal[col2][i] and flag != 0:
            sigPriceSell.append(signal['Close'][i])
            sigPriceBuy.append(np.nan)
            flag = 0
        # else   OBV == OBV_EMA  so append NaN
        else:
            sigPriceBuy.append(np.nan)
            sigPriceSell.append(np.nan)

    return (sigPriceBuy, sigPriceSell)

if __name__ == "__main__":
    ticker = input("Enter Ticker: ")
    start_date = datetime.datetime.now() - datetime.timedelta(days=365)  # one year ago
    interval = '1d'
    period = '1yr'
    df = get_stock(ticker, start_date, interval, period)

    close = df['Close']
    volume = df['Volume']

    df['OBV'] = calc_OBV(close, volume)
    df['OBV_EMA'] = calc_obv_ema(df['OBV'])

    #Create and plot the graph
    plt.figure(figsize=(12.2,4.5))
    df[['Close', 'OBV', 'OBV_EMA']].plot(figsize=(12, 6))
    # plt.plot(df['Close'],  label='Close', color='blue')
    # plt.plot(df['OBV'],  label='OBV', color= 'orange')
    # plt.plot(df['OBV_EMA'],  label='OBV_EMA', color= 'purple')
    #plt.xticks(rotation=45)
    plt.title('OBV/OBV_EMA')
    #plt.xlabel('Date',fontsize=18)
    #plt.ylabel('Price USD ($)',fontsize=18)
    plt.legend()
    plt.show()




