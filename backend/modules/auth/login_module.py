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


from utils.db_connection import get_db
from utils.jwt_setup import generate_jwt
from utils.extra_functions import get_device_info
import bcrypt, uuid
from datetime import datetime, timedelta
from utils.extra_functions import generate_otp, send_security_email, send_informational_email


def perform_login(data): 
    email = data.get("email")
    password = data.get("password")
    role = data.get("role")  

    #restrict roles 
    ALLOWED_ROLES = {"comrade", "landlord", "e_service"}

    if role not in ALLOWED_ROLES:
        return jsonify({"error": "credentials error"}), 400


    # ✅ Step 1: Validate input
    if not email or not password:
        return jsonify({"error": "credentials required"}), 400

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Users WHERE email=%s", (email,))
    user = cursor.fetchone()

    # ✅ New user -> OTP flow
    if not user and role is not None:
        otp = generate_otp()
        expires_at = datetime.utcnow() + timedelta(minutes=5)
        username = email.split("@")[0]
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        cursor.execute("DELETE FROM EmailOTP WHERE email = %s", (email,))
        conn.commit()


        cursor.execute("""
            INSERT INTO EmailOTP (email, username, password_hash, role, otp, expires_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            email,
            username,
            password_hash,
            role,
            otp,
            expires_at
        ))
        conn.commit()

        try:
            msg = Message("Verify Your Email", recipients=[email])
            msg.body = f"Hello {username},\n\nYour verification code is: {otp}\nThis code expires in 5 minutes."
            mail.send(msg)
        except Exception as e:
            return jsonify({"error": "server error", "details": str(e)}), 500

        return jsonify({
            "status": "verify_otp",
            "message": "OTP sent to your email",
            "email": email
        }), 200

    # ✅ Existing user -> verify password
    if not bcrypt.checkpw(password.encode(), user["password"].encode()):
        return jsonify({"error": "Invalid credentials"}), 401

    # ✅ Generate or reuse device_id from cookie
    device_id = request.cookies.get("device_id")
    if not device_id:
        device_id = f"DEV-{uuid.uuid4().hex[:10].upper()}"

    session_id = str(uuid.uuid4())
    token, expiry, token_hash = generate_jwt(user["user_id"], user["role"], device_id, session_id)


    # hash the token
    # token_hash = hashlib.sha256(token.encode()).hexdigest()

    # ✅ Fetch device info
    device_info = get_device_info()

    # ✅ Insert session with device tracking
    cursor.execute("""
        INSERT INTO sessions (
            session_id, user_id, token, expires_at, device_id, browser, os, ip_address, location
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        session_id,
        user["user_id"],
        token_hash,
        expiry,
        device_id,
        device_info["browser"],
        device_info["os"],
        device_info["ip"],
        device_info["location"]
    ))
    conn.commit()

        # ✅ Step: Determine the user's primary (most used) device
        # ✅ Fetch most frequent (trusted) device
    cursor.execute("""
        SELECT device_id, COUNT(*) as usage_count
        FROM sessions
        WHERE user_id = %s
        GROUP BY device_id
        ORDER BY usage_count DESC
        LIMIT 1
    """, (user["user_id"],))
    primary_device = cursor.fetchone()

    # ✅ Fetch last session data
    cursor.execute("""
        SELECT device_id, ip_address, location, browser, os
        FROM sessions
        WHERE user_id = %s
        ORDER BY created_at DESC
        LIMIT 1
    """, (user["user_id"],))
    last_session = cursor.fetchone()

    # ✅ Calculate Trust Score
    trust_score = 0
    reasons = []

    # IP Check
    if last_session and last_session["ip_address"] == device_info["ip"]:
        trust_score += 40
    else:
        trust_score -= 50
        reasons.append("New IP address detected")

    # Location Check
    if last_session and last_session["location"] == device_info["location"]:
        trust_score += 30
    else:
        trust_score -= 30
        reasons.append("Login from a different location")

    # Device Check
    if primary_device and primary_device["device_id"] == device_id:
        trust_score += 20
    else:
        trust_score -= 20
        reasons.append("Unfamiliar device detected")

    # Browser Check
    if last_session and last_session["browser"] == device_info["browser"]:
        trust_score += 10
    else:
        trust_score -= 10
        reasons.append("Browser differs from previous login")

    # ✅ SECURITY ACTION BASED ON TRUST SCORE
    if trust_score < 50:
        send_security_email(user["email"], device_info, reasons)  # 🚨 High-risk
    elif trust_score < 80:
        send_informational_email(user["email"], device_info, reasons)  # ⚠ Medium-risk (just notify)
    # else:
    #   No alert - trusted ✅


    # ✅ Set cookie for device_id
    resp = make_response(jsonify({
        "status": "success",
        "user": {
            "user_id": user["user_id"],
            "username": user["username"],
            "role": user["role"],
            "email": user["email"]
        },
    }))
    resp.set_cookie(
        "device_id",
        device_id,
        max_age=365*24*60*60,  # 1 year
        httponly=True,
        secure=True,  # set to False if testing on HTTP
        samesite="None",  # allow cross-site sending
        path="/"
    )

    resp.set_cookie(
        "access_token",
        token,
        max_age=int((expiry - datetime.utcnow()).total_seconds()),
        httponly=True,
        secure=True,
        samesite="None",
        path="/"
    )

    csrf_token = secrets.token_hex(32)

    resp.set_cookie(
        "csrf_token",
        csrf_token,
        httponly=False,   # MUST be readable by JS
        secure=True,
        samesite="None",
        path="/"
    )

    return resp