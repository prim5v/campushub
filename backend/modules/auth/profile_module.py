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

        with conn.cursor() as cursor:
            query = "SELECT * FROM Users WHERE user_id = %s"
            print(f"[DEBUG] Executing query: {query} with user_id={current_user_id}")
            cursor.execute(query, (current_user_id,))
            user = cursor.fetchone()

            print(f"[DEBUG] Query result: {user}")

            if not user:
                print("[DEBUG] User not found — returning default student role")
                # Return a default student role instead of 404
                return jsonify({
                    "message": "Access granted", 
                    "user": {
                        "id": current_user_id,
                        "email": "unknown@student.com",
                        "role": "student",
                        "name": "Default Student",
                        "created_at": None
                    }
                }), 200

            print("[DEBUG] User found, returning success response")
            return jsonify({
                "message": "Access granted",
                "user": user
            }), 200

    except Exception as e:
        print(f"[ERROR] Exception occurred: {e}")
        return jsonify({"error": str(e)}), 500
