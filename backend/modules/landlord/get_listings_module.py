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
    cursor = db.cursor(pymysql.cursors.DictCursor)  # get dict results

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

        # 2️⃣ Get listing IDs
        listing_ids = [listing["id"] for listing in listings]

        # 3️⃣ Fetch images for those listings
        placeholders = ",".join(["%s"] * len(listing_ids))
        fetch_images_sql = f"""
            SELECT listing_id, image_url
            FROM images
            WHERE listing_id IN ({placeholders})
        """
        cursor.execute(fetch_images_sql, listing_ids)
        image_rows = cursor.fetchall()

        # 4️⃣ Build images map with FULL URLs
        images_map = {}
        base_url = request.host_url.rstrip("/")

        for img in image_rows:
            full_url = f"{base_url}/static/images/{img['image_url']}"
            images_map.setdefault(img["listing_id"], []).append(full_url)

        # 5️⃣ Attach images to listings
        for listing in listings:
            listing["images"] = images_map.get(listing["id"], [])

        return jsonify({"listings": listings}), 200

    except Exception as e:
        print(f"[ERROR] fetch_listings: {e}")
        return jsonify({"error": "Failed to fetch listings"}), 500

