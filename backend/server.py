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

# from flask_mail import Message
# from app import mail  # Ensure 'mail' is imported from where you initialized it
# python3.10 -m pip install flask flask-cors pymysql bcrypt requests PyJWT

# ================= FLASK APP SETUP =================
app = Flask(__name__)
CORS(
    app,
    supports_credentials=True,
    origins=[
        "http://localhost:5173",
        "https://zetech-feedback-portal.vercel.app"
    ]
)

app.config['UPLOAD_FOLDER'] = '/home/backendagripool4293/mysite/static/images'

# server.py
from routes.auth import auth_bp
app.register_blueprint(auth_bp)



# Configure structured logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


















