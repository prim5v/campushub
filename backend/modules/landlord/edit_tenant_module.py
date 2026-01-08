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

def fetch_edit_tenant(current_user_id, role):
    db = get_db()
    cursor = db.cursor()

    data = request.get_json()

    tenant_id = data.get("tenant_id")
    tenant_name = data.get("tenant_name")
    tenant_email = data.get("tenant_email")
    tenant_phone = data.get("tenant_phone")

    if not tenant_id:
        return jsonify({"error": "tenant_id is required"}), 400

    try:
        editsql = """
            UPDATE tenants_data
            SET
                tenant_name = %s,
                tenant_email = %s,
                tenant_phone = %s
            WHERE tenant_id = %s
        """

        cursor.execute(
            editsql,
            (
                tenant_name,
                tenant_email,
                tenant_phone,
                tenant_id
            )
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