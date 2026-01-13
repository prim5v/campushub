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

def fetch_listing_details(current_user_id, role, listing_id):
    db = get_db()
    cursor = db.cursor()

    try:
        # 1️⃣ Fetch listing details with verified status and amenities
        fetch_listing_sql = """
            SELECT l.*, p.verified, p.amenities
            FROM listings_data l
            LEFT JOIN properties_data p ON l.property_id = p.property_id
            WHERE l.listing_id = %s AND l.availability_status = 'available'
        """
        cursor.execute(fetch_listing_sql, (listing_id,))
        listing = cursor.fetchone()

        if not listing:
            return jsonify({"listing": None}), 404

        # 2️⃣ Fetch all images for this listing
        fetch_images_sql = """
            SELECT image_url
            FROM images
            WHERE listing_id = %s
        """
        cursor.execute(fetch_images_sql, (listing_id,))
        images = cursor.fetchall()
        listing["images"] = [img["image_url"] for img in images]

        # 3️⃣ Fetch location for listing or property
        fetch_location_sql = """
            SELECT *
            FROM location_data
            WHERE listing_id = %s OR property_id = %s
            LIMIT 1
        """
        cursor.execute(fetch_location_sql, (listing_id, listing["property_id"]))
        loc = cursor.fetchone()
        if loc:
            listing["location"] = {
                "latitude": loc["latitude"],
                "longitude": loc["longitude"],
                "address": loc.get("address")
            }
        else:
            listing["location"] = {}

        # 4️⃣ Fetch all reviews for this listing
        fetch_reviews_sql = """
            SELECT r.*, u.username, u.user_id
            FROM reviews r
            LEFT JOIN users u ON r.user_id = u.user_id
            WHERE r.listing_id = %s
            ORDER BY r.review_date DESC
        """
        cursor.execute(fetch_reviews_sql, (listing_id,))
        reviews = cursor.fetchall()
        reviews_list = []

        for review in reviews:
            # Fetch user image if exists
            cursor.execute("""
                SELECT image_url
                FROM images
                WHERE user_id = %s
                ORDER BY uploaded_at DESC
                LIMIT 1
            """, (review["user_id"],))
            user_img = cursor.fetchone()
            reviews_list.append({
                "review_id": review["id"],
                "review_text": review["review_text"],
                "rating": review["rating"],
                "review_date": review["review_date"],
                "user": {
                    "user_id": review["user_id"],
                    "username": review["username"],
                    "image": user_img["image_url"] if user_img else None
                }
            })

        listing["reviews"] = reviews_list

        # 5️⃣ Calculate average rating and number of ratings
        if reviews_list:
            avg_rating = sum(r["rating"] for r in reviews_list) / len(reviews_list)
            listing["rating"] = {
                "average_rating": round(avg_rating, 2),
                "num_ratings": len(reviews_list)
            }
        else:
            listing["rating"] = {
                "average_rating": 0,
                "num_ratings": 0
            }

        return jsonify({"listing": listing}), 200

    except Exception as e:
        print(f"[ERROR] Exception occurred: {e}")
        return jsonify({"error": str(e)}), 500
