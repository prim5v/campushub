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

def fetch_properties(current_user_id, role):
    db = get_db()
    cursor = db.cursor()

    try:
        sql = """
            SELECT 
                p.*,
                l.address,
                l.latitude,
                l.longitude
            FROM properties_data p
            LEFT JOIN location_data l 
                ON p.property_id = l.property_id
            WHERE p.user_id = %s
        """
        cursor.execute(sql, (current_user_id,))
        properties = cursor.fetchall()

        if not properties:
            return jsonify({"properties": []}), 200

        # Fetch images
        property_ids = [p["property_id"] for p in properties]

        fetch_images_sql = """
            SELECT property_id, image_url
            FROM images
            WHERE property_id IN (%s)
        """ % ",".join(["%s"] * len(property_ids))

        cursor.execute(fetch_images_sql, property_ids)
        images = cursor.fetchall()

        images_map = {}
        for img in images:
            images_map.setdefault(img["property_id"], []).append(img["image_url"])

        for prop in properties:
            prop["images"] = images_map.get(prop["property_id"], [])

        return jsonify({"properties": properties}), 200

    except Exception as e:
        print(f"[ERROR] {e}")
        return jsonify({"error": str(e)}), 500

# {
#   "properties": [
#     {
#       "id": 1,
#       "property_id": "a8f3c21b9d42",
#       "user_id": "u123456",
#       "amenities": ["wifi", "parking", "water"],
#       "verified": false,
#       "property_name": "Sunset Apartments",
#       "property_description": "Modern bedsitters near Sarit Centre",
#       "property_type": "bedsitter",
#       "listed_at": "2026-01-10 14:22:11",

#       "address": "Westlands, Nairobi",
#       "latitude": -1.268452,
#       "longitude": 36.811923,

#       "images": [
#         "b3f21c_img1.jpg",
#         "a72dd_img2.jpg",
#         "9f1aa_img3.jpg"
#       ]
#     },
#     {
#       "id": 2,
#       "property_id": "f91ab72e1c33",
#       "user_id": "u123456",
#       "amenities": ["security", "balcony"],
#       "verified": true,
#       "property_name": "GreenVille Hostel",
#       "property_description": "Affordable student hostel near campus",
#       "property_type": "hostel",
#       "listed_at": "2026-01-03 09:11:45",

#       "address": "Kasarani, Nairobi",
#       "latitude": -1.221003,
#       "longitude": 36.897210,

#       "images": [
#         "c1a92_hostel1.jpg",
#         "d9912_hostel2.jpg"
#       ]
#     }
#   ]
# }

