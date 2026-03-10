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


from ...utils.db_connection import get_db
from ...utils.extra_functions import send_password_reset_email

def toggle_forgot_pwd():
    data = request.get_json() or request.form
    email = data.get("email")

    if not email:
        return jsonify({"error": "Email is required"}), 400

    db = get_db()
    cursor = db.cursor()

    # 1️⃣ Check if user exists
    cursor.execute("SELECT user_id FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    if not user:
        # For security, respond the same even if email doesn't exist
        return jsonify({"message": "If this email exists, a reset link has been sent."}), 200

    user_id = user["user_id"]

    # 2️⃣ Generate secure token
    token = secrets.token_urlsafe(32)

    # 3️⃣ Set expiration (e.g., 3 minutes from now)
    expires_at = datetime.utcnow() + timedelta(minutes=3)

    # 4️⃣ Insert token into password_resets table
    cursor.execute("""
        INSERT INTO password_resets(user_id, token, expires_at)
        VALUES (%s, %s, %s)
    """, (user_id, token, expires_at))
    db.commit()

    # 5️⃣ Construct reset link
    # RESET_LINK = f"https://campushub-website.vercel.app/reset-password/{token}"
    # Updated for search params
    RESET_LINK = f"https://campushub.yreen.co.ke/reset-password?token={token}"

    # 6️⃣ Send email
    email_sent = send_password_reset_email(email, RESET_LINK)
    if email_sent:
        return jsonify({"message": "If this email exists, a reset link has been sent."}), 200
    else:
        return jsonify({"error": "Failed to send reset email"}), 500

