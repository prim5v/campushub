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

# ================= RATE LIMITER SETUP =================
def user_or_ip():
    """
    Identify the requestor for rate limiting.
    Uses user_id from JWT cookie if available, otherwise client IP.
    """
    token = request.cookies.get("access_token")  # Get token from cookie

    if token:
        try:
            decoded = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            return decoded.get("user_id", get_remote_address())
        except Exception:
            pass

    return get_remote_address()



limiter = Limiter(
    key_func=user_or_ip,
    app=app,
    default_limits=["200 per day", "50 per hour"],  # Global defaults
)

@app.errorhandler(429)
def ratelimit_error(e):
    return jsonify({
        "error": "Too many requests — slow down.",
        "details": str(e.description)
    }), 429
# ======================================================
