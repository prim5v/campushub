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



def fetch_add_property(current_user_id, role, *args, **kwargs):
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    print(f"[DEBUG] Upload folder: {upload_folder}")
    print(f"[DEBUG] Current user ID: {current_user_id}, role: {role}")

    db = get_db()
    cursor = db.cursor()

    # Get data from form or JSON
    data = request.form
    print(f"[DEBUG] Incoming data keys: {list(data.keys()) if data else 'No data'}")

    property_name = data.get("property_name")
    property_description = data.get("property_description")
    property_type = data.get("property_type")

    # Location fields
    address = data.get("address")
    latitude = data.get("latitude")
    longitude = data.get("longitude")

    images = request.files.getlist("product_images")
    print(f"[DEBUG] Number of uploaded images: {len(images)}")

    # Validation
    if not images or len(images) == 0:
        print("[ERROR] No images provided")
        return jsonify({"error": "At least one listing image is required"}), 400

    if not all([property_name, property_description, property_type, address, latitude, longitude]):
        print("[ERROR] Missing required fields")
        return jsonify({"error": "All fields including location are required"}), 400

    allowed_types = {"house", "apartment", "condo", "townhouse", "hostel", "bedsitter"}
    if property_type not in allowed_types:
        print(f"[ERROR] Invalid property type: {property_type}")
        return jsonify({"error": "Invalid property type"}), 400

    os.makedirs(upload_folder, exist_ok=True)
    print("[DEBUG] Upload folder created or exists")

    # Generate 12+ char UUID
    property_id = uuid.uuid4().hex[:12]
    print(f"[DEBUG] Generated property ID: {property_id}")

    try:
        # 1️⃣ Insert property
        addsql = """
            INSERT INTO properties_data (
                property_id,
                user_id,
                property_name,
                property_description,
                property_type
            )
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(
            addsql,
            (property_id, current_user_id, property_name, property_description, property_type)
        )
        db.commit()
        print("[DEBUG] Property inserted successfully")

        # 2️⃣ Insert images
        insert_image = """
            INSERT INTO images (user_id, property_id, image_url)
            VALUES (%s, %s, %s)
        """
        saved_files = []
        for image in images:
            filename = f"{uuid.uuid4().hex}_{image.filename}"
            image_path = os.path.join(upload_folder, filename)
            image.save(image_path)
            cursor.execute(insert_image, (current_user_id, property_id, filename))
            saved_files.append(filename)
            print(f"[DEBUG] Saved image: {filename}")

        db.commit()
        print(f"[DEBUG] Total images saved: {len(saved_files)}")

        # 3️⃣ Insert location data
        insert_location = """
            INSERT INTO Location_data (user_id, property_id, latitude, longitude, address)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(insert_location, (current_user_id, property_id, latitude, longitude, address))
        db.commit()
        print("[DEBUG] Location data inserted successfully")

        return jsonify({
            "status": "success",
            "property_id": property_id,
            "message": "Property added successfully"
        }), 201

    except Exception as e:
        db.rollback()
        print(f"[ERROR] Exception occurred: {e}")
        return jsonify({"error": str(e)}), 500
