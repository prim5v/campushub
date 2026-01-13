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



def handle_mpesa_landlord_signup_callback(data):
    try:
        logger.info("📞 MPESA CALLBACK RECEIVED")

        # data = request.get_json(force=True)
        logger.info(f"📩 CALLBACK RAW DATA: {json.dumps(data)}")

        stk = data.get("Body", {}).get("stkCallback", {})

        result_code = stk.get("ResultCode")
        result_desc = stk.get("ResultDesc")
        checkout_request_id = stk.get("CheckoutRequestID")

        logger.info(f"📦 ResultCode={result_code}, CheckoutRequestID={checkout_request_id}")

        # ===============================
        # If payment failed
        # ===============================
        if result_code != 0:
            logger.warning(f"❌ Payment failed: {result_desc}")

            db = get_db()
            cursor = db.cursor()

            cursor.execute("""
                UPDATE pending_landlord_signups
                SET status='failed'
                WHERE checkout_request_id=%s
            """, (checkout_request_id,))
            db.commit()

            return jsonify({"ResultCode": 0, "ResultDesc": "Handled"}), 200

        # ===============================
        # Payment successful → extract metadata
        # ===============================
        metadata_items = stk.get("CallbackMetadata", {}).get("Item", [])

        amount = None
        mpesa_receipt = None
        phone = None

        for item in metadata_items:
            name = item.get("Name")
            if name == "Amount":
                amount = item.get("Value")
            elif name == "MpesaReceiptNumber":
                mpesa_receipt = item.get("Value")
            elif name == "PhoneNumber":
                phone = item.get("Value")

        logger.info(f"💰 Payment success: amount={amount}, receipt={mpesa_receipt}, phone={phone}")

        db = get_db()
        cursor = db.cursor()

        # ===============================
        # 🔥 CHECK IF THIS IS A LANDLORD SIGNUP PAYMENT
        # ===============================
        cursor.execute("""
            SELECT *
            FROM pending_landlord_signups
            WHERE checkout_request_id = %s
        """, (checkout_request_id,))
        pending = cursor.fetchone()

        if pending:
            logger.info(f"🎯 Payment belongs to pending signup: {pending['email']}")

            # Generate OTP
            otp = generate_otp()
            expires_at = datetime.utcnow() + timedelta(minutes=5)

            # Remove old OTP
            cursor.execute("DELETE FROM email_otp WHERE email = %s", (pending["email"],))

            # Insert into email_otp
            cursor.execute("""
                INSERT INTO email_otp
                (email, username, password_hash, role, otp_code, expires_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                pending["email"],
                pending["username"],
                pending["password_hash"],
                pending["role"],
                otp,
                expires_at
            ))

            # Mark pending as paid
            cursor.execute("""
                UPDATE pending_landlord_signups
                SET status='paid'
                WHERE id=%s
            """, (pending["id"],))

            db.commit()

            # Send OTP email
            msg = Message("Verify Your Email", recipients=[pending["email"]])
            msg.body = f"""Hello {pending['username']},

Your verification code is: {otp}

This code expires in 5 minutes.

— CompassHub
"""
            mail.send(msg)

            logger.info(f"📧 OTP sent to {pending['email']} after payment")

            # IMPORTANT: Respond to Safaricom
            return jsonify({"ResultCode": 0, "ResultDesc": "Success"}), 200

        # ===============================
        # Otherwise → normal payment (future orders)
        # ===============================
        logger.info("ℹ️ Payment is not a signup payment. Ignoring for now.")

        return jsonify({"ResultCode": 0, "ResultDesc": "Success"}), 200

    except Exception as e:
        logger.exception("🔥 CALLBACK CRASHED")

        # Must still return 200 to Safaricom
        return jsonify({"ResultCode": 0, "ResultDesc": "Error handled"}), 200