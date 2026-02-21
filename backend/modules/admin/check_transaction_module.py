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

def fetch_check_transaction():
    db = get_db()
    cursor = db.cursor(pymysql.cursors.DictCursor)

    try:
        data = request.get_json()

        transaction_id = data.get("transaction_id")
        property_id = data.get("property_id")

        # -----------------------------
        # Validation
        # -----------------------------
        if not transaction_id or not property_id:
            return jsonify({
                "error": "transaction_id and property_id are required"
            }), 400

        # -----------------------------
        # 1️⃣ Check Transaction Exists
        # -----------------------------
        transaction_sql = """
            SELECT *
            FROM transactions
            WHERE transaction_id = %s
        """
        cursor.execute(transaction_sql, (transaction_id,))
        transaction = cursor.fetchone()

        if not transaction:
            return jsonify({
                "error": "Transaction not found"
            }), 404

        # -----------------------------
        # 2️⃣ Check Transaction Status
        # -----------------------------
        if transaction["status"] != "completed":
            return jsonify({
                "error": "Transaction not completed",
                "transaction_status": transaction["status"]
            }), 400

        # -----------------------------
        # 3️⃣ Check Property Exists
        # -----------------------------
        property_sql = """
            SELECT verified
            FROM properties_data
            WHERE property_id = %s
        """
        cursor.execute(property_sql, (property_id,))
        property_row = cursor.fetchone()

        if not property_row:
            return jsonify({
                "error": "Property not found"
            }), 404

        # -----------------------------
        # 4️⃣ Prevent Double Verification
        # -----------------------------
        if property_row["verified"] == 1:
            return jsonify({
                "message": "Property already verified"
            }), 200

        # -----------------------------
        # 5️⃣ Verify Property
        # -----------------------------
        update_sql = """
            UPDATE properties_data
            SET verified = 1
            WHERE property_id = %s
        """
        cursor.execute(update_sql, (property_id,))
        db.commit()

        return jsonify({
            "message": "Property verified successfully",
            "transaction_id": transaction_id,
            "property_id": property_id
        }), 200

    except Exception as e:
        db.rollback()
        return jsonify({
            "error": str(e)
        }), 500