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




def generate_otp():
    return str(random.randint(100000, 999999))

def perform_verify_otp(data):
    email = data.get("email")
    otp = data.get("otp")

    if not otp or not email:
        return jsonify({"error": "OTP and email are required"}), 400

    try:
        conn = get_db()
        with conn.cursor() as cursor:

            # Fetch latest OTP record
            cursor.execute("""
                SELECT * FROM EmailOTP
                WHERE email = %s
                ORDER BY created_at DESC
                LIMIT 1
            """, (email,))
            record = cursor.fetchone()

            if not record:
                return jsonify({"error": "No OTP found for this email. Please request a new one."}), 400

            # Check if user exceeded attempts
            if record["attempts"] >= 5:
                return jsonify({"error": "Too many incorrect attempts. OTP locked. Request a new OTP."}), 403

            # Check expiration
            if datetime.utcnow() > record["expires_at"]:
                return jsonify({"error": "OTP has expired"}), 400

            # Validate OTP
            if record["otp"] != otp:
                # Increment attempt count
                cursor.execute("""
                    UPDATE EmailOTP SET attempts = attempts + 1
                    WHERE email = %s
                """, (email,))
                conn.commit()

                attempts_left = 5 - (record["attempts"] + 1)
                return jsonify({
                    "error": "Incorrect OTP",
                    "attempts_left": max(attempts_left, 0)
                }), 400

            # ✅ OTP correct: create user
            role_prefixes = {"admin": "adm", "student": "stu"}
            prefix = role_prefixes.get(record["role"], "usr")
            user_id = f"{prefix}-{str(uuid.uuid4())[:8]}"

            cursor.execute("""
                INSERT INTO Users (user_id, username, email, password, role)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                user_id,
                record["username"],
                record["email"],
                record["password_hash"],
                record["role"]
            ))
            conn.commit()

            # Delete OTP record
            cursor.execute("""DELETE FROM EmailOTP WHERE email = %s""", (email,))
            conn.commit()

            # ✅ Create session immediately
            device_id = request.cookies.get("device_id")
            if not device_id:
                device_id = f"DEV-{uuid.uuid4().hex[:10].upper()}"

            session_id = str(uuid.uuid4())
            token, expiry, token_hash = generate_jwt(user_id, record["role"], device_id, session_id)

            # Fetch device info
            device_info = get_device_info()

            cursor.execute("""
                INSERT INTO sessions (
                    session_id, user_id, token, expires_at, device_id, browser, os, ip_address, location
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                session_id,
                user_id,
                token_hash,
                expiry,
                device_id,
                device_info["browser"],
                device_info["os"],
                device_info["ip"],
                device_info["location"]
            ))
            conn.commit()

            # ✅ Prepare response with cookie
            resp = make_response(jsonify({
                "status": "success",
                "message": "Email verified successfully. Account created!",
                "user": {
                    "user_id": user_id,
                    "username": record["username"],
                    "role": record["role"],
                    "email": record["email"]
                },
            }))
            resp.set_cookie(
                "device_id",
                device_id,
                max_age=365*24*60*60,  # 1 year
                httponly=True,
                secure=True,  # set to False if testing on HTTP
                samesite="None"  # allow cross-site sending,
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

    except Exception as e:
        return jsonify({"error": str(e)}), 500

