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
from ...utils.vision import is_blurry, extract_face_embedding, compare_faces
import pickle


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

    # 1️⃣ Blur check
    if is_blurry(front_path) or is_blurry(back_path):
        return jsonify({"error": "ID image too blurry"}), 400

    # 2️⃣ Face extraction
    embedding = extract_face_embedding(front_path)
    if embedding is None:
        return jsonify({"error": "No face detected on ID"}), 400

    # 3️⃣ OCR (simplified placeholder)
    extracted = {
        "surname": "DOE",
        "other_names": "JOHN",
        "gender": "M",
        "id_number": "12345678",
        "place_of_birth": "KISUMU",
        "place_of_issue": "NAIROBI",
        "serial_number": "AA123456"
    }

    required_fields = ["surname", "other_names", "gender", "id_number"]
    if not all(extracted.get(f) for f in required_fields):
        return jsonify({"error": "Unable to extract all required ID fields"}), 400

    # 4️⃣ Store in DB
    cursor.execute("""
        INSERT INTO id_verification (
            user_id, session_id, surname, other_names, gender,
            id_number, place_of_birth, place_of_issue,
            serial_number, id_image_front, id_image_back, face_embedding
        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        current_user_id,
        session_id,
        extracted["surname"],
        extracted["other_names"],
        extracted["gender"],
        extracted["id_number"],
        extracted["place_of_birth"],
        extracted["place_of_issue"],
        extracted["serial_number"],
        front_path,
        back_path,
        pickle.dumps(embedding)
    ))

    db.commit()

    return jsonify({
        "message": "ID verified. Proceed to selfie verification",
        "session_id": session_id
    }), 200
