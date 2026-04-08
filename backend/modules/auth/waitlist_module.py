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
from ...utils.jwt_setup import generate_jwt
from ...utils.extra_functions import get_device_info
import bcrypt, uuid
from datetime import datetime, timedelta

from ...utils.email_setup import mail
from ...utils.extra_functions import send_welcome_email


def normalize_phone(phone):
    phone = phone.strip().replace(" ", "")
    if phone.startswith("07"):
        return "+254" + phone[1:]
    elif phone.startswith("7"):
        return "+254" + phone
    elif phone.startswith("+254"):
        return phone
    return phone


def waitlist_signup(data):
    full_name = data.get("full_name", "")
    phone = data.get("phone", "")
    campus = data.get("campus", "")
    budget = data.get("budget", "")
    move_in = data.get("preferred_move_in_date", "")
    location = data.get("preferred_location", "")

    # REQUIRED VALIDATION
    if not phone or not campus:
        return jsonify({"error": "Phone and campus are required"}), 400

    phone = normalize_phone(phone)

    # Budget validation
    try:
        budget = int(budget) if budget else None
    except:
        return jsonify({"error": "Invalid budget"}), 400

    try:
        conn = get_db()
        with conn.cursor() as cursor:

            # Check duplicate by phone
            cursor.execute("SELECT id FROM waitlist WHERE phone = %s", (phone,))
            if cursor.fetchone():
                return jsonify({"message": "Already registered"}), 200

            # Insert
            cursor.execute("""
                INSERT INTO waitlist 
                (full_name, phone, campus, budget, preferred_move_in_date, preferred_location) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (full_name, phone, campus, budget, move_in, location))

            conn.commit()

        return jsonify({"message": "Successfully added"}), 201

    except Exception as e:
        logging.error(f"Waitlist error: {e}")
        return jsonify({"error": "Internal server error"}), 500