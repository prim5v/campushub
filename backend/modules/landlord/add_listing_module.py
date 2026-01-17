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
    upload_folder = current_app.config["UPLOAD_FOLDER"]


    db = get_db()
    cursor = db.cursor()

    data = request.form  # REQUIRED for file uploads

    listing_name = data.get("listing_name")
    property_id = data.get("property_id")
    listing_description = data.get("listing_description")
    listing_type = data.get("listing_type")
    availability_status = data.get("availability_status")
    availability_date = data.get("availability_date")
    timeline = data.get("timeline")
    price = data.get("price")
    deposits = data.get("deposits")

    images = request.files.getlist("product_images")

    if not images or len(images) == 0:
        return jsonify({"error": "At least one listing image is required"}), 400

    if not all([listing_name, property_id, availability_status, price]):
        return jsonify({"error": "Missing required fields"}), 400
    
    if float(price) <= 0:
        return jsonify({"error": "Price must be greater than 0"}), 400

    allowed_timeline = {"daily", "weekly", "monthly"}
    if timeline not in allowed_timeline:
        return jsonify({"error": "Invalid timeline value"}), 400

    os.makedirs(upload_folder, exist_ok=True)

    # Generate 12+ char UUID
    listing_id = uuid.uuid4().hex[:12]
    profitpercent = 0.1 # 10% profit change as per business logic
    profit = profitpercent * price
    renting_price = float(price) + profit

    try:
        # 1️⃣ Insert listing
        insert_listing = """
            INSERT INTO listings_data (
                listing_id, user_id, property_id, listing_name, listing_type,
                listing_description, availability_status,
                availability_date, timeline, price, renting_price, deposits
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        cursor.execute(
            insert_listing,
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
                price,
                renting_price,
                deposits
            ),
        )


        db.commit()

        # 2️⃣ Insert images
        insert_image = """
            INSERT INTO images (user_id, listing_id, image_url)
            VALUES (%s, %s, %s)
        """

        saved_files = []

        for image in images:
            filename = f"{uuid.uuid4().hex}_{image.filename}"
            image_path = os.path.join(upload_folder, filename)

            image.save(image_path)

            cursor.execute(
                insert_image,
                (current_user_id, listing_id, filename)
            )

            saved_files.append(filename)

        db.commit()

        return jsonify({
            "message": "Listing added successfully",
            "listing_id": listing_id,
            "images": saved_files
        }), 201

    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500

