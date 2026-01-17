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


from ...utils.db_connection import get_db

def fetch_listings(current_user_id, role, *args, **kwargs):
    db = get_db()
    cursor = db.cursor(pymysql.cursors.DictCursor)

    try:
        # 1️⃣ Fetch listings
        fetch_listings_sql = """
            SELECT *
            FROM listings_data
            WHERE user_id = %s
        """
        cursor.execute(fetch_listings_sql, (current_user_id,))
        listings = cursor.fetchall()

        if not listings:
            return jsonify({"listings": []}), 200

        # 2️⃣ Collect listing IDs and property IDs
        listing_ids = [listing["id"] for listing in listings]
        property_ids = list(set([
            listing["property_id"]
            for listing in listings
            if listing.get("property_id")
        ]))

        # 3️⃣ Fetch images for those listings
        placeholders = ",".join(["%s"] * len(listing_ids))
        fetch_images_sql = f"""
            SELECT listing_id, image_url
            FROM images
            WHERE listing_id IN ({placeholders})
        """
        cursor.execute(fetch_images_sql, listing_ids)
        image_rows = cursor.fetchall()

        # 4️⃣ Build images map
        images_map = {}
        base_url = request.host_url.rstrip("/")

        for img in image_rows:
            full_url = f"{base_url}/static/images/{img['image_url']}"
            images_map.setdefault(img["listing_id"], []).append(full_url)

        # 5️⃣ Fetch locations using property_id
        locations_map = {}

        if property_ids:
            prop_placeholders = ",".join(["%s"] * len(property_ids))
            fetch_locations_sql = f"""
                SELECT property_id, address, latitude, longitude
                FROM Location_data
                WHERE property_id IN ({prop_placeholders})
            """
            cursor.execute(fetch_locations_sql, property_ids)
            location_rows = cursor.fetchall()

            for loc in location_rows:
                locations_map[loc["property_id"]] = {
                    "address": loc["address"],
                    "latitude": float(loc["latitude"]),
                    "longitude": float(loc["longitude"]),
                }

        # 6️⃣ Attach images + location to listings
        for listing in listings:
            listing["images"] = images_map.get(listing["id"], [])

            listing["location"] = locations_map.get(
                listing["property_id"],
                None  # or {"address": None, "latitude": None, "longitude": None}
            )

        return jsonify({"listings": listings}), 200

    except Exception as e:
        print(f"[ERROR] fetch_listings: {e}")
        return jsonify({"error": "Failed to fetch listings"}), 500




{
    "listings": [
        {
            "id": 1,
            "listing_id": "LIST123",
            "property_id": "PROP456",
            "user_id": "USER789",
            "listing_name": "Modern Bedsitter",
            "listing_description": "A cozy and modern bedsitter located in the heart of the city.",
            "deposits": { "deposit amount": 5000, "water deposits":2000, "electricity deposits":3000 },
            "listing_type": "bedsitter",
            "price": 12000,
            "renting_price": 13000,
            "timeline": "monthly",
            "availability_status": "available",
            "availability_date": "2023-10-01",
            "listed_at": "2023-09-15T10:00:00",
            "images": [
            "http://127.0.0.1:5000/static/images/img1.jpg",
            "http://127.0.0.1:5000/static/images/img2.jpg"
            ],
        "location": {
            "address": "Thika Road, Roysambu",
            "latitude": -1.218453,
            "longitude": 36.889012
        }
        }
    ]
}
