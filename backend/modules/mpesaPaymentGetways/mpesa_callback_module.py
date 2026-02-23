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



def handle_mpesa_transaction_callback(data):
    try:
        logger.info("📞 MPESA TRANSACTION CALLBACK RECEIVED")
        logger.info(f"📩 RAW DATA: {json.dumps(data)}")

        stk = data.get("Body", {}).get("stkCallback", {})

        result_code = stk.get("ResultCode")
        result_desc = stk.get("ResultDesc")
        checkout_request_id = stk.get("CheckoutRequestID")

        logger.info(f"ResultCode={result_code}, CheckoutRequestID={checkout_request_id}")

        db = get_db()
        cursor = db.cursor()

        # ===============================
        # Payment Failed
        # ===============================
        if result_code != 0:
            logger.warning(f"❌ Payment failed: {result_desc}")

            cursor.execute("""
                UPDATE transactions
                SET status = 'failed'
                WHERE checkout_request_id = %s
            """, (checkout_request_id,))
            db.commit()

            return jsonify({"ResultCode": 0, "ResultDesc": "Handled"}), 200

        # ===============================
        # Payment Successful
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

        logger.info(f"💰 SUCCESS amount={amount}, receipt={mpesa_receipt}, phone={phone}")

        # Verify transaction exists
        cursor.execute("""
            SELECT id, status
            FROM transactions
            WHERE checkout_request_id = %s
        """, (checkout_request_id,))
        transaction = cursor.fetchone()

        if not transaction:
            logger.warning("⚠️ No matching transaction found")
            return jsonify({"ResultCode": 0, "ResultDesc": "No transaction"}), 200

        # Prevent double processing
        if transaction["status"] == "completed":
            logger.info("ℹ️ Transaction already completed")
            return jsonify({"ResultCode": 0, "ResultDesc": "Already processed"}), 200

        # Update transaction
        cursor.execute("""
            UPDATE transactions
            SET
                status = 'success',
                mpesa_code = %s,
                amount = %s
            WHERE checkout_request_id = %s
        """, (
            mpesa_receipt,
            amount,
            checkout_request_id
        ))

        db.commit()

        logger.info("✅ Transaction marked completed")

        return jsonify({"ResultCode": 0, "ResultDesc": "Success"}), 200

    except Exception:
        logger.exception("🔥 CALLBACK ERROR")

        # Always return 200 to Safaricom
        return jsonify({"ResultCode": 0, "ResultDesc": "Error handled"}), 200