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

def perform_manual_create_account():
    data = request.get_json() or request.form

    email = data.get("email")
    phone_number = data.get("phone_number")
    consent_manual = data.get("consent_manual")
    consent_email_valid = data.get("consent_email_valid")

    if not email or not phone_number:
        return jsonify({"error": "email and phone_number required"}), 400

    if consent_manual is None or consent_email_valid is None:
        return jsonify({"error": "consents required"}), 400

    try:
        db = get_db()

        with db.cursor() as cursor:
            cursor.execute("""
                UPDATE email_otp
                SET consent_manual = %s,
                    consent_email_valid = %s,
                    phone_number = %s
                WHERE email = %s
            """, (consent_manual, consent_email_valid, phone_number, email))

        db.commit()

        if cursor.rowcount == 0:
            return jsonify({
                "success": False,
                "message": "No signup record found for this email"
            }), 404

        logger.info(f"Manual consent updated for {email}")

        return jsonify({
            "success": True,
            "message": "Manual account request recorded"
        }), 200

    except Exception as e:
        db.rollback()
        logger.exception(f"Error during user manual create account request: {e}")
        return jsonify({
            "success": False,
            "message": "Server error"
        }), 500