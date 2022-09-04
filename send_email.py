import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import email

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
    s.login(email_from, "fffgqvyyyyfbxjxkggllmwv")
    s.sendmail(email_from, [email_to], msg.as_string())
    s.quit()
