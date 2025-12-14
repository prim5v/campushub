# imports
import bcrypt
from flask import Blueprint, Flask, jsonify, g, request, current_app
import pymysql
import uuid, random, string, re
from flask_cors import CORS
import requests
from functools import wraps
import jwt
from google import genai  # ✅ correct for google-genai>=1.0.0
from datetime import datetime, date, timedelta
from requests.auth import HTTPBasicAuth
# from flask import current_app
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
from flask_mail import Mail, Message
from decimal import Decimal
from twilio.rest import Client
from google import genai  # ✅ correct for google-genai>=1.0.0
from flask import make_response
import user_agents
import hashlib
import secrets



def get_location(ip: str) -> str:
    """Resolve IP to city, region, country using ipinfo.io"""
    try:
        res = requests.get(f"https://ipinfo.io/{ip}/json", timeout=2)
        if res.status_code == 200:
            data = res.json()
            city = data.get("city")
            region = data.get("region")
            country = data.get("country")
            return ", ".join(filter(None, [city, region, country]))
    except Exception:
        pass
    return "Unknown"


def get_device_info() -> dict:
    ua_string = request.headers.get("User-Agent", "Unknown")
    user_agent = user_agents.parse(ua_string)
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)

    ua_lower = ua_string.lower()

    # Browser detection with fallback
    browser_family = user_agent.browser.family
    if browser_family in ("Other", "Unknown"):
        if "chrome" in ua_lower:
            browser_family = "Chrome"
        elif "firefox" in ua_lower:
            browser_family = "Firefox"
        elif "safari" in ua_lower:
            browser_family = "Safari"
        elif "edge" in ua_lower:
            browser_family = "Edge"
        elif "insomnia" in ua_lower:
            browser_family = "Insomnia"
        elif "postman" in ua_lower:
            browser_family = "Postman"
        else:
            browser_family = "Unknown"

    # OS detection with fallback
    os_family = user_agent.os.family
    if os_family in ("Other", "Unknown"):
        if "windows" in ua_lower:
            os_family = "Windows"
        elif "macintosh" in ua_lower or "mac os" in ua_lower:
            os_family = "MacOS"
        elif "linux" in ua_lower:
            os_family = "Linux"
        elif "android" in ua_lower:
            os_family = "Android"
        elif "iphone" in ua_lower or "ipad" in ua_lower:
            os_family = "iOS"
        elif "insomnia" in ua_lower:
            os_family = "Unknown API Client"
        elif "postman" in ua_lower:
            os_family = "Unknown API Client"
        else:
            os_family = "Unknown"

    # Device type detection with fallback
    device_family = user_agent.device.family
    if device_family in ("Other", "Unknown"):
        if "mobile" in ua_lower:
            device_family = "Mobile"
        elif "tablet" in ua_lower or "ipad" in ua_lower:
            device_family = "Tablet"
        elif "insomnia" in ua_lower or "postman" in ua_lower:
            device_family = "PC (API Client)"
        else:
            device_family = "PC"

    location = get_location(ip)

    return {
        "browser": browser_family,
        "os": os_family,
        "device": device_family,
        "ip": ip,
        "location": location
    }


# from utils.email_utils import send_security_email

def send_security_email(email, device_info, reasons):
    subject = "⚠️ Security Alert: Unusual Login Detected"

    reasons_text = "\n".join([f"• {reason}" for reason in reasons])

    message_body = f"""
    🔐 **Security Alert**

    A new login was detected on your account that appears unusual:

    🔎 **Reason(s) for alert:**
    {reasons_text}

    📱 **Login Details:**
    • Browser: {device_info['browser']}
    • Operating System: {device_info['os']}
    • IP Address: {device_info['ip']}
    • Location: {device_info['location']}

    If this was NOT you, please secure your account immediately by changing your password or contacting support.

    Stay safe,
    Your Security Team
    """

    msg = Message(subject, recipients=[email], body=message_body)

    try:
        mail.send(msg)
        print("✅ Security email sent successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False



def send_informational_email(email, device_info, reasons):
    subject = "ℹ️ Login Notice: New Device or Browser Detected"

    reasons_text = "\n".join([f"• {reason}" for reason in reasons])

    message_body = f"""
    🔔 **Login Notice**

    A new login was detected on your account. This login is slightly different from your usual activity,
    but does not appear fully suspicious.

    🔎 **Reason(s) for notification:**
    {reasons_text}

    📱 **Login Details:**
    • Browser: {device_info['browser']}
    • Operating System: {device_info['os']}
    • IP Address: {device_info['ip']}
    • Location: {device_info['location']}

    If this was you, no action is needed.
    If not, please review your account activity.

    Stay safe,
    Your Security Team
    """

    msg = Message(subject, recipients=[email], body=message_body)

    try:
        mail.send(msg)
        print("✅ Informational email sent successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False
