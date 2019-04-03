import sendgrid
import re
import os
from sendgrid.helpers.mail import *
from django.core.exceptions import ValidationError

def dispatch_email(user_email, subject, message):
    """
    This method handles the sending of mails to users
    """
    sg = sendgrid.SendGridAPIClient(apikey=os.getenv("SENDGRID_API_KEY"))
    from_email = Email(email=os.getenv("FROM_EMAIL"))
    to_email = Email(email=user_email)
    subject = subject
    content = Content("text/plain", message)

    try:
        mail = Mail(from_email, subject, to_email, content)
        response = sg.client.mail.send.post(request_body=mail.get())
        if response.status_code is not 202:
            return "check sender email and API key settings"
        return "Email sent to {}".format(user_email)
    except Exception:
        return "Error while sending mail to provided account"

def check_password(password):
    """
    check passwords to ensure they contain letters and numbers only
    """
    if not re.match('^[a-zA-Z0-9]+$', password):
        raise ValidationError('The password has to contain letters and numbers')
    