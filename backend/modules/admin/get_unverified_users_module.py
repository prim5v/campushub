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

def fetch_unverified_users():
    db = get_db()
    cursor = db.cursor()

    try:
        # Fetch users whose security check status is 'unverified'
        unverified_sql = """
            SELECT 
                u.id,
                u.user_id,
                u.username,
                u.email,
                u.phone,
                u.role,
                u.is_active,
                u.created_at,

                sc.id AS security_id,
                sc.id_number,
                sc.full_name,
                sc.check_type,
                sc.status AS security_status,
                sc.reviewed_by,
                sc.review_notes,
                sc.performed_at

            FROM users u
            JOIN security_checks sc ON u.user_id = sc.user_id
            WHERE sc.status = 'pending'
        """
        cursor.execute(unverified_sql)
        unverified_users = cursor.fetchall()

        return jsonify({"unverified_users": unverified_users}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
