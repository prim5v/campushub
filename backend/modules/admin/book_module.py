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



def make_booking():
    data = request.get_json() or request.form

    listing_id = data.get("listing_id")
    phone = data.get("phone")
    amount = data.get("amount")
    user_id = data.get("user_id")
    request_id = data.get("request_id")  # <-- Make sure frontend sends this

    # --- Validation ---
    if not listing_id or not phone or not amount or not request_id:
        return jsonify({"error": "All fields are required"}), 400

    try:
        amount = int(amount)
        if amount <= 0:
            return jsonify({"error": "Invalid amount"}), 400
    except ValueError:
        return jsonify({"error": "Amount must be a number"}), 400

    # --- Generate booking ID ---
    booking_id = f"BK-{uuid.uuid4().hex[:12].upper()}"

    payment_status = "pending"
    booking_status = "initiated"

    conn = get_db()
    cursor = conn.cursor()

    try:
        # --- Insert into bookings ---
        cursor.execute("""
            INSERT INTO bookings 
            (booking_id, listing_id, user_id, phone_number, amount, payment_status, booking_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            booking_id,
            listing_id,
            user_id,
            phone,
            amount,
            payment_status,
            booking_status
        ))

        # --- Update request status ---
        cursor.execute("""
            UPDATE requests
            SET status = 'booked'
            WHERE request_id = %s
        """, (request_id,))

        conn.commit()

        return jsonify({
            "message": "Booking created successfully",
            "booking_id": booking_id,
            "payment_status": payment_status,
            "booking_status": booking_status
        }), 201

    except Exception as e:
        conn.rollback()
        logger.error(f"Booking creation failed: {e}")
        return jsonify({"error": "Failed to create booking"}), 500