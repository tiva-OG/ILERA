from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from twilio.rest import Client
from datetime import date


class SMSClient:
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN
    sender_number = settings.TWILIO_SENDER_NUMBER

    @classmethod
    def send_sms(cls, phone, message):
        client = Client(cls.account_sid, cls.auth_token)
        message = client.messages.create(from_=cls.sender_number, body=message, to=phone)
        return message


class EmailClient:
    subject = "Your ILERA OTP Code"
    from_email = settings.DEFAULT_FROM_EMAIL

    @classmethod
    def send_email(cls, receiver, code):
        to_email = [receiver]
        context = {"code": code, "year": date.today().year}

        html_content = render_to_string("otp/email_otp.html", context)
        text_content = "This email contains information from ILERA. Please view in an HTML-compatible client."

        email = EmailMultiAlternatives(cls.subject, text_content, cls.from_email, to_email)
        email.attach_alternative(html_content, "text/html")
        email.send()

        return email
