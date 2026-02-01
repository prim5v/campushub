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


def set_user_status():
    """
    Activate / Deactivate a user account
    """

    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id")
    is_active = data.get("is_active")

    # ---- validation ----
    if not user_id or is_active is None:
        return jsonify({"error": "user_id and is_active are required"}), 400

    if is_active not in (0, 1, True, False):
        return jsonify({"error": "is_active must be 0 or 1"}), 400

    is_active = int(is_active)

    # prevent admin from disabling self
    if user_id == g.user["user_id"]:
        return jsonify({"error": "You cannot change your own account status"}), 400

    conn = get_db()
    cursor = conn.cursor()

    # ---- check user exists ----
    cursor.execute("""
        SELECT user_id, username, email, role, is_active
        FROM users
        WHERE user_id = %s
        LIMIT 1
    """, (user_id,))
    user = cursor.fetchone()

    if not user:
        return jsonify({"error": "User not found"}), 404

    # ---- update status ----
    cursor.execute("""
        UPDATE users
        SET is_active = %s
        WHERE user_id = %s
    """, (is_active, user_id))

    conn.commit()

    return jsonify({
        "status": "success",
        "message": "User status updated successfully",
        "user": {
            "user_id": user["user_id"],
            "username": user["username"],
            "email": user["email"],
            "role": user["role"],
            "is_active": is_active
        }
    }), 200