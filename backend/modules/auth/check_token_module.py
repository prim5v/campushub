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


from ...utils.db_connection import get_db

def check_token():
    data = request.get_json() or request.form
    token = data.get("token")

    if not token:
        return jsonify({"valid": False, "message": "No token provided"}), 400

    try:
        db = get_db()
        cursor = db.cursor()
        # Check token in password_resets table and that it hasn't expired
        sql = """
            SELECT user_id, expires_at
            FROM password_resets
            WHERE token = %s
            LIMIT 1
        """
        cursor.execute(sql, (token,))
        row = cursor.fetchone()

        if not row:
            return jsonify({"valid": False, "message": "Token not found"}), 404

        user_id, expires_at = row
        now = datetime.utcnow()

        if expires_at < now:
            return jsonify({"valid": False, "message": "Token expired"}), 401

        # Token is valid
        return jsonify({"valid": True, "user_id": user_id}), 200

    except Exception as e:
        # Log to Sentry
        # Sentry.captureException(e)
        return jsonify({"valid": False, "message": "Server error"}), 500