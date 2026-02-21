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

def fetch_recent_system_activity():
    db = get_db()
    cursor = db.cursor()

    try:
        activities = []

        # ---------------- USERS ----------------
        cursor.execute("""
            SELECT user_id, username, created_at
            FROM users
            ORDER BY created_at DESC
            LIMIT 10
        """)
        users = cursor.fetchall()

        for u in users:
            activities.append({
                "type": "user_registered",
                "title": "New User Registration",
                "description": f"{u['username']} created an account",
                "user_id": u["user_id"],
                "timestamp": u["created_at"]
            })

        # ---------------- LISTINGS ----------------
        cursor.execute("""
            SELECT listing_id, listing_name, user_id, listed_at
            FROM listings_data
            ORDER BY listed_at DESC
            LIMIT 10
        """)
        listings = cursor.fetchall()

        for l in listings:
            activities.append({
                "type": "listing_created",
                "title": "New Listing Created",
                "description": l["listing_name"],
                "user_id": l["user_id"],
                "timestamp": l["listed_at"]
            })

        # ---------------- TRANSACTIONS ----------------
        cursor.execute("""
            SELECT user_id, amount, transaction_date
            FROM transactions
            ORDER BY transaction_date DESC
            LIMIT 10
        """)
        txs = cursor.fetchall()

        for t in txs:
            activities.append({
                "type": "payment_completed",
                "title": "Payment Processed",
                "description": f"Payment of {float(t['amount'])}",
                "user_id": t["user_id"],
                "timestamp": t["transaction_date"]
            })

        # ---------------- VERIFICATIONS ----------------
        cursor.execute("""
            SELECT user_id, status, performed_at
            FROM security_checks
            ORDER BY performed_at DESC
            LIMIT 10
        """)
        checks = cursor.fetchall()

        for c in checks:
            activities.append({
                "type": "verification_update",
                "title": "Verification Update",
                "description": f"Status changed to {c['status']}",
                "user_id": c["user_id"],
                "timestamp": c["performed_at"]
            })

        # ---------------- SORT + LIMIT GLOBAL ----------------
        activities.sort(key=lambda x: x["timestamp"], reverse=True)
        activities = activities[:20]

        return jsonify({
            "count": len(activities),
            "activities": activities
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500