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
import json
from ...utils.email_setup import mail   
from ...utils.db_connection import get_db
from ...utils.jwt_setup import generate_jwt
import bcrypt, uuid
from datetime import datetime, timedelta
from ...utils.extra_functions import (generate_otp, send_security_email, send_informational_email, get_device_info)
# from ...utils.vision import is_blurry, extract_face_embedding, compare_faces
# import pickle


def verify_id_route(current_user_id, *args, **kwargs):
    db = get_db()
    cursor = db.cursor(pymysql.cursors.DictCursor)

    id_front = request.files.get("id_front")
    id_back = request.files.get("id_back")

    if not id_front or not id_back:
        return jsonify({"error": "ID front and back required"}), 400

    session_id = uuid.uuid4().hex[:12]
    upload_dir = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_dir, exist_ok=True)

    front_path = os.path.join(upload_dir, f"{session_id}_front.jpg")
    back_path = os.path.join(upload_dir, f"{session_id}_back.jpg")

    id_front.save(front_path)
    id_back.save(back_path)
    # Store verification record
    cursor.execute("""
        INSERT INTO verification (user_id, session_id)
        VALUES (%s, %s, %s, %s)
    """, (current_user_id, session_id))
    # insert into image table
    cursor.execute("""
        INSERT INTO images (user_id, session_id, image_url)
        VALUES (%s, %s, %s)
    """, (current_user_id, session_id, front_path))
    cursor.execute("""
        INSERT INTO images (user_id, session_id, image_url)
        VALUES (%s, %s, %s)
    """, (current_user_id, session_id, back_path))

    db.commit()

    return jsonify({
        "message": "ID verified. Proceed to selfie verification",
        "session_id": session_id
    }), 200
