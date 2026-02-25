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




def perform_get_otp(data):
    try:
        email = data.get("email")
        username = data.get("username")
        password_hash = data.get("password_hash")
        role = data.get("role")

        if not all([email, username, password_hash, role]):
            return jsonify({"error": "fields required"}), 400

        conn = get_db()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        # Delete existing OTP row for email
        cursor.execute("SELECT * FROM email_otp WHERE email=%s", (email,))
        if cursor.fetchone():
            cursor.execute("DELETE FROM email_otp WHERE email=%s", (email,))
            conn.commit()

        # Validate user credentials
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()
        if not user:
            return jsonify({"error": "user not found"}), 404
        if password_hash != user["password_hash"]:
            return jsonify({"error": "invalid credentials"}), 401

        # Generate OTP
        otp = generate_otp()
        expires_at = datetime.utcnow() + timedelta(minutes=1)

        cursor.execute("""
            INSERT INTO email_otp (email, username, password_hash, role, otp_code, expires_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (email, username, password_hash, role, otp, expires_at))
        conn.commit()

        logging.info(f"Generated OTP {otp} for {email}, expires at {expires_at}")
        return jsonify({"code": otp})

    except Exception as e:
        logging.exception("Exception in perform_get_otp")
        return jsonify({"error": "internal server error"}), 500



