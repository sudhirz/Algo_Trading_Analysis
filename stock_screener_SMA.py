import pandas as pd
import datetime
import yfinance as yf
import smtplib
import email
from datetime import datetime

import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

df = pd.DataFrame()
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

#Create a function to scrape the data
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
  msg['From'] = 'xxxxxxx@gmail.com'
  msg['To'] = 'xxxxxxx@gmail.com'
  msg['Subject'] = email_subject

  if attachment != None:
    part2 = MIMEText(attachment, "html")
    msg.attach(part2)

  email_from = 'xxxxxxx@gmail.com'
  email_to = 'xxxxxxx@gmail.com'
  s = smtplib.SMTP("smtp.gmail.com", 587)
  ## for yahoo mail user: s = smtplib.SMTP("smtp.mail.yahoo.com",587)
  ## for hotmail user: s = smtplib.SMTP("smtp.live.com",587)
  s.ehlo()
  s.starttls()
  s.ehlo()
  s.login(email_from, "fffgqvyyyfbxjxkggllmwv")
  s.sendmail(email_from, [email_to], msg.as_string())
  s.quit()


def get_stock_price(code):
  # you can change the start date
  start_date = datetime.datetime.now() - datetime.timedelta(days=365) # one year ago
  data = yf.download(code, start=start_date)
  return data

def SMA_screener(close, days):
  return close.rolling(window=days).mean()

def percent_change(close):
    return close.pct_change()

#string.ascii_uppercase

#Loop through every letter in the alphabet to get all of the tickers from the website
# for char in string.ascii_uppercase:
#   (temp_name,temp_ticker) = scrape_stock_symbols(char)
start_time = datetime.now()
ticker_file = open(r"NYSE.txt","r")
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

    price_chart_df['SMA_7'] = SMA_screener(close, 7)
    price_chart_df['SMA_20'] = SMA_screener(close, 20)
    price_chart_df['SMA_50'] = SMA_screener(close, 50)
    price_chart_df['SMA_200'] = SMA_screener(close, 200)
    price_chart_df['percent_change'] = percent_change(close)

    if price_chart_df['percent_change'].iloc[-1] > 0 \
        and price_chart_df['Close'].iloc[-1] > price_chart_df['SMA_7'].iloc[-1] \
        and price_chart_df['SMA_7'].iloc[-1] > price_chart_df['SMA_20'].iloc[-1]\
        and price_chart_df['SMA_20'].iloc[-1] > price_chart_df['SMA_50'].iloc[-1]\
        and price_chart_df['SMA_50'].iloc[-1] > price_chart_df['SMA_200'].iloc[-1]:
      SMA_screened_list.append(stock_code)
      standard_deviation = price_chart_df['Close'].std()
      df1 = {'ticker':stock_code,
             'Close': price_chart_df['Close'].iloc[-1],
             'SMA_7': price_chart_df['SMA_7'].iloc[-1],
             'SMA_20': price_chart_df['SMA_20'].iloc[-1],
             'SMA_50': price_chart_df['SMA_50'].iloc[-1],
             'SMA_200': price_chart_df['SMA_200'].iloc[-1],
             'STD': standard_deviation,
             }
      df = df.append(df1, ignore_index = True)


  except Exception as e:
    print(e)

df['SMA_7_PCT_CHG'] = df['SMA_7'].pct_change(periods=1)

# sort top 10 with least variance at the top


df = df.sort_values(by='SMA_7_PCT_CHG', ascending=False)

#print(SMA_screened_list)
#print(df.head(10))

text = 'Attached is the CSV file'
email_df = df.to_html()

#send_email(SMA_screened_list, 'SMA_Screener_today')
send_email(text, 'SMA_Screener_table_today', attachment=email_df)

end_time = datetime.now()
print('start time - {} \n  end time - {}' .format(start_time, end_time))
