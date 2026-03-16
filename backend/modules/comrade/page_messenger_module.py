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


from ...utils.db_connection import get_db

def send_page_messenger():
    try:
        db = get_db()
        cursor = db.cursor()

        data = request.get_json(silent=True) or request.form
        page_name = data.get("page_name")
        user = data.get("user")
        page_id = request.cookies.get("page_id")
        

        # Validate input
        if not page_name:
            return jsonify({"error": "page_name is required"}), 400

        # Generate page_id if missing
        if not page_id:
            page_id = uuid.uuid4().hex[:12]
        
        if not user:
            user = "anonymous"

        insert_query = """
            INSERT INTO page_time (page_id, page_name, user)
            VALUES (%s, %s, %s)
        """

        try:
            cursor.execute(insert_query, (page_id, page_name, user))
            db.commit()
        except pymysql.MySQLError as db_err:
            logging.error(f"Database error: {db_err}")
            db.rollback()
            return jsonify({"error": "Database error occurred"}), 500

        # Create response
        resp = make_response(jsonify({
            "status": "success"
            # "page_id": page_id
        }))

        resp.set_cookie(
            "page_id",
            page_id,
            httponly=True,
            secure=True,
            samesite="None",
            path="/"
        )

        return resp

    except Exception as e:
        logging.error(f"Unexpected error in send_page_messenger: {str(e)}")
        return jsonify({
            "error": "Internal server error"
        }), 500



