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





def perform_verify_ids(data):
    if "front" not in data or "back" not in data:
        return jsonify({"error": "Both front and back images required"}), 400

    front_file = data["front"]
    back_file = data["back"]
    front_path = os.path.join(UPLOAD_FOLDER, secure_filename(front_file.filename))
    back_path = os.path.join(UPLOAD_FOLDER, secure_filename(back_file.filename))

    front_file.save(front_path)
    back_file.save(back_path)

    # ✅ Generate a cache key based on both files
    combined_hash = hashlib.sha256()
    combined_hash.update(open(front_path, "rb").read())
    combined_hash.update(open(back_path, "rb").read())
    cache_key = combined_hash.hexdigest()

    # Check Redis cache first
    if r.exists(cache_key):
        print("✅ Cache hit")
        cached_result = r.get(cache_key).decode()
        try:
            return jsonify(json.loads(cached_result))
        except json.JSONDecodeError:
            # Fallback if cached data is corrupted
            print("⚠️ Cached AI output invalid, regenerating...")

    # 1️⃣ Prepare prompt for AI
    prompt = f"""
You are an AI ID verification assistant for CompassHub.

Check the two uploaded ID images (front and back) and:

1. Reject if the image is blurry, cropped, or missing essential information.
2. Accept only if all data is clearly visible.
3. Extract the following fields: name, date of birth (DOB), ID number, 
4. Return strictly valid JSON exactly like this format:
{{
  "status": "accepted" or "rejected",
  "reason": "reason if rejected, else empty",
  "data": {{
    "name": "...",
    "dob": "...",
    "id_number": "..."
  }}
}}
Images:
Front: {front_path}
Back: {back_path}
"""

    try:
        # 2️⃣ Call AI
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # or GPT-4V if available
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        ai_result = response.choices[0].message.content.strip()

        # Ensure it’s valid JSON
        ai_json = json.loads(ai_result)

        # 3️⃣ Cache AI result (expire 1 hour)
        r.set(cache_key, json.dumps(ai_json), ex=3600)

        # 4️⃣ Return to frontend
        return jsonify(ai_json)

    except Exception as e:
        print("❌ AI error:", str(e))
        return jsonify({"error": str(e)}), 500

    finally:
        # Optional: clean up uploaded images
        os.remove(front_path)
        os.remove(back_path)

