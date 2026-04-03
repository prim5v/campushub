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
import os


from ...utils.db_connection import get_db

def make_badge_request(current_user_id, role, data):
    db = get_db()
    cursor = db.cursor()

    try:
        # Extract data
        property_name = data.get("property_name")
        badge_type = data.get("badge_type")

        logging.info(f"[MAKE_BADGE_REQUEST] Called by user_id={current_user_id}, role={role}, "
                     f"badge_type={badge_type}, property_name={property_name}")

        # Validate required fields
        if not all([badge_type, property_name]):
            logging.warning("[MAKE_BADGE_REQUEST] Missing required fields")
            return jsonify({"error": "Missing required fields"}), 400

        # Insert badge request into database
        cursor.execute("""
            INSERT INTO badge_requests (user_id, badge_type, property_name, requested_at)
            VALUES (%s, %s, %s, NOW())
        """, (current_user_id, badge_type, property_name))
        db.commit()

        logging.info(f"[MAKE_BADGE_REQUEST] Badge request created successfully for user_id={current_user_id}")
        return jsonify({"message": "Badge request submitted successfully"}), 201

    except Exception as e:
        logging.error(f"Error making badge request: {e}")
        return jsonify({"error": "Failed to submit badge request"}), 500