
import os
from twilio.rest import Client

os.system('google-chrome --headless --disable-gpu --screenshot --virtual-time-budget=10000 --window-size=550,2300 --hide-scrollbars http://localhost:3000/screenshot')


# Your Account Sid and Auth Token from twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
client = Client(account_sid, auth_token)

message = client.messages \
                .create(
                     body="Join Earth's mightiest heroes. Like Kevin Bacon.",
                     from_='+12513192223',
                     to='+14047888665'
                 )

print(message.sid)
