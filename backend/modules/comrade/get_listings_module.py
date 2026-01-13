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

def fetch_listings(current_user_id, role):
    db = get_db()
    cursor = db.cursor()

    try:
        # 1️⃣ Fetch only available listings with property verified status using JOIN
        fetch_listings_sql = """
            SELECT l.*, p.verified
            FROM listings_data l
            LEFT JOIN properties_data p ON l.property_id = p.property_id
            WHERE l.availability_status = 'available'
        """
        cursor.execute(fetch_listings_sql)
        listings = cursor.fetchall()

        if not listings:
            return jsonify({"listings": []}), 200

        listing_ids = [listing["listing_id"] for listing in listings]

        # 2️⃣ Fetch all images for listings in one query
        fetch_images_sql = """
            SELECT listing_id, image_url
            FROM images
            WHERE listing_id = ANY(%s)
        """
        cursor.execute(fetch_images_sql, (listing_ids,))
        images = cursor.fetchall()

        images_map = {}
        for img in images:
            images_map.setdefault(img["listing_id"], []).append(img["image_url"])

        # 3️⃣ Fetch all location data for listings and properties in one query
        fetch_locations_sql = """
            SELECT *
            FROM location_data
            WHERE listing_id = ANY(%s) OR property_id = ANY(%s)
        """
        property_ids = [listing["property_id"] for listing in listings]
        cursor.execute(fetch_locations_sql, (listing_ids, property_ids))
        locations = cursor.fetchall()

        location_map = {}
        for loc in locations:
            key = loc["listing_id"] if loc["listing_id"] else loc["property_id"]
            location_map[key] = {
                "latitude": loc["latitude"],
                "longitude": loc["longitude"],
                "address": loc.get("address")
            }

        # 4️⃣ Fetch all reviews for listings in one query
        fetch_reviews_sql = """
            SELECT listing_id, rating
            FROM reviews
            WHERE listing_id = ANY(%s)
        """
        cursor.execute(fetch_reviews_sql, (listing_ids,))
        reviews = cursor.fetchall()

        ratings_map = {}
        for listing_id in listing_ids:
            listing_reviews = [r["rating"] for r in reviews if r["listing_id"] == listing_id]
            if listing_reviews:
                avg_rating = sum(listing_reviews) / len(listing_reviews)
                ratings_map[listing_id] = {
                    "average_rating": round(avg_rating, 2),
                    "num_ratings": len(listing_reviews)
                }
            else:
                ratings_map[listing_id] = {
                    "average_rating": 0,
                    "num_ratings": 0
                }

        # 5️⃣ Attach images, location, and ratings to each listing
        for listing in listings:
            listing_id = listing["listing_id"]
            property_id = listing["property_id"]

            listing["images"] = images_map.get(listing_id, [])
            listing["location"] = location_map.get(listing_id) or location_map.get(property_id, {})
            listing["rating"] = ratings_map.get(listing_id)

        return jsonify({"listings": listings}), 200

    except Exception as e:
        print(f"[ERROR] Exception occurred: {e}")
        return jsonify({"error": str(e)}), 500



