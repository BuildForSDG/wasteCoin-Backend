from twilio.rest import Client
# account_sid = "AC7227807a67f5af6f2ca7c66595c1ca6f"
# auth_token = "a30830b7c5f8b7be61677882c17141f9"

account_sid = ""
auth_token = ""
verification = Client(account_sid,auth_token)
twilio_number = "+12025191283"


def sendsms(phone,message):
    verification.messages.create(from_=twilio_number, to=f"+234{phone}",body=message)