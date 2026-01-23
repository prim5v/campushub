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
# from backend import app.config["UPLOAD_FOLDER"]




def fetch_add_listing(current_user_id, role, *args, **kwargs):
    """
    Add a new listing with images, amenities, room size, and max occupants.
    listing_id is now VARCHAR, compatible with UUID strings.
    """
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    db = get_db()
    cursor = db.cursor(pymysql.cursors.DictCursor)

    data = request.form  # REQUIRED for file uploads

    # Required fields
    listing_name = data.get("listing_name")
    property_id = data.get("property_id")
    listing_description = data.get("listing_description")
    listing_type = data.get("listing_type")
    availability_status = data.get("availability_status")
    availability_date = data.get("availability_date")
    timeline = data.get("timeline")
    price = data.get("price")
    deposits = data.get("deposits")

    # New optional fields
    room_size = data.get("room_size")  # e.g., "18 sqm"
    max_occupants = data.get("max_occupants")  # e.g., "2"

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

    images = request.files.getlist("product_images")

    # Validate required fields
    if not images:
        return jsonify({"error": "At least one listing image is required"}), 400

    if not all([listing_name, property_id, availability_status, price]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        price = float(price)
        if price <= 0:
            return jsonify({"error": "Price must be greater than 0"}), 400
    except ValueError:
        return jsonify({"error": "Price must be a valid number"}), 400

    allowed_timeline = {"daily", "weekly", "monthly"}
    if timeline not in allowed_timeline:
        return jsonify({"error": "Invalid timeline value"}), 400

    os.makedirs(upload_folder, exist_ok=True)

    # Generate listing_id (string)
    listing_id = uuid.uuid4().hex[:12]

    # Calculate profit
    profitpercent = Decimal("0.1")
    price_decimal = Decimal(str(price))
    profit = profitpercent * price_decimal
    renting_price = price_decimal + profit

    try:
        # 1️⃣ Insert listing with room_size and max_occupants
        insert_listing_sql = """
            INSERT INTO listings_data (
                listing_id, user_id, property_id, listing_name, listing_type,
                listing_description, availability_status,
                availability_date, timeline, price, renting_price, deposits,
                room_size, max_occupants
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(
            insert_listing_sql,
            (
                listing_id,
                current_user_id,
                property_id,
                listing_name,
                listing_type,
                listing_description,
                availability_status,
                availability_date,
                timeline,
                float(price_decimal),
                float(renting_price),
                deposits,
                room_size,
                max_occupants
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
            "message": "Listing added successfully",
            "listing_id": listing_id,
            "images": saved_files,
            "amenities": amenities_keys,
            "room_size": room_size,
            "max_occupants": max_occupants
        }), 201

    except Exception as e:
        db.rollback()
        logging.error(f"Error adding listing: {str(e)}")
        return jsonify({"error": str(e)}), 500
