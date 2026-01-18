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

    logging.info(f"Add listing request from user_id={current_user_id}, property_id={property_id}")

    if not images or len(images) == 0:
        logging.warning("No images provided")
        return jsonify({"error": "At least one listing image is required"}), 400

    if not all([listing_name, property_id, availability_status, price]):
        logging.warning("Missing required fields")
        return jsonify({"error": "Missing required fields"}), 400

    try:
        # Safely cast price to float
        price = float(price)
        if price <= 0:
            logging.warning(f"Invalid price: {price}")
            return jsonify({"error": "Price must be greater than 0"}), 400
    except ValueError:
        logging.error(f"Price is not a valid number: {price}")
        return jsonify({"error": "Price must be a valid number"}), 400

    allowed_timeline = {"daily", "weekly", "monthly"}
    if timeline not in allowed_timeline:
        logging.warning(f"Invalid timeline: {timeline}")
        return jsonify({"error": "Invalid timeline value"}), 400

    os.makedirs(upload_folder, exist_ok=True)

    # Generate listing_id
    listing_id = uuid.uuid4().hex[:12]

    # Profit calculation
    profitpercent = Decimal("0.1")  # 10% profit
    price_decimal = Decimal(str(price))
    profit = profitpercent * price_decimal
    renting_price = price_decimal + profit

    logging.info(f"Calculated profit={profit} renting_price={renting_price}")

    try:
        # Insert listing
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
                float(price_decimal),
                float(renting_price),
                deposits
            ),
        )
        db.commit()
        logging.info(f"Listing inserted successfully: {listing_id}")

        # Insert images
        insert_image = "INSERT INTO images (user_id, listing_id, image_url) VALUES (%s, %s, %s)"
        saved_files = []

        for image in images:
            filename = f"{uuid.uuid4().hex}_{image.filename}"
            image_path = os.path.join(upload_folder, filename)
            image.save(image_path)
            cursor.execute(insert_image, (current_user_id, listing_id, filename))
            saved_files.append(filename)

        db.commit()
        logging.info(f"Saved {len(saved_files)} images for listing {listing_id}")

        return jsonify({
            "message": "Listing added successfully",
            "listing_id": listing_id,
            "images": saved_files
        }), 201

    except Exception as e:
        db.rollback()
        logging.error(f"Error adding listing: {str(e)}")
        return jsonify({"error": str(e)}), 500
