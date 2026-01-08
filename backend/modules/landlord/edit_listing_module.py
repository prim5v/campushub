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

def fetch_edit_listing(current_user_id, role):
    db = get_db()
    cursor = db.cursor()

    data = request.get_json()

    listing_id = data.get("listing_id")
    listing_name = data.get("listing_name")
    listing_description = data.get("listing_description")
    listing_type = data.get("listing_type")
    price = data.get("price")

    if not listing_id:
        return jsonify({"error": "listing_id is required"}), 400

    try:
        editsql = """
            UPDATE listings
            SET
                listing_name = %s,
                listing_description = %s,
                listing_type = %s,
                price = %s
            WHERE listing_id = %s AND user_id = %s
        """

        cursor.execute(
            editsql,
            (
                listing_name,
                listing_description,
                listing_type,
                price,
                listing_id,
                current_user_id,
            ),
        )
        db.commit()

        if cursor.rowcount == 0:
            return jsonify({
                "error": "listing not found or not authorized"
            }), 404

        return jsonify({
            "status": "success",
            "message": "Listing updated successfully"
        }), 200
    
    
    except Exception as e:
        print(f"[ERROR] Exception occurred: {e}")
        return jsonify({"error": str(e)}), 500