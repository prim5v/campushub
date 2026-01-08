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

def fetch_edit_property(current_user_id, role):
    db = get_db()
    cursor = db.cursor()

    data = request.get_json()

    property_id = data.get("property_id")
    property_name = data.get("property_name")
    property_description = data.get("property_description")
    property_type = data.get("property_type")

    if not property_id:
        return jsonify({"error": "property_id is required"}), 400

    try:
        editsql = """
            UPDATE properties
            SET
                property_name = %s,
                property_description = %s,
                property_type = %s
            WHERE property_id = %s AND user_id = %s
        """

        cursor.execute(
            editsql,
            (
                property_name,
                property_description,
                property_type,
                property_id,
                current_user_id
            )
        )

        db.commit()

        if cursor.rowcount == 0:
            return jsonify({
                "error": "Property not found or not authorized"
            }), 404

        return jsonify({
            "status": "success",
            "message": "Property updated successfully"
        }), 200

    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500


