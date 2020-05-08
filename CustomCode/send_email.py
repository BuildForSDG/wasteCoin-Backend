from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

def send_email(subject,email_address,messageToSend):
    msg = MIMEMultipart()
    message = messageToSend
    user_id = 'Am1nuIsr2'
    msg['From'] = "aminuisrael90@gmail.com"
    msg['To'] = email_address
    msg['Subject'] = subject

    msg.attach(MIMEText(message, 'plain'))
    server = smtplib.SMTP('smtp.gmail.com: 587')
    server.starttls()
    server.login(msg['From'], user_id)
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()