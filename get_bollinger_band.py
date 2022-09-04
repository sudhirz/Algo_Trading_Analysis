def get_bollinger_band(adj_close):
    # Calculate 30 Day Moving Average, Std Deviation, Upper Band and Lower Band

    ma_30_days = adj_close.rolling(window=20).mean()

    # set .std(ddof=0) for population std instead of sample
    std_30_days = adj_close.rolling(window=20).std()

    upper_band = ma_30_days + (std_30_days * 2)
    lower_band = ma_30_days - (std_30_days * 2)

    return ma_30_days, upper_band, lower_band