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

from ...utils.email_setup import mail   
from ...utils.db_connection import get_db
from ...utils.jwt_setup import generate_jwt
import bcrypt, uuid
from datetime import datetime, timedelta
from ...utils.extra_functions import (generate_otp, send_security_email, send_informational_email, get_device_info)



def perform_signup(data):
    """Handle new user registration via OTP"""
    email = data.get("email")
    password = data.get("password")
    username = data.get("username")
    role = data.get("role")

    ALLOWED_ROLES = {"comrade", "landlord", "e_service"}
    if role not in ALLOWED_ROLES:
        return jsonify({"error": "server error"}), 400

    if not email or not password or not username or not role:
        return jsonify({"error": "server error"}), 400

    conn = get_db()
    cursor = conn.cursor()

    # check if username already exists
    cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
    if cursor.fetchone():
        return jsonify({"error": "server error"}), 400

    # Check if user already exists
    cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
    if cursor.fetchone():
        return jsonify({"error": "server error"}), 400

    # Generate OTP
    otp = generate_otp()
    expires_at = datetime.utcnow() + timedelta(minutes=5)
    # username = email.split("@")[0]
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    # Remove previous OTP if any
    cursor.execute("DELETE FROM email_otp WHERE email = %s", (email,))
    conn.commit()

    # Insert new OTP record
    cursor.execute("""
        INSERT INTO email_otp (email, username, password_hash, role, otp_code, expires_at)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (email, username, password_hash, role, otp, expires_at))
    conn.commit()

    # Send OTP email
    try:
        msg = Message("Verify Your Email", recipients=[email])
        msg.body = f"Hello {username},\n\nYour verification code is: {otp}\nThis code expires in 5 minutes."
        mail.send(msg)
    except Exception as e:
        return jsonify({"error": "Server error", "details": str(e)}), 500

    return jsonify({
        "status": "verify_otp",
        "message": "OTP sent to your email",
        "email": email
    }), 200
