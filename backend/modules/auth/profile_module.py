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

def check_profile(current_user_id, role):

    print("[DEBUG] /profile route called")
    print(f"[DEBUG] Current User ID from token: {current_user_id}, Role from token: {role}")

    try:
        conn = get_db()
        print("[DEBUG] Database connection established")

        with conn.cursor(pymysql.cursors.DictCursor) as cursor:

            query = """
                SELECT 
                    u.user_id,
                    u.username,
                    u.email,
                    u.phone,
                    u.role,
                    u.plan,
                    u.is_active,
                    u.created_at,

                    s.id_number,
                    s.full_name,
                    s.check_type,
                    s.status AS verification_status,
                    s.reviewed_by,
                    s.review_notes,
                    s.performed_at AS verification_date

                FROM users u
                LEFT JOIN security_checks s ON u.user_id = s.user_id
                WHERE u.user_id = %s
                LIMIT 1
            """

            print(f"[DEBUG] Executing profile join query for user_id={current_user_id}")
            cursor.execute(query, (current_user_id,))
            user = cursor.fetchone()

            print(f"[DEBUG] Query result: {user}")

            if not user:
                print("[DEBUG] User not found — returning default student role")

                return jsonify({
                    "message": "Access granted",
                    "user": {
                        "user_id": current_user_id,
                        "email": "unknown@student.com",
                        "role": "student",
                        "username": "Default Student",
                        "created_at": None,
                        "verification": None
                    }
                }), 200

            # Build clean profile object
            profile = {
                "user_id": user["user_id"],
                "username": user["username"],
                "email": user["email"],
                "phone": user["phone"],
                "role": user["role"],
                "plan": user["plan"],
                "is_active": bool(user["is_active"]),
                "created_at": user["created_at"],

                "verification": {
                    "id_number": user["id_number"],
                    "full_name": user["full_name"],
                    "check_type": user["check_type"],
                    "status": user["verification_status"],
                    "reviewed_by": user["reviewed_by"],
                    "review_notes": user["review_notes"],
                    "performed_at": user["verification_date"],
                }
            }

            print("[DEBUG] Returning full merged profile")

            return jsonify({
                "message": "Access granted",
                "user": profile
            }), 200

    except Exception as e:
        print(f"[ERROR] Exception occurred: {e}")
        return jsonify({"error": str(e)}), 500
