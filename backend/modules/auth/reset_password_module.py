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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("password_reset")

def toggle_reset_pwd():
    data = request.get_json() or request.form
    token = data.get("token")
    new_password = data.get("password")

    if not token or not new_password:
        logger.warning(f"Password reset request missing token or password. Token: {token}, Password length: {len(new_password) if new_password else 0}")
        return jsonify({"success": False, "message": "Token and password required"}), 400

    try:
        db = get_db()
        cursor = db.cursor()

        # 1️⃣ Verify token exists and is not expired
        sql_token = """
            SELECT user_id, expires_at
            FROM password_resets
            WHERE token = %s
            LIMIT 1
        """
        cursor.execute(sql_token, (token,))
        row = cursor.fetchone()

        if not row:
            logger.info(f"Password reset token not found: {token}")
            return jsonify({"success": False, "message": "Invalid token"}), 404

        user_id, expires_at = row
        logger.info(f"Token query result: {row}")

        # Convert expires_at to datetime if it's a string
        if isinstance(expires_at, str):
            try:
                expires_at = datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S")
            except ValueError as e:
                logger.error(f"Failed to parse expires_at: {expires_at} - {e}")
                return jsonify({"success": False, "message": "Invalid token expiry format"}), 500

        now = datetime.utcnow()
        logger.info(f"Token belongs to user_id={user_id}, expires_at={expires_at}, current_time={now}")

        if expires_at < now:
            logger.info(f"Token expired for user_id={user_id}")
            return jsonify({"success": False, "message": "Token expired"}), 401

        # 2️⃣ Hash new password
        hashed_password = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt())

        # 3️⃣ Update password_hash in users table
        sql_update = "UPDATE users SET password_hash = %s WHERE user_id = %s"
        cursor.execute(sql_update, (hashed_password, user_id))

        # 4️⃣ Delete token to prevent reuse
        sql_delete = "DELETE FROM password_resets WHERE token = %s"
        cursor.execute(sql_delete, (token,))

        db.commit()
        logger.info(f"Password reset successfully for user_id={user_id}")

        return jsonify({"success": True, "message": "Password reset successfully"}), 200

    except Exception as e:
        db.rollback()
        logger.exception(f"Error during password reset: {e}")
        return jsonify({"success": False, "message": "Server error"}), 500