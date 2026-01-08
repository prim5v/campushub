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
        # 1️⃣ Fetch properties
        fetch_properties_sql = """
            SELECT *
            FROM properties
            WHERE user_id = %s
        """
        cursor.execute(fetch_properties_sql, (current_user_id,))
        properties = cursor.fetchall()

        if not properties:
            return jsonify({"properties": []}), 200

        # 2️⃣ Collect property_ids
        property_ids = [prop["property_id"] for prop in properties]

        # 3️⃣ Fetch images for those properties
        fetch_images_sql = """
            SELECT property_id, image_url
            FROM images
            WHERE property_id IN (%s)
        """ % ",".join(["%s"] * len(property_ids))

        cursor.execute(fetch_images_sql, property_ids)
        images = cursor.fetchall()

        # 4️⃣ Group images by property_id
        images_map = {}
        for img in images:
            images_map.setdefault(img["property_id"], []).append(img["image_url"])

        # 5️⃣ Attach images to properties
        for prop in properties:
            prop["images"] = images_map.get(prop["property_id"], [])

        return jsonify({"properties": properties}), 200

    except Exception as e:
        print(f"[ERROR] Exception occurred: {e}")
        return jsonify({"error": str(e)}), 500

