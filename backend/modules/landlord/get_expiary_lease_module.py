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

def fetch_expiary_lease(current_user_id, role):
    db = get_db()
    cursor = db.cursor()

    try:
        # 🔐 Optional role guard (recommended)
        if role not in ("landlord", "admin"):
            return {
                "success": False,
                "message": "Unauthorized access"
            }

        # 1️⃣ Fetch leases expiring in next 2 months
        sql = """
            SELECT
                tenant_id,
                tenant_name,
                tenant_email,
                tenant_phone,
                listing_id,
                rent_amount,
                lease_start_date,
                lease_end_date,
                DATEDIFF(lease_end_date, CURDATE()) AS days_remaining
            FROM tenants_data
            WHERE user_id = %s
              AND lease_end_date >= CURDATE()
              AND lease_end_date <= DATE_ADD(CURDATE(), INTERVAL 2 MONTH)
            ORDER BY lease_end_date ASC
        """

        cursor.execute(sql, (current_user_id,))
        expiring_leases = cursor.fetchall()

        return {
            "success": True,
            "count": len(expiring_leases),
            "data": expiring_leases
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
