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
import os
from dotenv import load_dotenv


# Load environment variables from .env
load_dotenv()

# Set the secret key from environment
current_app.config["SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")



def generate_jwt(user_id, role, device_id, session_id):
    # Set expiry based on role
    if role == "admin":
        expiry = datetime.utcnow() + timedelta(hours=2)
    elif role == "student":
        expiry = datetime.utcnow() + timedelta(hours=8)
    else:
        # Default fallback (optional)
        expiry = datetime.utcnow() + timedelta(hours=5)

    payload = {
        "user_id": user_id,
        "role": role,
        "device_id": device_id,
        "session_id": session_id,
        "exp": expiry
    }

    token = jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    return token, expiry, token_hash



def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # ✅ Get device_id from header or cookie
        device_id = request.headers.get("X-Device-ID") or request.cookies.get("device_id")
        if not device_id:
            return jsonify({"error": "Device ID header missing"}), 400

        # ✅ Get JWT from HttpOnly cookie
        token = request.cookies.get("access_token")
        if not token:
            return jsonify({"error": "Token is missing!"}), 401

        # ✅ Verify JWT
        try:
            data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            current_user = data.get("user_id")
            role = data.get("role")
            token_device_id = data.get("device_id")
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired!"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token!"}), 401

        # ✅ Device mismatch check
        if token_device_id != device_id:
            return jsonify({"error": "Token not valid for this device"}), 401

        # ✅ Hash token for DB lookup
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        # ✅ Check session in DB
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM sessions WHERE user_id=%s AND token=%s AND device_id=%s",
            (current_user, token_hash, device_id)
        )
        session = cursor.fetchone()
        if not session:
            return jsonify({"error": "Session not found or invalidated!"}), 401
        if datetime.utcnow() > session["expires_at"]:
            return jsonify({"error": "Session expired. Please login again."}), 401

        # ✅ CSRF check for unsafe HTTP methods
        if request.method in ("POST", "PUT", "PATCH", "DELETE"):
            csrf_header = request.headers.get("X-CSRF-Token")
            csrf_cookie = request.cookies.get("csrf_token")
            if not csrf_header or not csrf_cookie or csrf_header != csrf_cookie:
                return jsonify({"error": "CSRF validation failed!"}), 403

        return f(current_user, role, *args, **kwargs)

    return decorated
