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
import math

from flask import render_template

from .email_setup import mail

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
    device_brand_info = get_device_brand(ua_string)
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
        "device_brand": device_brand_info["brand"],
        "device_model": device_brand_info["model"],
        "ip": ip,
        "location": location
    }




# from utils.email_utils import send_security_email

def send_security_email(email, device_info, reasons):

    html = render_template(
        "emails/security_alert.html",
        device=device_info,
        reasons=reasons
    )

    msg = Message(
        subject="⚠️ Security Alert: Unusual Login Detected",
        recipients=[email],
        html=html
    )

    try:
        mail.send(msg)
        print("✅ Security email sent successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False



def generate_otp():
    return str(random.randint(100000, 999999))

def send_informational_email(email, device_info, reasons):
    html = render_template(
        "emails/security_alert.html",
        device=device_info,
        reasons=reasons
    )

    msg = Message(
        subject="ℹ️ Login Notice: New Device or Browser Detected",
        recipients=[email],
        html=html
    )

    try:
        mail.send(msg)
        print("✅ Informational email sent successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False


def get_device_brand(ua_string: str) -> dict:
    ua = ua_string.lower()

    # --- Mobile brands ---
    if "iphone" in ua:
        return {"brand": "Apple", "model": "iPhone"}
    if "ipad" in ua:
        return {"brand": "Apple", "model": "iPad"}
    if "samsung" in ua:
        return {"brand": "Samsung", "model": "Android"}
    if "tecno" in ua:
        return {"brand": "Tecno", "model": "Android"}
    if "infinix" in ua:
        return {"brand": "Infinix", "model": "Android"}
    if "itel" in ua:
        return {"brand": "Itel", "model": "Android"}
    if "redmi" in ua or "xiaomi" in ua:
        return {"brand": "Xiaomi", "model": "Android"}
    if "huawei" in ua:
        return {"brand": "Huawei", "model": "Android"}
    if "oppo" in ua:
        return {"brand": "Oppo", "model": "Android"}
    if "vivo" in ua:
        return {"brand": "Vivo", "model": "Android"}

    # --- Laptops / PCs ---
    if "dell" in ua:
        return {"brand": "Dell", "model": "PC"}
    if "asus" in ua:
        return {"brand": "ASUS", "model": "PC"}
    if "hp" in ua or "hewlett-packard" in ua:
        return {"brand": "HP", "model": "PC"}
    if "lenovo" in ua:
        return {"brand": "Lenovo", "model": "PC"}
    if "acer" in ua:
        return {"brand": "Acer", "model": "PC"}
    if "macintosh" in ua or "mac os" in ua:
        return {"brand": "Apple", "model": "Mac"}

    # --- API Clients ---
    if "postman" in ua:
        return {"brand": "Postman", "model": "API Client"}
    if "insomnia" in ua:
        return {"brand": "Insomnia", "model": "API Client"}

    return {"brand": "Unknown", "model": "Unknown"}


def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Returns distance in METERS between two coordinates.
    """
    R = 6371000  # Earth radius in meters

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2) ** 2 +
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return int(R * c)  # return meters (integer)


def safe_iso(dt, fallback="Immediately"):
    if not dt or str(dt).startswith("0000"):
        return fallback
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt)
        except:
            return fallback
    return dt.isoformat()
