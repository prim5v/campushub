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


# from ...utils.db_connection import get_db

# import logging


# logger = logging.getLogger(__name__)


import json
import logging
from flask import jsonify
from ...utils.db_connection import get_db
from ...utils.paymentGateways import trigger_mpesa_stk

logger = logging.getLogger(__name__)


def get_requests_and_bookings():
    try:
        db = get_db()
        cursor = db.cursor()

        # -------------------------
        # Fetch requests
        # -------------------------
        cursor.execute("SELECT * FROM requests ORDER BY requested_at DESC")
        requests_rows = cursor.fetchall()

        # -------------------------
        # Fetch bookings
        # -------------------------
        cursor.execute("SELECT * FROM bookings ORDER BY booked_at DESC")
        bookings_rows = cursor.fetchall()

        cursor.close()
        db.close()

        # -------------------------
        # Return JSON
        # -------------------------
        return jsonify({
            "status": "success",
            "data": {
                "requests": requests_rows,
                "bookings": bookings_rows
            }
        }), 200

    except Exception as e:
        logger.exception("🔥 Failed to fetch requests/bookings")
        return jsonify({
            "status": "error",
            "message": "Could not fetch data"
        }), 500