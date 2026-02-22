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

import json
import logging
from flask import jsonify
from ...utils.db_connection import get_db

logger = logging.getLogger(__name__)

def get_listings():
    logger.info("get_listings called")

    db = get_db()
    cursor = db.cursor(pymysql.cursors.DictCursor)

    try:
        query = """
            SELECT
                l.listing_id,
                p.property_name,
                l.listing_name AS unit,
                l.listing_type,
                l.price,
                l.timeline,
                l.availability_status,
                l.availability_date,
                u.username,
                u.is_active
            FROM listings_data l
            LEFT JOIN properties_data p ON l.property_id = p.property_id
            LEFT JOIN users u ON l.user_id = u.user_id
            ORDER BY l.listed_at DESC
        """

        cursor.execute(query)
        rows = cursor.fetchall()

        listings = []

        for row in rows:
            listings.append({
                "listing_id": row["listing_id"],
                "property_name": row["property_name"],
                "unit": row["unit"],
                "type": row["listing_type"],
                "price": float(row["price"]) if row["price"] else None,
                "timeline": row["timeline"],
                "availability": row["availability_status"],
                "availability_date": row["availability_date"],
                "landlord_username": row["username"],
                "status": "active" if row["is_active"] else "inactive"
            })

        return jsonify({
            "count": len(listings),
            "listings": listings
        }), 200

    except Exception as e:
        logger.error(f"get_listings error: {e}", exc_info=True)
        return jsonify({"error": "internal server error"}), 500