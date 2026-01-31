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



def verify_selfie_route(current_user_id, *args, **kwargs):
    db = get_db()
    cursor = db.cursor(pymysql.cursors.DictCursor)

    session_id = request.form.get("session_id")
    selfie = request.files.get("selfie")

    if not session_id or not selfie:
        return jsonify({"error": "Missing session_id or selfie"}), 400

    cursor.execute(
        "SELECT * FROM id_verification WHERE session_id=%s AND user_id=%s",
        (session_id, current_user_id)
    )
    record = cursor.fetchone()

    if not record:
        return jsonify({"error": "Invalid verification session"}), 404

    selfie_path = os.path.join(
        current_app.config["UPLOAD_FOLDER"],
        f"{session_id}_selfie.jpg"
    )
    selfie.save(selfie_path)

    if is_blurry(selfie_path):
        return jsonify({"error": "Selfie too blurry"}), 400

    selfie_embedding = extract_face_embedding(selfie_path)
    if selfie_embedding is None:
        return jsonify({"error": "No face detected in selfie"}), 400

    id_embedding = pickle.loads(record["face_embedding"])
    similarity = compare_faces(id_embedding, selfie_embedding)

    if similarity >= 0.90:
        return jsonify({
            "message": "Identity verified successfully",
            "similarity": round(similarity, 3)
        }), 200

    # ❌ Failed — cleanup
    cursor.execute("DELETE FROM id_verification WHERE session_id=%s", (session_id,))
    db.commit()

    return jsonify({
        "error": "Face mismatch",
        "similarity": round(similarity, 3)
    }), 403
