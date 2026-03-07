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


def check_token():
    data = request.get_json() or request.form
    token = data.get("token")

    if not token:
        logger.warning("Check token request with no token provided")
        return jsonify({"valid": False, "message": "No token provided"}), 400

    try:
        db = get_db()
        cursor = db.cursor()
        sql = """
            SELECT user_id, expires_at
            FROM password_resets
            WHERE token = %s
            LIMIT 1
        """
        cursor.execute(sql, (token,))
        row = cursor.fetchone()

        if not row:
            logger.info(f"Token not found: {token}")
            return jsonify({"valid": False, "message": "Token not found"}), 404

        user_id, expires_at = row
        logger.info(f"Check token query result: {row}")

        # Convert expires_at to datetime if it's a string
        if isinstance(expires_at, str):
            try:
                expires_at = to_datetime(expires_at)
            except ValueError as e:
                logger.error(f"Failed to parse expires_at: {expires_at} - {e}")
                return jsonify({"valid": False, "message": "Invalid token expiry format"}), 500

        now = datetime.utcnow()
        logger.info(f"Token belongs to user_id={user_id}, expires_at={expires_at}, current_time={now}")

        if expires_at < now:
            logger.info(f"Token expired for user_id={user_id}")
            return jsonify({"valid": False, "message": "Token expired"}), 401

        return jsonify({"valid": True, "user_id": user_id}), 200

    except Exception as e:
        logger.exception(f"Error checking token: {e}")
        return jsonify({"valid": False, "message": "Server error"}), 500