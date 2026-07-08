import os
import logging

from flask import render_template

logger = logging.getLogger(__name__)

Email_PROVIDER = os.getenv("EMAIL_PROVIDER", "gmail").lower()

from flask_mail import Mail, Message
from .email_setup import mail

from sib_api_v3_sdk import (ApiClient, Configuration, TransactionalEmailsApi, SendSmtpEmail, SendSmtpEmailTo)

configuration = Configuration()
configuration.api_key['api-key'] = os.getenv("BREVO_API_KEY")

brevo_api = TransactionalEmailsApi(ApiClient(configuration))

def send_email(to, subject, template, **context):

    html = render_template(template, **context)
    if Email_PROVIDER == "gmail":
        return send_gmail_email(to, subject, html)
    elif Email_PROVIDER == "brevo":
        return send_brevo_email(to, subject, html)
    else:
        raise Exception(f"Email provider {Email_PROVIDER} is not supported.")

def send_gmail_email(to, subject, html):
    msg =Message(subject=subject, recipients=[to])
    msg.html = html
    mail.send(msg)
    logger.info(f"Email sent to {to} via Gmail with subject: {subject}")
    return True

def send_brevo_email(to, subject, html):
    email = SendSmtpEmail(

         sender ={
             "name": os.getenv("BREVO_SENDER_NAME"),
             "email": os.getenv("BREVO_SENDER_EMAIL")
         },
         to=[
             {
                 "email": to,
                 "name": to.split("@")[0]
             }
         ],
         subject=subject,
         html_content=html
    )
    # brevo_api.send_transational_email(email)
    brevo_api.send_transac_email(email)
    logger.info(f"Email sent to {to} via Brevo with subject: {subject}")
    return True


    # possible function call
    # from ...utils.email_service import send_email

    # send_email(
    #     to=email,
    #     subject="Verify Your Email Address",
    #     template="emails/otp_verification.html",
    #     username=username,
    #     otp=otp
    # )

    # username && otp fall in **context, which is passed to the render_template function to populate the email template with dynamic content.
