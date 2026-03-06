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


def check_token():
    data = request.get_json() or request.form
    token = data.get("token")

    logger.info(f"Received check token request. Token: {token}")

    if not token:
        logger.warning("No token provided in request")
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
        logger.info(f"Check token query result: {row}")

        if not row:
            logger.warning("Token not found")
            return jsonify({"valid": False, "message": "Token not found"}), 404

        user_id, expires_at = row
        now = datetime.utcnow()
        logger.info(f"Token belongs to user_id={user_id}, expires_at={expires_at}, current_time={now}")

        if expires_at < now:
            logger.warning("Token expired")
            return jsonify({"valid": False, "message": "Token expired"}), 401

        logger.info("Token is valid")
        return jsonify({"valid": True, "user_id": user_id}), 200

    except Exception as e:
        logger.error(f"Error checking token: {e}", exc_info=True)
        return jsonify({"valid": False, "message": "Server error"}), 500