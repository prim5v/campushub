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
import logging

from ...utils.db_connection import get_db
from ...utils.extra_functions import to_datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("password_reset")

def toggle_reset_pwd():
    data = request.get_json() or request.form
    token = data.get("token")
    new_password = data.get("password")

    if not token or not new_password:
        logger.warning(
            f"Password reset request missing token or password. "
            f"Token: {token}, Password length: {len(new_password) if new_password else 0}"
        )
        return jsonify({"success": False, "message": "Token and password required"}), 400

    try:
        db = get_db()
        with db.cursor() as cursor:

            # 1️⃣ Get token record
            cursor.execute("""
                SELECT user_id, expires_at
                FROM password_resets
                WHERE token = %s
                LIMIT 1
            """, (token,))

            record = cursor.fetchone()
            if not record:
                logger.info(f"Password reset token not found: {token}")
                return jsonify({"success": False, "message": "Invalid token"}), 404

            user_id = record["user_id"]
            expires_at = record["expires_at"]

            logger.info(f"Token record: {record}")

            # 2️⃣ Check expiry using OTP-style logic
            if datetime.utcnow() > expires_at:
                logger.info(f"Token expired for user_id={user_id}")
                return jsonify({"success": False, "message": "Token expired"}), 401

            # 3️⃣ Hash password
            hashed_password = bcrypt.hashpw(
                new_password.encode("utf-8"),
                bcrypt.gensalt()
            )

            # 4️⃣ Update password
            cursor.execute(
                "UPDATE users SET password_hash = %s WHERE user_id = %s",
                (hashed_password, user_id)
            )

            # 5️⃣ Delete used token immediately
            cursor.execute(
                "DELETE FROM password_resets WHERE token = %s",
                (token,)
            )

            db.commit()

            logger.info(f"Password reset successful for user_id={user_id}")

            return jsonify({
                "success": True,
                "message": "Password reset successfully"
            }), 200

    except Exception as e:
        db.rollback()
        logger.exception(f"Error during password reset: {e}")
        return jsonify({
            "success": False,
            "message": "Server error"
        }), 500