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


logger = logging.getLogger(__name__)

def check_landlord_payment_status(checkoutId):
    db = get_db()
    cursor = db.cursor()

    try:
        logger.info("🔎 Checking landlord payment status")

        checkout_request_id = checkoutId

        if not checkout_request_id:
            logger.warning("⚠️ No checkout_request_id provided")
            return jsonify({
                "status": "error",
                "message": "checkout_request_id is required"
            }), 400

        logger.info(f"📦 Checking payment for: {checkout_request_id}")

        cursor.execute("""
            SELECT status, email, username, plan_id, created_at
            FROM pending_landlord_signups
            WHERE checkout_request_id = %s
        """, (checkout_request_id,))

        row = cursor.fetchone()

        if not row:
            logger.warning("❌ No pending signup found for this checkout_request_id")
            return jsonify({
                "status": "not_found",
                "message": "No signup found for this payment"
            }), 404

        status = row["status"]

        logger.info(f"📊 Current payment status: {status}")

        # ===============================
        # Still waiting for payment
        # ===============================
        if status == "pending_payment":
            return jsonify({
                "status": "pending_payment",
                "message": "Waiting for payment confirmation"
            }), 200

        # ===============================
        # Payment completed
        # ===============================
        if status == "paid":
            return jsonify({
                "status": "paid",
                "message": "Payment confirmed. OTP sent to email.",
                "email": row["email"]
            }), 200

        # ===============================
        # Payment failed
        # ===============================
        if status == "failed":
            return jsonify({
                "status": "failed",
                "message": "Payment failed or was cancelled"
            }), 200

        # ===============================
        # Unknown status
        # ===============================
        logger.warning(f"⚠️ Unknown status in DB: {status}")

        return jsonify({
            "status": "error",
            "message": "Unknown payment status"
        }), 500

    except Exception:
        logger.exception("🔥 Error while checking landlord payment status")
        return jsonify({
            "status": "error",
            "message": "Server error"
        }), 500
