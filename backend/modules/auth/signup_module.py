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
from flask import render_template

from ...utils.email_setup import mail   
from ...utils.db_connection import get_db
from ...utils.jwt_setup import generate_jwt
import bcrypt, uuid
from datetime import datetime, timedelta
from ...utils.extra_functions import (generate_otp, send_security_email, send_informational_email, get_device_info)


import logging
# from datetime import datetime, timedelta
# import bcrypt
# from flask import jsonify
# from flask_mail import Message

logger = logging.getLogger(__name__)

def perform_signup(data):
    """Handle new user registration via OTP"""

    try:
        logger.info("🚀 Signup request received")

        email = data.get("email")
        password = data.get("password")
        username = data.get("username")
        role = data.get("role")

        logger.info(f"📥 Payload received: email={email}, username={username}, role={role}")

        ALLOWED_ROLES = {"comrade", "landlord", "e_service"}

        # ==============================
        # Validate input
        # ==============================
        if role not in ALLOWED_ROLES:
            logger.warning(f"❌ Invalid role attempted: {role}")
            return jsonify({"error": "invalid role"}), 400

        if not email or not password or not username or not role:
            logger.warning("❌ Missing required fields in signup payload")
            return jsonify({"error": "missing required fields"}), 400

        conn = get_db()
        cursor = conn.cursor()
        logger.info("✅ Database connection opened")

        # ==============================
        # Check username
        # ==============================
        logger.info(f"🔎 Checking if username exists: {username}")
        cursor.execute("SELECT 1 FROM users WHERE username=%s", (username,))
        if cursor.fetchone():
            logger.warning(f"❌ Username already exists: {username}")
            return jsonify({"error": "username already exists"}), 400

        # ==============================
        # Check email
        # ==============================
        logger.info(f"🔎 Checking if email exists: {email}")
        cursor.execute("SELECT 1 FROM users WHERE email=%s", (email,))
        if cursor.fetchone():
            logger.warning(f"❌ Email already exists: {email}")
            return jsonify({"error": "email already exists"}), 400

        # ==============================
        # Generate OTP
        # ==============================
        otp = generate_otp()
        expires_at = datetime.utcnow() + timedelta(minutes=5)
        logger.info(f"🔐 OTP generated for {email}, expires at {expires_at}")

        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        logger.info("🔒 Password hashed")

        # ==============================
        # Remove old OTP
        # ==============================
        logger.info(f"🧹 Removing old OTP records for {email}")
        cursor.execute("DELETE FROM email_otp WHERE email = %s", (email,))
        conn.commit()

        # ==============================
        # Insert new OTP
        # ==============================
        logger.info(f"💾 Inserting new OTP record for {email}")
        cursor.execute("""
            INSERT INTO email_otp (email, username, password_hash, role, otp_code, expires_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (email, username, password_hash, role, otp, expires_at))
        conn.commit()

        # ==============================
        # Send Email
        # ==============================
        logger.info(f"📧 Sending OTP email to {email}")
        try:
            msg = Message("Verify Your Email", recipients=[email])
#             msg.body = f"""Hello {username},

# Your verification code is: {otp}

# This code expires in 5 minutes.

# — CompassHub
# """
            msg.html = render_template(
    "emails/otp_verification.html",
    username=username,
    otp=otp
)

            mail.send(msg)
            logger.info(f"✅ OTP email sent successfully to {email}")

        except Exception as e:
            logger.exception("❌ Failed to send OTP email")
            return jsonify({"error": "failed to send email"}), 500

        # ==============================
        # Success
        # ==============================
        logger.info(f"🎉 Signup OTP flow started successfully for {email}")

        return jsonify({
            "status": "verify_otp",
            "message": "OTP sent to your email",
            "email": email
        }), 200

    except Exception as e:
        logger.exception("🔥 CRITICAL ERROR during signup process")
        return jsonify({"error": "internal server error"}), 500
