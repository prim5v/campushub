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
import os
import json


from ...utils.db_connection import get_db

def fetch_add_transaction(current_user_id, role):
    db = get_db()
    cursor = db.cursor()

    data = request.get_json()

    title = data.get("title")
    category = data.get("category")
    transaction_type = data.get("transaction_type")
    amount = data.get("amount")
    payment_method = data.get("payment_method")
    mpesa_code = data.get("mpesa_code")
    paid_by = data.get("paid_by")  # expecting a dict
    paid_to = data.get("paid_to")  # expecting a dict
    status = data.get("status", "pending")

    if not all([title, category, transaction_type, amount, payment_method]):
        return jsonify({"error": "Missing required fields"}), 400

    transaction_id = str(uuid.uuid4())

    try:
        insertsql = """
            INSERT INTO transactions (
                transaction_id, paid_by, paid_to, title, category,
                transaction_type, amount, payment_method, mpesa_code, status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        cursor.execute(
            insertsql,
            (
                transaction_id,
                json.dumps(paid_by),
                json.dumps(paid_to),
                title,
                category,
                transaction_type,
                amount,
                payment_method,
                mpesa_code,
                status
            )
        )

        db.commit()

        return jsonify({"message": "Transaction added successfully", 
                        "transaction_id": transaction_id
                        }), 201

    except Exception as e:
        db.rollback()
        logging.error(f"Error adding transaction: {e}")
        return jsonify({"error": "Failed to add transaction"}), 500