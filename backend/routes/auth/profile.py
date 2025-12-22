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

from ...modules.auth.profile_module import check_profile
from ...utils.jwt_setup import token_required, require_role
from ...utils.limiter import limiter
from . import auth_bp  # your blueprint

# route to get users info when using token
#this route is called when the app loads to determine the logged in user's screen since the app will have different screens based on role
@auth_bp.route("/profile", methods=["GET"])
@token_required
@require_role("admin")
@limiter.limit("20 per minute")  # still light protection
def profile(current_user_id, role):
    response = check_profile(current_user_id, role)  # call module function that handles DB + JWT
    return response