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

def edit_listing(listing_id, data):
    try:
        conn = get_db()
        cursor = conn.cursor()

        allowed_fields = [
            "listing_name",
            "listing_description",
            "listing_type",
            "price",
            "renting_price",
            "timeline",
            "availability_status",
            "availability_date",
            "room_size",
            "max_occupants",
            "deposits"
        ]

        updates = []
        values = []

        for field in allowed_fields:
            if field in data:
                updates.append(f"{field} = %s")
                values.append(data[field])

        if not updates:
            return jsonify({"error": "No valid fields to update"}), 400

        values.append(listing_id)

        sql = f"""
            UPDATE listings_data
            SET {", ".join(updates)}
            WHERE listing_id = %s
        """

        cursor.execute(sql, values)
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Listing not found"}), 404

        return jsonify({
            "status": "success",
            "message": "Listing updated successfully"
        }), 200

    except Exception as e:
        logger.error(f"edit_listing error: {e}", exc_info=True)
        return jsonify({"error": "internal server error"}), 500