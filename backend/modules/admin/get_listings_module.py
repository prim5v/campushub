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

from flask import jsonify
from ...utils.db_connection import get_db

def fetch_all_listings():
    db = get_db()
    cursor = db.cursor()

    try:
        sql = """
            SELECT
                l.listing_id,
                l.listing_name,
                l.listing_description,
                l.listing_type,
                l.price,
                l.timeline,
                l.availability_status,
                l.listed_at,

                u.user_id AS uploader_id,
                u.username AS uploader_username,
                u.email AS uploader_email,
                u.phone AS uploader_phone,
                u.role AS uploader_role
            FROM listings_data l
            JOIN users u
                ON l.user_id = u.user_id
            ORDER BY l.listed_at DESC
        """

        cursor.execute(sql)
        listings = cursor.fetchall()

        return jsonify({
            "count": len(listings),
            "listings": listings
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
