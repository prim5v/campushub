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

from . import auth_bp  # your blueprint
from ...modules.auth.verifyotp_module import perform_verify_otp  # import function from your module        
from ...utils.limiter import limiter


@auth_bp.route("/verify-otp", methods=["POST"])
@limiter.limit("4 per minute")  # still light protection
def verify_otp():
    data = request.get_json()
    response = perform_verify_otp(data)  # call module function that handles DB + JWT
    return response