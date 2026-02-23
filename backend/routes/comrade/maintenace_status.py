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


from . import comrade
from ...utils.limiter import limiter
from ...utils.db_connection import get_db
from . import comrade


@comrade.route("/system_maintenance")
@limiter.limit("25 per minute")
def maintenance_status():
    db= get_db()
    with db.cursor(pymysql.cursors.DictCursor) as cursor:
        cursor.execute("SELECT is_active, message FROM system_maintenance LIMIT 1")
        result = cursor.fetchone()
        return jsonify(result)