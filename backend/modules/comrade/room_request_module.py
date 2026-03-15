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

def make_room_request(current_user_id, role, *args, **kwargs):
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    data = request.form or request.get_json(silent=True) or {}

    title = data.get("title")
    room_description = data.get("description")
    room_type = data.get("room_type")
    room_size = data.get("room_size")
    amenities_raw = data.get("amenities")
    images = request.files.getlist("room_images")
    deadline = data.get("deadline")
    price_range = data.get("price_range") #its a string
    max_occupants = data.get("max_occupants")
    phone = data.get("phone")

        # Parse max_occupants as integer if provided
    if max_occupants:
        try:
            max_occupants = int(max_occupants)
            if max_occupants <= 0:
                return jsonify({"error": "max_occupants must be greater than 0"}), 400
        except ValueError:
            return jsonify({"error": "max_occupants must be an integer"}), 400
    else:
        max_occupants = None

    # Amenities passed from frontend as JSON array: ["wifi", "parking"]
    amenities_raw = data.get("amenities")
    amenities_keys = []
    if amenities_raw:
        try:
            import json
            amenities_keys = json.loads(amenities_raw)
        except Exception:
            return jsonify({"error": "Invalid amenities format"}), 400


        # Validate required fields
    if not images:
        return jsonify({"error": "At least one listing image is required"}), 400

    if not all([title, price_range, room_description, room_type, room_size, deadline, phone]):
        return jsonify({"error": "Missing required fields"}), 400

    os.makedirs(upload_folder, exist_ok=True)
    listing_id = uuid.uuid4().hex[:12]

    try:
        db = get_db()
        cursor = db.cursor()

        # 1️⃣ Insert listing
        insert_room_sql = """
            INSERT INTO room_requests (
                listing_id, user_id, title, room_description, room_size, max_occupants,
                room_type, price_range, deadline, phone
            )
            VALUES( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(
            insert_room_sql,
            (
                listing_id,
                current_user_id,
                title,
                room_description,
                room_size,
                max_occupants,
                room_type,
                price_range,
                deadline,
                phone
            ),
        )


        # 2️⃣ Insert images
        insert_image_sql = "INSERT INTO images (user_id, listing_id, image_url) VALUES (%s, %s, %s)"
        saved_files = []
        for image in images:
            filename = f"{uuid.uuid4().hex}_{image.filename}"
            image_path = os.path.join(upload_folder, filename)
            image.save(image_path)
            cursor.execute(insert_image_sql, (current_user_id, listing_id, filename))
            saved_files.append(filename)



        # 3️⃣ Insert amenities into listings_amenities
        if amenities_keys:
            # Fetch amenity IDs
            format_strings = ",".join(["%s"] * len(amenities_keys))
            cursor.execute(
                f"SELECT id, amenity_key FROM amenities WHERE amenity_key IN ({format_strings})",
                amenities_keys
            )
            rows = cursor.fetchall()
            amenity_id_map = {row["amenity_key"]: row["id"] for row in rows}

            insert_listing_amenity_sql = """
                INSERT INTO listings_amenities (listing_id, amenity_id, available)
                VALUES (%s, %s, 1)
            """
            for key in amenities_keys:
                amenity_id = amenity_id_map.get(key)
                if amenity_id:
                    cursor.execute(insert_listing_amenity_sql, (listing_id, amenity_id))


        # 4️⃣ Commit everything
        db.commit()

        return jsonify({
            "message": "Request made succesfully"
        }), 201

    except Exception as e:
        db.rollback()
        logging.error(f"Error adding listing: {str(e)}")
        return jsonify({"error": str(e)}), 500
