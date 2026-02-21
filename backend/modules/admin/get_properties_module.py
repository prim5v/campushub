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
import psutil
import secrets

from flask import jsonify
from ...utils.db_connection import get_db

def fetch_properties():
    db = get_db()
    cursor = db.cursor(pymysql.cursors.DictCursor)

    try:
        # Main query to get property info, landlord, listing count, and location
        query = """
            SELECT 
                p.property_id,
                p.property_name,
                u.username AS landlord_name,
                u.is_active,
                CASE WHEN p.verified = 1 THEN 'verified' ELSE 'unverified' END AS verification_status,
                IFNULL(l.listing_count, 0) AS listing_count,
                ld.address,
                ld.latitude,
                ld.longitude
            FROM properties_data p
            LEFT JOIN users u ON p.user_id = u.user_id
            LEFT JOIN (
                SELECT property_id, COUNT(*) AS listing_count
                FROM listings_data
                GROUP BY property_id
            ) l ON p.property_id = l.property_id
            LEFT JOIN Location_data ld ON p.property_id = ld.property_id
            ORDER BY p.listed_at DESC
        """
        cursor.execute(query)
        properties = cursor.fetchall()

        # Base URL for images
        base_url = request.host_url.rstrip("/") + "/static/images/"

        # For each property, fetch associated images
        for prop in properties:
            # Human-readable account status
            prop["account_status"] = "active" if prop["is_active"] else "inactive"
            del prop["is_active"]

            # Get images
            image_query = """
                SELECT image_url
                FROM images
                WHERE property_id = %s
            """
            cursor.execute(image_query, (prop["property_id"],))
            images = cursor.fetchall()
            # Return as list of full URLs
            prop["images"] = [base_url + img["image_url"] for img in images]

        return jsonify({"count": len(properties), "properties": properties}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500