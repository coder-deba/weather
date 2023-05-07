import smtplib

from cs50 import SQL
from datetime import datetime
import ssl
import schedule
import time

from helpers import weather
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///weather.db")

def subscribed():
    subs = db.execute('SELECT * FROM subscribers')
    print("it's good")
    for i in range(len(subs)):
        city = subs[i]["place"]
        wet = weather(city)[2]
        print(wet)
        send_email(subs[i]["username"], wet, subs[i]["email"], city)

def send_email(username, wet, mail, place):
    # me == my email address
    # you == recipient's email address
    email_sender = 'info.weathernet02@gmail.com'
    email_password = 'vymvfrjphuejlkdo'
    email_receiver = mail

    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Link"
    msg['From'] = email_sender
    msg['To'] = email_receiver
    print(wet["icon"])

    # Create the body of the message (a plain-text and an HTML version).
    text = "Hi!\nHow are you?\nHere is the link you wanted:\nhttp://www.python.org"
    html = """\
    <html>
      <head></head>
      <body>
        <p>Hi """ +str(username)+ """<br>
          Good morning:)<br>
          Here is the weather report for """ +str(place)+ """.
        </p>
        <img src=""" +str(wet["icon"])+ """>
        <table>
          <tbody>
            <tr>
              <th>Description</th>
              <td>""" +str(wet["desc"])+ """<td>
            </tr>
            <tr>
              <th>Max. Temperature</th>
              <td>""" +str(wet["max_temp"])+ " &#176;C"+ """<td>
            </tr>
            <tr>
              <th>Min. Temperature</th>
              <td>""" +str(wet["min_temp"])+ " &#176;C"+ """<td>
            </tr>
            <tr>
                <th>Wind speed</th>
                <td>""" +str(wet["max_wind"])+" kmph"+ """<td>
            </tr>
            <tr>
                <th>Humidity</th>
                <td>""" +str(wet["avg_humidity"])+" %"+ """<td>
            </tr>
            <tr>
                <th>Chances of Precipitation</th>
                <td>""" +str(wet["precip_chance"])+" %"+ """<td>
            </tr>
          </tbody>
        </table>
      </body>
    </html>
    """

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)
    # Send the message via local SMTP server.
    context = ssl.create_default_context()

    try:
      with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
          smtp.login(email_sender, email_password)
          smtp.sendmail(email_sender, email_receiver, msg.as_string())
          print('Message sent at', datetime.now())
    except Exception as e:
        print('Error:', e)
    # finally:
    #     smtp.quit()
        

# Schedule the message to be sent every day at 9 AM
schedule.every().day.at("11:18").do(subscribed)

while True:
  schedule.run_pending()
  time.sleep(1)    

