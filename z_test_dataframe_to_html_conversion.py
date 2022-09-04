import pandas as pd
import smtplib
import email
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(email_body, email_subject, attachment=None):
       #msg = email.message_from_string(", ".join(email_body))
       msg = MIMEMultipart("alternative")
       msg['From'] = 'mesudhir@gmail.com'
       msg['To'] = 'mesudhir@gmail.com'
       msg['Subject'] = email_subject

       if type(email_body) == list:
              message_body = ' '.join(email_body)
       else:
              message_body = email_body

       msg.attach(message_body, "text")

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


df = pd.DataFrame

df1 = {'ticker': 'AAAA',
       'Close': 22,
       'SMA_7': 22,
       'SMA_20': 22,
       'SMA_50': 22,
       'SMA_200': 22
       }

df = df.append(df1, ignore_index = True)

email_body = 'This is test'


email_attachment = df.to_html()

send_email(email_body, 'z_test_dataframe_to_html', email_attachment)

print(df)