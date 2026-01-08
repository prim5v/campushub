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

def fetch_overview(current_user_id, role):
    db = get_db()
    cursor = db.cursor()
    try:
        overview_sql = """
            SELECT 
                (SELECT COUNT(*) FROM tenants_data WHERE user_id = %s) AS total_tenants,
                (SELECT COUNT(*) FROM properties_data WHERE user_id = %s) AS total_properties,
                (SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE user_id = %s AND type = 'income') AS total_income,
                (SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE user_id = %s AND type = 'expense') AS total_expenses
        """

        cursor.execute(
            overview_sql,
            (
                current_user_id,
                current_user_id,
                current_user_id,
                current_user_id
            )
        )
        result = cursor.fetchone()

        total_amount = float(result[2]) - float(result[3])

        overview_data = {
            "total_tenants": result[0],
            "total_properties": result[1],
            "total_income": float(result[2]),
            "total_expenses": float(result[3]),
            "total amount" : total_amount
        }

        return jsonify(overview_data), 200

    except Exception as e:
        logging.error(f"Error fetching overview: {e}")
        return jsonify({"error": "An error occurred while fetching overview"}), 500
