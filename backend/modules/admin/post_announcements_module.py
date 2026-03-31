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
import logging
from flask import jsonify
from ...utils.db_connection import get_db

logger = logging.getLogger(__name__)

def post_announcement(data):
    try:
        logger.info("📦 Post Announcement request received")

        audience = data.get("audience")
        title = data.get("title")
        message = data.get("message")

        if not audience or not title or not message:
            logger.warning("❌ Missing required fields: audience, title, or message")
            return jsonify({"error": "missing required fields: audience, title, or message"}), 400

        db = get_db()
        cursor = db.cursor(pymysql.cursors.DictCursor)

        insert_query = """
            INSERT INTO announcements (audience, title, message)
            VALUES (%s, %s, %s)
        """
        cursor.execute(insert_query, (audience, title, message))
        db.commit()

        logger.info("✅ Announcement posted successfully")
        return jsonify({"message": "Announcement posted successfully"}), 201

    except Exception as e:
        logger.error(f"❌ Error posting announcement: {str(e)}")
        return jsonify({"error": "An error occurred while posting the announcement"}), 500