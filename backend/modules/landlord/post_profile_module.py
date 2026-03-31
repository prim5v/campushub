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
import os


from ...utils.db_connection import get_db
from werkzeug.utils import secure_filename

def post_profile(current_user_id, role, data):
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    db = get_db()
    cursor = db.cursor()

    try:
        fullname = data.get("fullname")
        phone = data.get("phone")
        id_number = data.get("id_number")
        username = data.get("username")

        profile_picture = request.files.get("profile_picture")

        if not all([fullname, phone, id_number, username]):
            return jsonify({"error": "missing required fields"}), 400

        # Validate phone
        if not re.match(r'^\+?\d{10,15}$', phone):
            return jsonify({"error": "invalid phone number"}), 400

        # Check username duplicate
        cursor.execute("SELECT user_id FROM users WHERE username=%s AND user_id!=%s", (username, current_user_id))
        if cursor.fetchone():
            return jsonify({"error": "username already taken"}), 400

        os.makedirs(upload_folder, exist_ok=True)

        db.begin()

        # Update user
        cursor.execute("""
            UPDATE users 
            SET fullname=%s, phone=%s, id_number=%s, username=%s
            WHERE user_id=%s
        """, (fullname, phone, id_number, username, current_user_id))

        # Save profile picture
        if profile_picture:
            if not profile_picture.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                return jsonify({"error": "invalid image format"}), 400

            filename = secure_filename(profile_picture.filename)
            filename = f"{uuid.uuid4().hex}_{filename}"
            image_path = os.path.join(upload_folder, filename)
            profile_picture.save(image_path)

            cursor.execute(
                "INSERT INTO images (user_id, image_url) VALUES (%s, %s)",
                (current_user_id, filename)
            )

        db.commit()
        return jsonify({"message": "profile updated successfully"}), 200

    except Exception as e:
        db.rollback()
        logging.error(f"Error updating profile: {e}")
        return jsonify({"error": "internal server error"}), 500