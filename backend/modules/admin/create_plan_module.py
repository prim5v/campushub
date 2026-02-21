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

logger = logging.getLogger(__name__)

def create_plan(data):
    try:
        logger.info("📦 Create plan request received")

        # Extract fields from payload
        name = data.get("name")
        price = data.get("price")
        period = data.get("period")
        description = data.get("description")
        features = data.get("features") or []
        not_included = data.get("not_included") or []
        popular = data.get("popular", 0)
        properties_limit = data.get("properties_limit", 1)
        listings_limit = data.get("listings_limit", 1)

        # Validation
        if not name or price is None or not period or not features or not not_included:
            logger.warning("❌ Missing required plan fields")
            return jsonify({"error": "missing required fields"}), 400

        # Normalize strings to lists if needed
        if isinstance(features, str):
            features = [f.strip() for f in features.split(",") if f.strip()]
        if isinstance(not_included, str):
            not_included = [f.strip() for f in not_included.split(",") if f.strip()]

        # Serialize to JSON for MySQL
        features_json = json.dumps(features)
        not_included_json = json.dumps(not_included)

        # Insert into database
        conn = get_db()
        cursor = conn.cursor()
        logger.info(f"🧾 Inserting plan: {name}")

        cursor.execute("""
            INSERT INTO plan_data
            (name, price, period, description, features, not_included, popular, properties_limit, listings_limit)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            name,
            price,
            period,
            description,
            features_json,
            not_included_json,
            popular,
            properties_limit,
            listings_limit
        ))

        conn.commit()
        plan_id = cursor.lastrowid
        logger.info(f"✅ Plan created successfully. ID={plan_id}, name={name}")

        return jsonify({
            "status": "success",
            "message": "Plan created successfully",
            "plan_id": plan_id
        }), 201

    except Exception as e:
        logger.exception("🔥 Failed to create plan")
        return jsonify({"error": "internal server error"}), 500