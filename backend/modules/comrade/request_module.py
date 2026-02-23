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

def make_request(current_user_id, role, *args, **kwargs):
    data = request.get_json() or request.form

    listing_id = data.get("listing_id")
    phone_number = data.get("phone_number")
    full_name = data.get("full_name")

    if not listing_id or not phone_number or not full_name:
        return jsonify({"error": "All fields are required"}), 400

    request_id = f"REQ-{uuid.uuid4().hex[:12].upper()}"

    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO requests (request_id, listing_id, user_id, phone_number, full_name)
            VALUES (%s, %s, %s, %s, %s)
        """, (request_id, listing_id, current_user_id, phone_number, full_name))

        conn.commit()

        return jsonify({
            "message": "Request submitted successfully",
            "request_id": request_id
        }), 201

    except Exception as e:
        conn.rollback()
        return jsonify({"error": "Failed to submit request"}), 500

    # finally:
    #     cursor.close()
    #     conn.close()