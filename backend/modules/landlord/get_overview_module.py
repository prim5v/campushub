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
import logging

def fetch_overview(current_user_id, role, *args, **kwargs):
    logging.info(f"[OVERVIEW] Fetching overview for user_id={current_user_id}, role={role}")

    try:
        db = get_db()
        logging.info("[OVERVIEW] Database connection acquired")

        # IMPORTANT: Use DictCursor
        cursor = db.cursor(pymysql.cursors.DictCursor)
        logging.info("[OVERVIEW] Cursor created (DictCursor)")

        overview_sql = """
            SELECT 
                (SELECT COUNT(*) FROM tenants_data WHERE user_id = %s) AS total_tenants,
                (SELECT COUNT(*) FROM properties_data WHERE user_id = %s) AS total_properties,
                (SELECT COUNT(*) FROM listings_data WHERE user_id = %s) AS total_listings,
                (SELECT COALESCE(SUM(amount), 0) 
                 FROM transactions 
                 WHERE user_id = %s AND transaction_type = 'income') AS total_income,
                (SELECT COALESCE(SUM(amount), 0) 
                 FROM transactions 
                 WHERE user_id = %s AND transaction_type = 'expense') AS total_expenses
        """

        params = (
            current_user_id,
            current_user_id,
            current_user_id,
            current_user_id,
            current_user_id
        )

        logging.info(f"[OVERVIEW] Executing SQL with params: {params}")

        cursor.execute(overview_sql, params)

        result = cursor.fetchone()

        logging.info(f"[OVERVIEW] Raw SQL result: {result}")

        if not result:
            logging.warning("[OVERVIEW] Query returned no results")
            return jsonify({"error": "No data found"}), 404

        # Safely convert Decimals / None
        total_income = float(result["total_income"] or 0)
        total_expenses = float(result["total_expenses"] or 0)

        total_amount = total_income - total_expenses

        overview_data = {
            "total_tenants": int(result["total_tenants"]),
            "total_properties": int(result["total_properties"]),
            "total_listings": int(result["total_listings"]),
            "total_income": total_income,
            "total_expenses": total_expenses,
            "total_amount": total_amount
        }

        logging.info(f"[OVERVIEW] Computed overview data: {overview_data}")

        return jsonify(overview_data), 200

    except Exception as e:
        logging.exception("[OVERVIEW] CRITICAL ERROR while fetching overview")
        return jsonify({"error": "An error occurred while fetching overview"}), 500
