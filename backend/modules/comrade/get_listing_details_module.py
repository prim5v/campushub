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
from ...utils.extra_functions import haversine_distance
import json
from decimal import Decimal
from datetime import datetime

def fetch_listing_details(data):
    """
    Expects:
    {
      "listing_id": "...",
      "coordinates": { "latitude": ..., "longitude": ... }
    }
    """

    listing_id = data.get("listing_id")
    coordinates = data.get("coordinates") or {}
    user_lat = coordinates.get("latitude")
    user_lon = coordinates.get("longitude")

    if not listing_id:
        return jsonify({"success": False, "error": "listing_id is required"}), 400

    db = get_db()
    cursor = db.cursor(pymysql.cursors.DictCursor)

    try:
        # 1️⃣ Fetch listing + property verified
        cursor.execute("""
            SELECT l.*, p.verified
            FROM listings_data l
            LEFT JOIN properties_data p ON l.property_id = p.property_id
            WHERE l.listing_id = %s AND l.availability_status = 'available'
        """, (listing_id,))
        l = cursor.fetchone()

        if not l:
            return jsonify({"success": False, "listing": None}), 404

        property_id = l["property_id"]
        landlord_user_id = l["user_id"]

        # 2️⃣ Fetch listing images
        cursor.execute("""
            SELECT image_url
            FROM images
            WHERE listing_id = %s
            ORDER BY uploaded_at ASC
        """, (listing_id,))
        images = [row["image_url"] for row in cursor.fetchall()]

        # 3️⃣ Fetch landlord image
        cursor.execute("""
            SELECT image_url
            FROM images
            WHERE user_id = %s
            ORDER BY uploaded_at DESC
            LIMIT 1
        """, (landlord_user_id,))
        landlord_img_row = cursor.fetchone()
        landlord_image = landlord_img_row["image_url"] if landlord_img_row else None

        # 4️⃣ Fetch location (same logic as fetch_listings)
        cursor.execute("""
            SELECT *
            FROM Location_data
            WHERE listing_id = %s OR property_id = %s
            LIMIT 1
        """, (listing_id, property_id))
        loc = cursor.fetchone()

        location_obj = None
        location_str = None

        if loc:
            location_obj = {
                "latitude": float(loc["latitude"]),
                "longitude": float(loc["longitude"]),
                "address": loc.get("address")
            }
            location_str = loc.get("address")

        # 5️⃣ Compute distance
        distance_meters = None
        distance_str = None

        if user_lat is not None and user_lon is not None and location_obj:
            dist = haversine_distance(
                float(user_lat), float(user_lon),
                location_obj["latitude"], location_obj["longitude"]
            )
            distance_meters = dist

            if dist < 1000:
                distance_str = f"{dist} m"
            else:
                km = dist / 1000
                distance_str = f"{round(km, 2)} km"

        # 6️⃣ Fetch amenities (SAME as fetch_listings)
        cursor.execute("""
            SELECT a.amenity_key, a.label
            FROM listings_amenities la
            JOIN amenities a ON la.amenity_id = a.id
            WHERE la.listing_id = %s
        """, (listing_id,))
        amenities_raw = cursor.fetchall()

        amenities = [
            {
                "name": a["label"],
                "key": a["amenity_key"],
                "available": True
            }
            for a in amenities_raw
        ]

        # 7️⃣ Fetch reviews + users
        cursor.execute("""
            SELECT r.*, u.username
            FROM reviews r
            LEFT JOIN users u ON r.user_id = u.user_id
            WHERE r.listing_id = %s
            ORDER BY r.review_date DESC
        """, (listing_id,))
        reviews_raw = cursor.fetchall()

        reviews_list = []

        for r in reviews_raw:
            # reviewer image
            cursor.execute("""
                SELECT image_url
                FROM images
                WHERE user_id = %s
                ORDER BY uploaded_at DESC
                LIMIT 1
            """, (r["user_id"],))
            reviewer_img = cursor.fetchone()

            reviews_list.append({
                "id": r["id"],
                "author": r.get("username") or "Anonymous",
                "avatar": reviewer_img["image_url"] if reviewer_img else None,
                "rating": int(r["rating"]),
                "date": r["review_date"].isoformat() if r.get("review_date") else None,
                "comment": r["review_text"]
            })

        if reviews_list:
            avg_rating = round(sum(r["rating"] for r in reviews_list) / len(reviews_list), 2)
            reviews_count = len(reviews_list)
        else:
            avg_rating = 0
            reviews_count = 0

        # 8️⃣ Fetch landlord info
        cursor.execute("""
            SELECT u.username, u.created_at
            FROM users u
            WHERE u.user_id = %s
        """, (landlord_user_id,))
        landlord_user = cursor.fetchone()

        cursor.execute("""
            SELECT full_name
            FROM security_checks
            WHERE user_id = %s AND check_type = 'landlord' AND status = 'verified'
            ORDER BY performed_at DESC
            LIMIT 1
        """, (landlord_user_id,))
        sec = cursor.fetchone()

        # properties count
        cursor.execute("""
            SELECT COUNT(*) AS cnt
            FROM properties_data
            WHERE user_id = %s
        """, (landlord_user_id,))
        prop_cnt = cursor.fetchone()
        properties_count = int(prop_cnt["cnt"]) if prop_cnt else 0

        landlord_name = sec["full_name"] if sec and sec.get("full_name") else landlord_user.get("username")

        landlord = {
            "name": landlord_name,
            "image": landlord_image,
            "responseRate": "98%",           # fixed for now
            "responseTime": "within 2 hours",
            "memberSince": str(landlord_user["created_at"].year) if landlord_user and landlord_user.get("created_at") else None,
            "properties": properties_count
        }

        # 9️⃣ Parse deposits JSON
        deposit = None
        if l.get("deposits"):
            try:
                if isinstance(l["deposits"], str):
                    deposit = json.loads(l["deposits"])
                else:
                    deposit = l["deposits"]
            except:
                deposit = l["deposits"]

        # 🔟 Build FINAL FRONTEND-READY OBJECT
        mapped = {
            "title": l["listing_name"],
            "type": l["listing_type"].capitalize() if l.get("listing_type") else None,
            "price": float(l["price"]) if isinstance(l["price"], Decimal) else float(l["price"]),
            "deposit": deposit,

            "location": location_str,
            "distance": distance_str,

            "size": l.get("room_size"),
            "maxOccupants": l.get("max_occupants"),
            "availableFrom": l["availability_date"].isoformat() if l.get("availability_date") else "Immediately",

            "images": images,
            "amenities": amenities,

            "description": l.get("listing_description"),
            "verified": bool(l.get("verified")),

            "rating": avg_rating,
            "reviews": reviews_count,

            "landlord": landlord,
            "reviewsList": reviews_list
        }

        # 🔍 Debug
        print("FULL LISTING DETAILS:", json.dumps(mapped, indent=2, default=str))

        return jsonify({
            "success": True,
            "listing": mapped
        }), 200

    except Exception as e:
        print(f"[ERROR] fetch_listing_details: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
