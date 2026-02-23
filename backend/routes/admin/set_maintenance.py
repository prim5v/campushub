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


from . import admin
from ...utils.limiter import limiter
from ...utils.db_connection import get_db



admin.route("/set_system_maintenance", methods=["PUT", "POST"])
@limiter.limit("10 per minute")
def set_maintenance():
    """
    Inserts or updates system maintenance status.
    JSON body: { "is_active": true/false, "message": "Optional message" }
    """
    data = request.get_json()
    if not data or "is_active" not in data:
        return jsonify({"error": "Missing 'is_active' field"}), 400

    is_active = 1 if data["is_active"] else 0
    message = data.get("message", "The system is currently under maintenance. Please check back later.")

    db = get_db()
    try:
        with db.cursor() as cursor:
            # Check if a row exists
            cursor.execute("SELECT id FROM system_maintenance LIMIT 1")
            row = cursor.fetchone()

            if row:
                # Update existing
                cursor.execute("""
                    UPDATE system_maintenance
                    SET is_active = %s, message = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (is_active, message, row['id']))
            else:
                # Insert first row
                cursor.execute("""
                    INSERT INTO system_maintenance (is_active, message)
                    VALUES (%s, %s)
                """, (is_active, message))
            db.commit()

        return jsonify({"success": True, "is_active": is_active, "message": message})
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500