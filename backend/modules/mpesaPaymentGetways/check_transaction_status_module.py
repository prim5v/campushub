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

def check_transaction_status(checkout_id):
    db = get_db()
    cursor = db.cursor()

    try:
        logger.info("🔎 Checking transaction status")

        if not checkout_id:
            return jsonify({
                "status": "error",
                "message": "checkout_request_id is required"
            }), 400

        cursor.execute("""
            SELECT 
                transaction_id,
                status,
                amount,
                mpesa_code,
                transaction_date
            FROM transactions
            WHERE checkout_request_id = %s
        """, (checkout_id,))

        row = cursor.fetchone()

        if not row:
            return jsonify({
                "status": "not_found",
                "message": "Transaction not found"
            }), 404

        status = row["status"]

        # ===============================
        # Pending
        # ===============================
        if status == "pending":
            return jsonify({
                "status": "pending",
                "message": "Payment awaiting confirmation"
            }), 200

        # ===============================
        # Completed
        # ===============================
        if status == "success":
            return jsonify({
                "status": "success",
                "message": "Payment successful",
                "transaction_id": row["transaction_id"],
                "mpesa_receipt": row["mpesa_code"],
                "amount": str(row["amount"])
            }), 200

        # ===============================
        # Failed
        # ===============================
        if status == "failed":
            return jsonify({
                "status": "failed",
                "message": "Payment failed or cancelled"
            }), 200

        # ===============================
        # Partial (future use)
        # ===============================
        if status == "partial":
            return jsonify({
                "status": "partial",
                "message": "Partial payment received"
            }), 200

        # ===============================
        # Unknown state
        # ===============================
        return jsonify({
            "status": "error",
            "message": "Unknown transaction status"
        }), 500

    except Exception:
        logger.exception("🔥 Error while checking transaction status")
        return jsonify({
            "status": "error",
            "message": "Server error"
        }), 500

    # finally:
    #     cursor.close()
    #     db.close()