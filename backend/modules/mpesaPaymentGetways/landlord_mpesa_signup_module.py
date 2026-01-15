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
import logging
import os
import base64

import requests
import json
import dotenv

dotenv.load_dotenv()

logger = logging.getLogger(__name__)


def perform_landlord_mpesa_signup(data):
    try:
        logger.info("🚀 Landlord MPESA signup started")

        user = data.get("user", {})
        plan = data.get("plan", {})
        payment = data.get("payment", {})

        email = user.get("email")
        username = user.get("username")
        password = user.get("password")
        role = user.get("role")
        plan_id = plan.get("id")
        phone = payment.get("mpesaPhone")

        logger.info(f"📥 Payload: email={email}, username={username}, plan_id={plan_id}, phone={phone}")

        # =========================
        # Validate
        # =========================
        if not all([email, username, password, role, plan_id, phone]):
            logger.warning("❌ Missing required fields")
            return jsonify({"error": "missing required fields"}), 400

        if role != "landlord":
            logger.warning("❌ Invalid role")
            return jsonify({"error": "invalid role"}), 400

        db = get_db()
        cursor = db.cursor()

        # =========================
        # Check if user already exists
        # =========================
        cursor.execute("SELECT 1 FROM users WHERE email=%s OR username=%s", (email, username))
        if cursor.fetchone():
            logger.warning("❌ User already exists")
            return jsonify({"error": "user already exists"}), 400
        

        # =========================
        # Check if plan exists
        # =========================
        cursor.execute("SELECT * FROM plan_data WHERE id=%s", (plan_id,))
        plan_row = cursor.fetchone()
        if not plan_row:
            logger.warning("❌ Invalid plan")
            return jsonify({"error": "invalid plan"}), 400

        price = float(plan_row["price"])
        if price <= 0:
            logger.warning("❌ Free plan not supported here")
            return jsonify({"error": "plan is free"}), 400

        # =========================
        # Hash password
        # =========================
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        # =========================
        # MPESA CREDENTIALS (same as your working code)
        # =========================
        consumer_key = os.getenv("MPESA_CONSUMER_KEY")
        consumer_secret = os.getenv("MPESA_CONSUMER_SECRET")
        passkey = os.getenv("MPESA_PASSKEY")
        business_short_code = os.getenv("MPESA_SHORTCODE")

        # =========================
        # Get access token
        # =========================
        auth_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        auth_response = requests.get(auth_url, auth=HTTPBasicAuth(consumer_key, consumer_secret))
        access_token = "Bearer " + auth_response.json()['access_token']

        # =========================
        # Generate password
        # =========================
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        data_to_encode = business_short_code + passkey + timestamp
        encoded_password = base64.b64encode(data_to_encode.encode()).decode('utf-8')

        # =========================
        # Build STK payload
        # =========================
        payload = {
            "BusinessShortCode": business_short_code,
            "Password": encoded_password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(price),
            "PartyA": phone,
            "PartyB": business_short_code,
            "PhoneNumber": phone,
            "CallBackURL": "https://campushub4293.pythonanywhere.com/mpesaPaymentGetways/mpesa_landlord_signup_callback",
            "AccountReference": f"SIGNUP-{email}",
            "TransactionDesc": "CompassHub Landlord Signup"
        }

        headers = {
            "Authorization": access_token,
            "Content-Type": "application/json"
        }

        logger.info(f"📡 Sending STK push to {phone} for KES {price}")
        logger.info(f"📡 Payload: {payload}")

        # =========================
        # Send STK push
        # =========================
        stk_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        response = requests.post(stk_url, json=payload, headers=headers)
        mpesa_response = response.json()

        logger.info(f"📨 MPESA response: {mpesa_response}")

        if mpesa_response.get("ResponseCode") != "0":
            logger.error("❌ STK push failed")
            return jsonify({
                "error": "STK push failed",
                "details": mpesa_response
            }), 400

        checkout_request_id = mpesa_response.get("CheckoutRequestID")

        # =========================
        # Save pending signup
        # =========================
        logger.info(f"💾 Saving pending signup for {email}")

        cursor.execute("""
            INSERT INTO pending_landlord_signups
            (email, username, password_hash, role, plan_id, checkout_request_id, status)
            VALUES (%s, %s, %s, %s, %s, %s, 'pending_payment')
            ON DUPLICATE KEY UPDATE
                checkout_request_id = VALUES(checkout_request_id),
                plan_id = VALUES(plan_id),
                status = 'pending_payment',
                created_at = NOW()
        """, (email, username, password_hash, role, plan_id, checkout_request_id))
        db.commit()


        logger.info(f"✅ Pending signup created: {email}")

        # =========================
        # Return response
        # =========================
        return jsonify({
            "status": "mpesa",
            "message": "Check your phone to complete payment",
            "checkout_request_id": checkout_request_id,
            "mpesa_response": mpesa_response
        }), 200

    except Exception as e:
        logger.exception("🔥 Landlord MPESA signup failed")
        return jsonify({"error": "internal server error"}), 500
