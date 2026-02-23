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


from . import admin  # your blueprint
from ...utils.limiter import limiter
from ...modules.admin.get_bookings_and_requests_module import get_requests_and_bookings

@admin.route("/get_bookings_and_requests", methods=['POST', 'GET', 'DELETE'])
@limiter.limit("10 per minute")
def fetch_requests_and_bookings():
    response = get_requests_and_bookings()
    return response