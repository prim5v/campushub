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


# from ...utils.db_connection import get_db

# import logging


# logger = logging.getLogger(__name__)


import json
import logging
from flask import jsonify
from ...utils.db_connection import get_db
from ...utils.paymentGateways import trigger_mpesa_stk

logger = logging.getLogger(__name__)

def get_requests_and_bookings():
    try:
        db = get_db()
        cursor = db.cursor(pymysql.cursors.DictCursor)

        # =========================
        # REQUESTS (ENRICHED)
        # =========================
        cursor.execute("""
            SELECT 
                r.*,

                -- Requestor
                u.username AS requestor_username,
                u.email AS requestor_email,
                u.phone AS requestor_phone,
                u.role AS requestor_role,
                u.is_active AS requestor_active,

                -- Listing
                l.listing_name,
                l.listing_description,
                l.price AS listing_price,
                l.renting_price,
                l.deposits,
                l.listing_type,
                l.availability_status,

                -- Property
                p.property_name,
                p.property_description,
                p.property_type,
                p.amenities,
                p.verified AS property_verified,

                -- Location
                loc.latitude,
                loc.longitude,
                loc.address,

                -- Landlord user
                landlord.username AS landlord_username,
                landlord.email AS landlord_email,
                landlord.phone AS landlord_phone,
                landlord.role AS landlord_role,

                -- Latest landlord security check
                sc.id_number AS landlord_id_number,
                sc.full_name AS landlord_full_name,
                sc.status AS landlord_verification_status,
                sc.reviewed_by AS landlord_reviewed_by,
                sc.review_notes AS landlord_review_notes,
                sc.performed_at AS landlord_performed_at

            FROM requests r

            LEFT JOIN users u 
                ON r.user_id = u.user_id

            LEFT JOIN listings_data l 
                ON r.listing_id = l.listing_id

            LEFT JOIN properties_data p 
                ON l.property_id = p.property_id

            LEFT JOIN users landlord 
                ON p.user_id = landlord.user_id

            LEFT JOIN Location_data loc 
                ON l.listing_id = loc.listing_id

            LEFT JOIN (
                SELECT s1.*
                FROM security_checks s1
                WHERE s1.check_type = 'landlord'
                AND s1.performed_at = (
                    SELECT MAX(s2.performed_at)
                    FROM security_checks s2
                    WHERE s2.user_id = s1.user_id
                    AND s2.check_type = 'landlord'
                )
            ) sc 
                ON landlord.user_id = sc.user_id

            ORDER BY r.requested_at DESC
        """)

        requests_rows = cursor.fetchall()

        # =========================
        # BOOKINGS (ENRICHED)
        # =========================
        cursor.execute("""
            SELECT 
                b.*,

                -- Tenant
                u.username AS tenant_username,
                u.email AS tenant_email,
                u.phone AS tenant_phone,
                u.role AS tenant_role,
                u.is_active AS tenant_active,

                -- Listing
                l.listing_name,
                l.listing_description,
                l.price AS listing_price,
                l.renting_price,
                l.deposits,
                l.listing_type,
                l.availability_status,

                -- Property
                p.property_name,
                p.property_description,
                p.property_type,
                p.amenities,
                p.verified AS property_verified,

                -- Location
                loc.latitude,
                loc.longitude,
                loc.address,

                -- Landlord user
                landlord.username AS landlord_username,
                landlord.email AS landlord_email,
                landlord.phone AS landlord_phone,
                landlord.role AS landlord_role,

                -- Latest landlord security check
                sc.id_number AS landlord_id_number,
                sc.full_name AS landlord_full_name,
                sc.status AS landlord_verification_status,
                sc.reviewed_by AS landlord_reviewed_by,
                sc.review_notes AS landlord_review_notes,
                sc.performed_at AS landlord_performed_at

            FROM bookings b

            LEFT JOIN users u 
                ON b.user_id = u.user_id

            LEFT JOIN listings_data l 
                ON b.listing_id = l.listing_id

            LEFT JOIN properties_data p 
                ON l.property_id = p.property_id

            LEFT JOIN users landlord 
                ON p.user_id = landlord.user_id

            LEFT JOIN Location_data loc 
                ON l.listing_id = loc.listing_id

            LEFT JOIN (
                SELECT s1.*
                FROM security_checks s1
                WHERE s1.check_type = 'landlord'
                AND s1.performed_at = (
                    SELECT MAX(s2.performed_at)
                    FROM security_checks s2
                    WHERE s2.user_id = s1.user_id
                    AND s2.check_type = 'landlord'
                )
            ) sc 
                ON landlord.user_id = sc.user_id

            ORDER BY b.booked_at DESC
        """)

        bookings_rows = cursor.fetchall()

        cursor.close()
        db.close()

        return jsonify({
            "status": "success",
            "data": {
                "requests": requests_rows,
                "bookings": bookings_rows
            }
        }), 200

    except Exception as e:
        logger.exception("🔥 Failed to fetch enriched requests/bookings")
        return jsonify({
            "status": "error",
            "message": str(e)  # temporary for debugging
        }), 500
    
# def get_requests_and_bookings():
#     try:
#         db = get_db()
#         cursor = db.cursor()

#         # -------------------------
#         # Fetch requests
#         # -------------------------
#         cursor.execute("SELECT * FROM requests ORDER BY requested_at DESC")
#         requests_rows = cursor.fetchall()

#         # -------------------------
#         # Fetch bookings
#         # -------------------------
#         cursor.execute("SELECT * FROM bookings ORDER BY booked_at DESC")
#         bookings_rows = cursor.fetchall()

#         cursor.close()
#         db.close()

#         # -------------------------
#         # Return JSON
#         # -------------------------
#         return jsonify({
#             "status": "success",
#             "data": {
#                 "requests": requests_rows,
#                 "bookings": bookings_rows
#             }
#         }), 200

#     except Exception as e:
#         logger.exception("🔥 Failed to fetch requests/bookings")
#         return jsonify({
#             "status": "error",
#             "message": "Could not fetch data"
#         }), 500