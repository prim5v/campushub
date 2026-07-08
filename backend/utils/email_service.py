import os
import logging

from flask import render_template

logger = logging.getLogger(__name__)

EMAIL_PROVIDER = os.getenv("EMAIL_PROVIDER", "gmail").lower()

# ------------------------
# Gmail imports
# ------------------------
from flask_mail import Message
from .email_setup import mail

# ------------------------
# Brevo imports
# ------------------------
from sib_api_v3_sdk import (
    Configuration,
    ApiClient,
    TransactionalEmailsApi,
    SendSmtpEmail
)

configuration = Configuration()
configuration.api_key["api-key"] = os.getenv("BREVO_API_KEY")

brevo_api = TransactionalEmailsApi(ApiClient(configuration))


def send_email(to, subject, template, **context):
    """
    Generic email sender.

    Example:
        send_email(
            to=email,
            subject="Verify",
            template="emails/otp_verification.html",
            username=username,
            otp=otp
        )
    """

    html = render_template(template, **context)

    if EMAIL_PROVIDER == "gmail":
        return send_gmail_email(to, subject, html)

    elif EMAIL_PROVIDER == "brevo":
        return send_brevo_email(to, subject, html)

    else:
        raise Exception(f"Unknown email provider: {EMAIL_PROVIDER}")


def send_gmail_email(to, subject, html):

    msg = Message(
        subject=subject,
        recipients=[to]
    )

    msg.html = html

    mail.send(msg)

    logger.info(f"Gmail email sent to {to}")

    return True


def send_brevo_email(to, subject, html):

    email = SendSmtpEmail(

        sender={
            "name": os.getenv("BREVO_SENDER_NAME"),
            "email": os.getenv("BREVO_SENDER_EMAIL")
        },

        to=[
            {
                "email": to
            }
        ],

        subject=subject,

        html_content=html

    )

    brevo_api.send_transac_email(email)

    logger.info(f"Brevo email sent to {to}")

    return True