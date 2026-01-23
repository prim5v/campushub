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
import math

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Returns distance in METERS between two coordinates.
    """
    R = 6371000  # Earth radius in meters

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2) ** 2 +
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return int(R * c)  # return meters (integer)


def fetch_listings(data):
    coordinates = data.get("coordinates")  # { latitude, longitude }
    user_lat = coordinates.get("latitude") if coordinates else None
    user_lon = coordinates.get("longitude") if coordinates else None

    db = get_db()
    cursor = db.cursor(pymysql.cursors.DictCursor)

    try:
        # 1️⃣ Fetch only available listings + property verified
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
        property_ids = [listing["property_id"] for listing in listings]

        format_strings = ",".join(["%s"] * len(listing_ids))
        property_strings = ",".join(["%s"] * len(property_ids))

        # 2️⃣ Fetch all images
        cursor.execute(
            f"SELECT listing_id, image_url FROM images WHERE listing_id IN ({format_strings})",
            listing_ids
        )
        images = cursor.fetchall()

        images_map = {}
        for img in images:
            images_map.setdefault(img["listing_id"], []).append(img["image_url"])

        # 3️⃣ Fetch all locations
        cursor.execute(
            f"""
            SELECT *
            FROM location_data
            WHERE listing_id IN ({format_strings})
            OR property_id IN ({property_strings})
            """,
            listing_ids + property_ids
        )
        locations = cursor.fetchall()

        location_map = {}
        for loc in locations:
            key = loc["listing_id"] if loc["listing_id"] else loc["property_id"]
            location_map[key] = {
                "latitude": float(loc["latitude"]),
                "longitude": float(loc["longitude"]),
                "address": loc.get("address")
            }

        # 4️⃣ Fetch reviews
        cursor.execute(
            f"SELECT listing_id, rating FROM reviews WHERE listing_id IN ({format_strings})",
            listing_ids
        )
        reviews = cursor.fetchall()

        ratings_map = {}
        for listing_id in listing_ids:
            rs = [r["rating"] for r in reviews if r["listing_id"] == listing_id]
            if rs:
                ratings_map[listing_id] = {
                    "average_rating": round(sum(rs) / len(rs), 2),
                    "num_ratings": len(rs)
                }
            else:
                ratings_map[listing_id] = {"average_rating": 0, "num_ratings": 0}

        # 5️⃣ Fetch amenities
        cursor.execute(
            f"""
            SELECT la.listing_id, a.amenity_key, a.label
            FROM listings_amenities la
            JOIN amenities a ON la.amenity_id = a.id
            WHERE la.listing_id IN ({format_strings})
        """,
            listing_ids
        )
        amenities = cursor.fetchall()

        amenities_map = {}
        for a in amenities:
            amenities_map.setdefault(a["listing_id"], []).append({
                "key": a["amenity_key"],
                "label": a["label"]
            })

        # 6️⃣ Attach everything + compute distance
        for listing in listings:
            listing_id = listing["listing_id"]
            property_id = listing["property_id"]

            location = location_map.get(listing_id) or location_map.get(property_id)

            listing["images"] = images_map.get(listing_id, [])
            listing["location"] = location or {}
            listing["rating"] = ratings_map.get(listing_id, {"average_rating": 0, "num_ratings": 0})
            listing["amenities"] = amenities_map.get(listing_id, [])
            listing["verified"] = bool(listing.get("verified", False))

            # 📏 Distance calculation
            if user_lat is not None and user_lon is not None and location:
                dist = haversine_distance(
                    user_lat, user_lon,
                    location["latitude"], location["longitude"]
                )
                listing["distance"] = dist  # meters
            else:
                listing["distance"] = None

        # 7️⃣ Sort by distance (nearest first)
        listings.sort(key=lambda x: x["distance"] if x["distance"] is not None else 10**18)

        return jsonify({"listings": listings}), 200

    except Exception as e:
        print(f"[ERROR] Exception occurred: {e}")
        return jsonify({"error": str(e)}), 500
