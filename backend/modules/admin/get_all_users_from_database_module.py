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


# this fuction will fetch all users details,count daily, monthly 
def fetch_all_users():
    db = get_db()
    cursor = db.cursor()  # important for JSON-friendly results

    try:
        # 1. Fetch users with security checks + profile image
        users_sql = """
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
                sc.performed_at,

                img.image_url AS profile_image

            FROM users u
            LEFT JOIN security_checks sc 
                ON sc.user_id = u.user_id
            LEFT JOIN images img
                ON img.user_id = u.user_id
                AND img.sales_id IS NULL
        """

        cursor.execute(users_sql)
        rows = cursor.fetchall()

        # 2. Organize users properly
        users_map = {}

        for row in rows:
            uid = row["user_id"]

            if uid not in users_map:
                users_map[uid] = {
                    "id": row["id"],
                    "user_id": row["user_id"],
                    "username": row["username"],
                    "email": row["email"],
                    "phone": row["phone"],
                    "role": row["role"],
                    "is_active": row["is_active"],
                    "created_at": row["created_at"],
                    "profile_image": row["profile_image"],
                    "security_checks": []
                }

            # Append security check if exists
            if row["security_id"]:
                users_map[uid]["security_checks"].append({
                    "id": row["security_id"],
                    "id_number": row["id_number"],
                    "full_name": row["full_name"],
                    "check_type": row["check_type"],
                    "status": row["security_status"],
                    "reviewed_by": row["reviewed_by"],
                    "review_notes": row["review_notes"],
                    "performed_at": row["performed_at"]
                })

        users_list = list(users_map.values())

        # 3. Get total users count
        count_sql = "SELECT COUNT(*) AS users_count FROM users"
        cursor.execute(count_sql)
        users_count = cursor.fetchone()["users_count"]

        return jsonify({
            "users_count": users_count,
            "users": users_list
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
