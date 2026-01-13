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
import json


from ...utils.db_connection import get_db
import logging

# Set up logging for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Log to console (works in dev)
if not logger.handlers:
    handler = logging.StreamHandler()  # logs go to console
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def get_plans():
    logger.info("get_plans called")
    db = get_db()
    cursor = db.cursor()
    try:
        logger.info("Executing SQL to fetch plans")
        sql = "SELECT * FROM plan_data ORDER BY price ASC"
        cursor.execute(sql)
        rows = cursor.fetchall()
        logger.info(f"Fetched {len(rows)} rows from plan_data")

        if not rows:
            logger.info("No plans found, returning empty list")
            return jsonify({"plans": []}), 200

        plans = []
        for row in rows:
            try:
                features = json.loads(row["features"]) if row["features"] else []
                not_included = json.loads(row["not_included"]) if row["not_included"] else []
            except Exception as parse_error:
                logger.error(f"Failed to parse JSON fields for plan {row.get('id')}: {parse_error}")
                features, not_included = [], []

            plan_obj = {
                "id": row["id"],
                "name": row["name"],
                "price": row["price"],
                "period": row["period"],
                "description": row["description"],
                "features": features,
                "notIncluded": not_included,
                "popular": bool(row["popular"])
            }
            plans.append(plan_obj)
            logger.info(f"Processed plan: {plan_obj['name']}")

        logger.info("Returning all plans successfully")
        return jsonify({"plans": plans}), 200

    except Exception as e:
        logger.error(f"Exception in get_plans: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500