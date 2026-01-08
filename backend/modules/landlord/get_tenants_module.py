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

def fetch_tenants(current_user_id, role):
    db = get_db()
    cursor = db.cursor()

    try:
        # 1️⃣ Fetch tenants + listing + property info
        fetch_tenants_sql = """
            SELECT
                -- Tenant info
                t.tenant_id,
                t.user_id AS tenant_user_id,
                t.tenant_name,
                t.tenant_email,
                t.tenant_phone,
                t.lease_start_date,
                t.lease_end_date,
                t.rent_amount,
                t.payment_schedule,
                t.created_at AS tenant_created_at,

                -- Listing info
                l.listing_id,
                l.listing_name,
                l.listing_description,
                l.listing_type,
                l.price AS listing_price,
                l.renting_price,
                l.timeline,
                l.availability_status,

                -- Property info
                p.property_id,
                p.property_name,
                p.property_description,
                p.property_type

            FROM Tenants_data t
            JOIN listings_data l ON t.listing_id = l.listing_id
            JOIN properties_data p ON l.property_id = p.property_id
            WHERE p.user_id = %s
            ORDER BY t.created_at DESC
        """

        cursor.execute(fetch_tenants_sql, (current_user_id,))
        tenants = cursor.fetchall()

        # ✅ Count tenants
        tenants_count = len(tenants)

        if not tenants:
            return jsonify({
                "tenants": [],
                "tenants_count": 0
            }), 200

        # 2️⃣ Collect tenant_ids
        tenant_ids = [t["tenant_id"] for t in tenants]

        # 3️⃣ Fetch tenant images
        fetch_images_sql = """
            SELECT tenant_id, image_url
            FROM images
            WHERE tenant_id IN (%s)
        """ % ",".join(["%s"] * len(tenant_ids))

        cursor.execute(fetch_images_sql, tenant_ids)
        images = cursor.fetchall()

        # 4️⃣ Group images by tenant_id
        images_map = {}
        for img in images:
            images_map.setdefault(img["tenant_id"], []).append(img["image_url"])

        # 5️⃣ Attach images to tenants
        for tenant in tenants:
            tenant["images"] = images_map.get(tenant["tenant_id"], [])

        return jsonify({
            "tenants": tenants,
            "tenants_count": tenants_count
        }), 200

    except Exception as e:
        logging.error(f"Error fetching tenants: {e}")
        return jsonify({"error": "Internal server error"}), 500



