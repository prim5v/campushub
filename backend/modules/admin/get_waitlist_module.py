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
from flask import make_response
import user_agents
import hashlib
import secrets


from ...utils.db_connection import get_db

def fetch_waitlist():
    db = get_db()
    cursor = db.cursor(pymysql.cursors.DictCursor)

    try:
        sql = """
        SELECT * FROM waitlist ORDER BY created_at DESC
        """
        cursor.execute(sql)
        data = cursor.fetchall()

        return jsonify({
            "data": data
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500