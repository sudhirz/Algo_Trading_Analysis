import pandas as pd
import datetime
import yfinance as yf
import email

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

df_SMA = pd.DataFrame()
df_EMA = pd.DataFrame()
df_ADX = pd.DataFrame()
df_RSI = pd.DataFrame()

# def get_stock_list():
#   # this is the website we're going to scrape from
#   url = "https://www.malaysiastock.biz/Stock-Screener.aspx"
#   response = requests.get(url, headers={'User-Agent':'test'})
#   soup = BeautifulSoup(response.content, "html.parser")
#   table = soup.find(id = "MainContent2_tbAllStock")
#   # return the result (only ticker code) in a list
#   return [stock_code.get('href')[-4:] for stock_code in table.find_all('a')]

company_name = []
company_ticker = []
SMA_screened_list = []
EMA_screened_list = []


# Create a function to scrape the data
# def scrape_stock_symbols(Letter):
#   Letter =  Letter.upper()
#   URL =  'https://www.advfn.com/nyse/newyorkstockexchange.asp?companies='+Letter
#   page = requests.get(URL)
#   soup = BeautifulSoup(page.text, "html.parser")
#   odd_rows = soup.find_all('tr', attrs= {'class':'ts0'})
#   even_rows = soup.find_all('tr', attrs= {'class':'ts1'})
#   for i in odd_rows:
#     row = i.find_all('td')
#     company_name.append(row[0].text.strip())
#     company_ticker.append(row[1].text.strip())
#   for i in even_rows:
#     row = i.find_all('td')
#     company_name.append(row[0].text.strip())
#     company_ticker.append(row[1].text.strip())
#   return company_name, company_ticker


def send_email(email_message, email_subject, attachment=None):
    msg = email.message_from_string(", ".join(email_message))
    msg = MIMEMultipart("alternative")
    msg['From'] = 'mesudhir@gmail.com'
    msg['To'] = 'mesudhir@gmail.com'
    msg['Subject'] = email_subject

    if attachment != None:
        part2 = MIMEText(attachment, "html")
        msg.attach(part2)

    email_from = 'mesudhir@gmail.com'
    email_to = 'mesudhir@gmail.com'
    s = smtplib.SMTP("smtp.gmail.com", 587)
    ## for yahoo mail user: s = smtplib.SMTP("smtp.mail.yahoo.com",587)
    ## for hotmail user: s = smtplib.SMTP("smtp.live.com",587)
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login(email_from, "gqvfbxjxkggllmwv")
    s.sendmail(email_from, [email_to], msg.as_string())
    s.quit()


def get_stock_price(code):
    # you can change the start date
    start_date = datetime.datetime.now() - datetime.timedelta(days=365)  # one year ago
    data = yf.download(code, start=start_date)
    return data


def SMA_screener(close, days):
    return close.rolling(window=days).mean()


def percent_change(close):
    return close.pct_change()


def add_EMA(price, day):
    return price.ewm(span=day).mean()


def add_STOCH(close, low, high, period, k, d=0):
    STOCH_K = ((close - low.rolling(window=period).min()) / (
            high.rolling(window=period).max() - low.rolling(window=period).min())) * 100
    STOCH_K = STOCH_K.rolling(window=k).mean()
    if d == 0:
        return STOCH_K
    else:
        STOCH_D = STOCH_K.rolling(window=d).mean()
        return STOCH_D


def check_bounce_EMA(df):
    candle1 = df.iloc[-1]
    candle2 = df.iloc[-2]
    cond1 = candle1['EMA18'] > candle1['EMA50'] > candle1['EMA100']
    cond2 = candle1['STOCH_%K(5,3,3)'] <= 30 or candle1['STOCH_%D(5,3,3)'] <= 30
    cond3 = candle2['Low'] < candle2['EMA50'] and \
            candle2['Close'] > candle2['EMA50'] and \
            candle1['Low'] > candle1['EMA50']
    return cond1 and cond2 and cond3


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


# Calculate the On Balance Volume
def calc_OBV(close, volume):
    OBV = []
    OBV.append(0)
    for i in range(1, len(close)):
        if close[i] > close[i - 1]:  # If the closing price is above the prior close price
            OBV.append(OBV[-1] + volume[i])  # then: Current OBV = Previous OBV + Current Volume
        elif close[i] < close[i - 1]:
            OBV.append(OBV[-1] - volume[i])
        else:
            OBV.append(OBV[-1])
    return OBV


# Calculate OBV EMA
def calc_obv_ema(obv):
    # Store the OBV and OBV EMA into new columns
    return obv.ewm(com=20).mean()


# string.ascii_uppercase

# Loop through every letter in the alphabet to get all of the tickers from the website
# for char in string.ascii_uppercase:
#   (temp_name,temp_ticker) = scrape_stock_symbols(char)
start_time = datetime.datetime.now()
ticker_file = open(r"C:\Users\sudhi\Documents\Algorithmic_Trading\NYSE.txt", "r")
ticker_list = []
for item in ticker_file:
    ticker = item.split()[0]
    ticker_list.append(ticker)

for stock_code in ticker_list:
    try:
        # Step 1: get stock price for each stock
        price_chart_df = get_stock_price(stock_code)

        close = price_chart_df['Close']
        low = price_chart_df['Low']
        open = price_chart_df['Open']
        high = price_chart_df['High']
        volume = price_chart_df['Volume']

        price_chart_df['SMA_7'] = SMA_screener(close, 7)
        price_chart_df['SMA_7_PCT_CHG'] = price_chart_df['SMA_7'].pct_change()
        price_chart_df['SMA_20'] = SMA_screener(close, 20)
        price_chart_df['SMA_50'] = SMA_screener(close, 50)
        price_chart_df['SMA_200'] = SMA_screener(close, 200)
        price_chart_df['percent_change'] = percent_change(close)

        if price_chart_df['percent_change'].iloc[-1] > 0 \
                and price_chart_df['SMA_7_PCT_CHG'].iloc[-1] > 0 \
                and price_chart_df['Close'].iloc[-1] > price_chart_df['SMA_7'].iloc[-1] \
                and price_chart_df['SMA_7'].iloc[-1] > price_chart_df['SMA_20'].iloc[-1] \
                and price_chart_df['SMA_20'].iloc[-1] > price_chart_df['SMA_50'].iloc[-1] \
                and price_chart_df['SMA_50'].iloc[-1] > price_chart_df['SMA_200'].iloc[-1]:
            SMA_screened_list.append(stock_code)
            price_chart_df['EMA18'] = add_EMA(close, 18)
            price_chart_df['EMA50'] = add_EMA(close, 50)
            price_chart_df['EMA100'] = add_EMA(close, 100)
            price_chart_df['STOCH_%K(5,3,3)'] = add_STOCH(close, low,
                                                          high, 5, 3)
            price_chart_df['STOCH_%D(5,3,3)'] = add_STOCH(close, low,
                                                          high, 5, 3, 3)

            # calculate standard deviation
            standard_deviation = close.std()

            price_chart_df['OBV'] = calc_OBV(close, volume)
            price_chart_df['OBV_EMA'] = calc_obv_ema(price_chart_df['OBV'])

            # Calculate ADX
            price_chart_df['plus_di'] = pd.DataFrame(
                get_adx(high, low, close, 14)[0]).rename(
                columns={0: 'plus_di'})
            price_chart_df['minus_di'] = pd.DataFrame(
                get_adx(high, low, close, 14)[1]).rename(
                columns={0: 'minus_di'})
            price_chart_df['adx'] = pd.DataFrame(
                get_adx(high, low, close, 14)[2]).rename(
                columns={0: 'adx'})

            # Calculate RSI
            price_chart_df['rsi_14'] = get_rsi(close, 14)

            if price_chart_df['adx'].iloc[-1] >= 40:
                df1_ADX = {'ticker': stock_code,
                           'Close': price_chart_df['Close'].iloc[-1],
                           'SMA_7': price_chart_df['SMA_7'].iloc[-1],
                           'SMA_7_PCT_CHG': price_chart_df['SMA_7_PCT_CHG'].iloc[-1],
                           'SMA_20': price_chart_df['SMA_20'].iloc[-1],
                           'SMA_50': price_chart_df['SMA_50'].iloc[-1],
                           'SMA_200': price_chart_df['SMA_200'].iloc[-1],
                           'STD': standard_deviation,
                           'EMA18': price_chart_df['EMA18'].iloc[-1],
                           'EMA50': price_chart_df['EMA50'].iloc[-1],
                           'EMA100': price_chart_df['EMA100'].iloc[-1],
                           'STOCH_%K(5,3,3)': price_chart_df['STOCH_%K(5,3,3)'].iloc[-1],
                           'STOCH_%D(5,3,3)': price_chart_df['STOCH_%D(5,3,3)'].iloc[-1],
                           'RSI_14': price_chart_df['rsi_14'].iloc[-1],
                           'ADX_plus_di': price_chart_df['plus_di'].iloc[-1],
                           'ADX': price_chart_df['adx'].iloc[-1],
                           'ADX_minus_di': price_chart_df['minus_di'].iloc[-1],
                           'OBV': price_chart_df['OBV'].iloc[-1],
                           'OBV_EMA': price_chart_df['OBV_EMA'].iloc[-1],
                           }
                df_ADX = df_ADX.append(df1_ADX, ignore_index=True)

            if price_chart_df['rsi_14'].iloc[-1] <= 35:
                df1_RSI = {'ticker': stock_code,
                           'Close': price_chart_df['Close'].iloc[-1],
                           'SMA_7': price_chart_df['SMA_7'].iloc[-1],
                           'SMA_7_PCT_CHG': price_chart_df['SMA_7_PCT_CHG'].iloc[-1],
                           'SMA_20': price_chart_df['SMA_20'].iloc[-1],
                           'SMA_50': price_chart_df['SMA_50'].iloc[-1],
                           'SMA_200': price_chart_df['SMA_200'].iloc[-1],
                           'STD': standard_deviation,
                           'EMA18': price_chart_df['EMA18'].iloc[-1],
                           'EMA50': price_chart_df['EMA50'].iloc[-1],
                           'EMA100': price_chart_df['EMA100'].iloc[-1],
                           'STOCH_%K(5,3,3)': price_chart_df['STOCH_%K(5,3,3)'].iloc[-1],
                           'STOCH_%D(5,3,3)': price_chart_df['STOCH_%D(5,3,3)'].iloc[-1],
                           'RSI_14': price_chart_df['rsi_14'].iloc[-1],
                           'ADX_plus_di': price_chart_df['plus_di'].iloc[-1],
                           'ADX': price_chart_df['adx'].iloc[-1],
                           'ADX_minus_di': price_chart_df['minus_di'].iloc[-1],
                           'OBV': price_chart_df['OBV'].iloc[-1],
                           'OBV_EMA': price_chart_df['OBV_EMA'].iloc[-1],
                           }
                df_RSI = df_RSI.append(df1_RSI, ignore_index=True)

            df1_SMA = {'ticker': stock_code,
                       'Close': price_chart_df['Close'].iloc[-1],
                       'SMA_7': price_chart_df['SMA_7'].iloc[-1],
                       'SMA_7_PCT_CHG': price_chart_df['SMA_7_PCT_CHG'].iloc[-1],
                       'SMA_20': price_chart_df['SMA_20'].iloc[-1],
                       'SMA_50': price_chart_df['SMA_50'].iloc[-1],
                       'SMA_200': price_chart_df['SMA_200'].iloc[-1],
                       'STD': standard_deviation,
                       'EMA18': price_chart_df['EMA18'].iloc[-1],
                       'EMA50': price_chart_df['EMA50'].iloc[-1],
                       'EMA100': price_chart_df['EMA100'].iloc[-1],
                       'STOCH_%K(5,3,3)': price_chart_df['STOCH_%K(5,3,3)'].iloc[-1],
                       'STOCH_%D(5,3,3)': price_chart_df['STOCH_%D(5,3,3)'].iloc[-1],
                       'RSI_14': price_chart_df['rsi_14'].iloc[-1],
                       'ADX_plus_di': price_chart_df['plus_di'].iloc[-1],
                       'ADX': price_chart_df['adx'].iloc[-1],
                       'ADX_minus_di': price_chart_df['minus_di'].iloc[-1],
                       'OBV': price_chart_df['OBV'].iloc[-1],
                       'OBV_EMA': price_chart_df['OBV_EMA'].iloc[-1],
                       }
            df_SMA = df_SMA.append(df1_SMA, ignore_index=True)

            # if all 3 conditions are met, add stock into screened list
            if check_bounce_EMA(price_chart_df):
                EMA_screened_list.append(stock_code)
                print(EMA_screened_list)

                df1_EMA = {'ticker': stock_code,
                           'Close': price_chart_df['Close'].iloc[-1],
                           'SMA_7': price_chart_df['SMA_7'].iloc[-1],
                           'SMA_7_PCT_CHG': price_chart_df['SMA_7_PCT_CHG'].iloc[-1],
                           'SMA_20': price_chart_df['SMA_20'].iloc[-1],
                           'SMA_50': price_chart_df['SMA_50'].iloc[-1],
                           'SMA_200': price_chart_df['SMA_200'].iloc[-1],
                           'STD': standard_deviation,
                           'EMA18': price_chart_df['EMA18'].iloc[-1],
                           'EMA50': price_chart_df['EMA50'].iloc[-1],
                           'EMA100': price_chart_df['EMA100'].iloc[-1],
                           'STOCH_%K(5,3,3)': price_chart_df['STOCH_%K(5,3,3)'].iloc[-1],
                           'STOCH_%D(5,3,3)': price_chart_df['STOCH_%D(5,3,3)'].iloc[-1],
                           'RSI_14': price_chart_df['rsi_14'].iloc[-1],
                           'ADX_plus_di': price_chart_df['plus_di'].iloc[-1],
                           'ADX': price_chart_df['adx'].iloc[-1],
                           'ADX_minus_di': price_chart_df['minus_di'].iloc[-1],
                           'OBV': price_chart_df['OBV'].iloc[-1],
                           'OBV_EMA': price_chart_df['OBV_EMA'].iloc[-1],
                           }
                df_EMA = df_EMA.append(df1_EMA, ignore_index=True)


    except Exception as e:
        print(e)

# sort top 10 with least variance at the top
if 'RSI_14' in df_SMA:
    df_SMA = df_SMA.sort_values(by=['RSI_14'])
if 'RSI_14' in df_EMA:
    df_EMA = df_EMA.sort_values(by=['RSI_14'])

if 'adx' in df_ADX:
    df_ADX = df_ADX.sort_values(by=['adx'], ascending=False)

if 'rsi' in df_RSI:
    df_RSI = df_RSI.sort_values(by=['rsi'], ascending=True)

text = 'Attached is the CSV file'
email_df_SMA = df_SMA.to_html()
email_df_EMA = df_EMA.to_html()
email_df_ADX = df_ADX.to_html()
email_df_RSI = df_RSI.to_html()

# send_email(SMA_screened_list, 'SMA_Screener_today')
send_email(text, 'SMA_Screener_table_today', attachment=email_df_SMA)
send_email(text, 'EMA_Screener_table_today', attachment=email_df_EMA)
send_email(text, 'ADX >= 40', attachment=email_df_ADX)
send_email(text, 'RSI <= 35', attachment=email_df_RSI)

end_time = datetime.datetime.now()
print('start time - {} \n  end time - {}'.format(start_time, end_time))
