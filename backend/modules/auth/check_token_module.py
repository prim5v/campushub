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
        conn = get_db()

        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT user_id, expires_at
                FROM password_resets
                WHERE token = %s
                LIMIT 1
            """, (token,))

            record = cursor.fetchone()

            if not record:
                logger.info(f"Token not found: {token}")
                return jsonify({
                    "valid": False,
                    "message": "Token not found"
                }), 404

            user_id = record["user_id"]
            expires_at = record["expires_at"]

            logger.info(f"Token record: {record}")

            # Same expiry pattern used in OTP verification
            if datetime.utcnow() > expires_at:
                logger.info(f"Token expired for user_id={user_id}")
                return jsonify({
                    "valid": False,
                    "message": "Token expired"
                }), 401

            logger.info(f"Token valid for user_id={user_id}")

            return jsonify({
                "valid": True,
                "user_id": user_id
            }), 200

    except Exception as e:
        logger.exception(f"Error checking token: {e}")
        return jsonify({
            "valid": False,
            "message": "Server error"
        }), 500