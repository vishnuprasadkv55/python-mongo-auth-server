from mailjet_rest import Client
import os
api_key = os.environ.get('MAILJET_KEY')
api_secret = os.environ.get('MAILJET_SECRET')
mailjet = Client(auth=(api_key, api_secret), version='v3.1')


def send_mail(mail_data):
    data = {
        'Messages': [
            {
                "From": {
                    "Email": "ouzkqwlbzmlirhm@trythe.net",
                    "Name": "Panic"
                },
                "To": [
                    {
                        "Email": mail_data["email"],
                        "Name": mail_data["username"]
                    }
                ],
                "Subject": "Greetings from Panic.",
                "TextPart": "Verification Code",
                "HTMLPart": "<h3>Hello " + mail_data["username"] + ", Here is your verification code: " + mail_data["verification_code"]  + "</h3><br />May the delivery force be with you!",
                "CustomID": "AppGettingStartedTest"
            }
        ]
    }
    result = mailjet.send.create(data=data)
    print('mail send to' + mail_data["email"])
