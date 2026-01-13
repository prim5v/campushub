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
import json


from ...utils.db_connection import get_db

def get_plan_details(plan_id):
    db = get_db()
    cursor = db.cursor()
    try:
        sql = "SELECT * FROM plan_data WHERE id = %s"
        cursor.execute(sql, (plan_id,))
        row = cursor.fetchone()

        if not row:
            return jsonify({"error": "Plan not found"}), 404
        
                # 🔹 Convert JSON fields to Python lists
        features = json.loads(row["features"]) if row["features"] else []
        not_included = json.loads(row["not_included"]) if row["not_included"] else []

        plan = {
            "id": row["id"],
            "name": row["name"],
            "price": row["price"],
            "period": row["period"],
            "description": row["description"],
            "features": features,    # JSON
            "notIncluded": not_included,
            "popular": row["popular"]
        }
        
        

        return jsonify({"plan": plan}), 200

    except Exception as e:
        print(f"[ERROR] get_plan_details: {e}")
        return jsonify({"error": str(e)}), 500