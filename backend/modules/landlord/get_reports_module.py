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

def fetch_reports(current_user_id, role):
    db = get_db()
    cursor = db.cursor()

    try:
        # 1️⃣ Fetch reports
        fetch_reports_sql = """
            SELECT *
            FROM reports
            WHERE user_id = %s
        """
        cursor.execute(fetch_reports_sql, (current_user_id,))
        reports = cursor.fetchall()

        return jsonify({"reports": reports}), 200

    except Exception as e:
        print(f"[ERROR] Exception occurred: {e}")
        return jsonify({"error": "Internal server error"}), 500