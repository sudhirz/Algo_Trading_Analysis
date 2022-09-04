import requests
from bs4 import BeautifulSoup
import yfinance as yf
import email
import smtplib
import string
import pandas as pd

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
EMA_screened_list = [] # will have final result if all condition matches


def send_email(screened_list, message):
  msg = email.message_from_string(", ".join(screened_list))
  msg['From'] = 'mesudhir@gmail.com'
  msg['To'] = 'mesudhir@gmail.com'
  msg['Subject'] = message

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


#Create a function to scrape the data
def scrape_stock_symbols(Letter):
  Letter =  Letter.upper()
  URL =  'https://www.advfn.com/nyse/newyorkstockexchange.asp?companies='+Letter
  page = requests.get(URL)
  soup = BeautifulSoup(page.text, "html.parser")
  odd_rows = soup.find_all('tr', attrs= {'class':'ts0'})
  even_rows = soup.find_all('tr', attrs= {'class':'ts1'})
  for i in odd_rows:
    row = i.find_all('td')
    company_name.append(row[0].text.strip())
    company_ticker.append(row[1].text.strip())
  for i in even_rows:
    row = i.find_all('td')
    company_name.append(row[0].text.strip())
    company_ticker.append(row[1].text.strip())
  return company_name, company_ticker


def get_stock_price(code):
  # you can change the start date
  data = yf.download(code, start="2021-01-01")
  return data

def add_EMA(price, day):
  return price.ewm(span=day).mean()

def add_STOCH(close, low, high, period, k, d=0):
    STOCH_K = ((close - low.rolling(window=period).min()) / (high.rolling(window=period).max() - low.rolling(window=period).min())) * 100
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
          candle1['Low'] > candle1 ['EMA50']
  return cond1 and cond2 and cond3


# # a list to store the screened results
# screened_list = []
# # get the full stock list
# ticker_file = open(r"C:\Users\sudhi\Documents\Algorithmic_Trading\NYSE.txt","r")
# ticker_list = []
# for item in ticker_file:
#     ticker = item.split()[0]
#     ticker_list.append(ticker)
string.ascii_uppercase

#Loop through every letter in the alphabet to get all of the tickers from the website
for char in string.ascii_uppercase:
  (temp_name,temp_ticker) = scrape_stock_symbols(char)



for stock_code in company_ticker:

  print(stock_code) # remove this if you dont want the ticker to be printed
  try:
    # Step 1: get stock price for each stock
    price_chart_df = get_stock_price(stock_code)

    # Step 2: add technical indicators (in this case EMA)
    #close = price_chart_df['Close']
    #low = price_chart_df['Low']
    #open = price_chart_df['Open']
    #high = price_chart_df['High']
    price_chart_df['EMA18'] = add_EMA(price_chart_df['Close'],18)
    price_chart_df['EMA50'] = add_EMA(price_chart_df['Close'],50)
    price_chart_df['EMA100'] = add_EMA(price_chart_df['Close'],100)
    price_chart_df['STOCH_%K(5,3,3)'] = add_STOCH(price_chart_df['Close'], price_chart_df['Low'], price_chart_df['High'], 5, 3)
    price_chart_df['STOCH_%D(5,3,3)'] = add_STOCH(price_chart_df['Close'], price_chart_df['Low'], price_chart_df['High'], 5, 3, 3)

    # if all 3 conditions are met, add stock into screened list
    if check_bounce_EMA(price_chart_df):
      EMA_screened_list.append(stock_code)
      print(EMA_screened_list)
  except Exception as e:
    print(e)

# you can add this part of code at the end of part 2
# remember: screened_list contains the result of the screening
# configure email and message

send_email(EMA_screened_list, 'EMA_Screened_Today')
