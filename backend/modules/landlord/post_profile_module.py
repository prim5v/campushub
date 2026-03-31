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
    logging.warning(f"[DEBUG] Content-Type: {request.content_type}")
    logging.warning(f"[DEBUG] request.form: {request.form}")
    logging.warning(f"[DEBUG] request.files: {request.files}")
    logging.warning(f"[DEBUG] data dict: {data}")

    upload_folder = current_app.config.get("UPLOAD_FOLDER", "uploads")
    db = get_db()
    cursor = db.cursor()

    logging.info(f"[POST_PROFILE] Called by user_id={current_user_id}, role={role}")

    try:
        # Extract data
        fullname = data.get("full_name")
        phone = data.get("phone")
        id_number = data.get("id_number")
        username = data.get("username")

        logging.debug(f"[POST_PROFILE] Received data: fullname={fullname}, phone={phone}, "
                      f"id_number={id_number}, username={username}")

        profile_picture = request.files.get("profile_picture")
        if profile_picture:
            logging.debug(f"[POST_PROFILE] Profile picture uploaded: {profile_picture.filename}")
        else:
            logging.debug("[POST_PROFILE] No profile picture uploaded")

        # Validate required fields
        if not all([fullname, phone, id_number, username]):
            logging.warning("[POST_PROFILE] Missing required fields")
            return jsonify({"error": "missing required fields"}), 400

        # Validate phone
        if not re.match(r'^\+?\d{10,15}$', phone):
            logging.warning(f"[POST_PROFILE] Invalid phone number: {phone}")
            return jsonify({"error": "invalid phone number"}), 400

        # Check username duplicate
        cursor.execute(
            "SELECT user_id FROM users WHERE username=%s AND user_id!=%s",
            (username, current_user_id)
        )
        if cursor.fetchone():
            logging.warning(f"[POST_PROFILE] Username already taken: {username}")
            return jsonify({"error": "username already taken"}), 400

        # Ensure upload folder exists
        os.makedirs(upload_folder, exist_ok=True)
        logging.debug(f"[POST_PROFILE] Upload folder verified: {upload_folder}")

        db.begin()

        # Update user
        cursor.execute("""
            UPDATE users
            SET phone=%s, username=%s
            WHERE user_id=%s
        """, (phone, username, current_user_id))
        logging.info(f"[POST_PROFILE] User table updated for user_id={current_user_id}")

        # update security_checks
        cursor.execute("""
             UPDATE security_checks
             SET full_name=%s, id_number=%s
             WHERE user_id=%s
         """, (fullname, id_number, current_user_id))

        # Save profile picture
        if profile_picture:
            if not profile_picture.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                logging.warning(f"[POST_PROFILE] Invalid image format: {profile_picture.filename}")
                return jsonify({"error": "invalid image format"}), 400

            filename = secure_filename(profile_picture.filename)
            filename = f"{uuid.uuid4().hex}_{filename}"
            image_path = os.path.join(upload_folder, filename)
            profile_picture.save(image_path)
            logging.info(f"[POST_PROFILE] Profile picture saved: {image_path}")

            cursor.execute(
                "INSERT INTO images (user_id, image_url) VALUES (%s, %s)",
                (current_user_id, filename)
            )
            logging.info(f"[POST_PROFILE] Image record inserted into DB for user_id={current_user_id}")

        db.commit()
        logging.info(f"[POST_PROFILE] Transaction committed successfully for user_id={current_user_id}")

        return jsonify({"message": "profile updated successfully"}), 200

    except Exception as e:
        db.rollback()
        logging.error(f"[POST_PROFILE] Exception occurred: {e}", exc_info=True)
        return jsonify({"error": "internal server error"}), 500