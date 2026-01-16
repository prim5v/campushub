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


from . import landlord  # your blueprint
from ...utils.limiter import limiter
from ...modules.landlord.add_listing_module import fetch_add_listing
from ...utils.jwt_setup import token_required, require_role


@landlord.route("/add_listing", methods=["POST"])
@token_required
@require_role("landlord")
@limiter.limit("10 per minute")  # moderate protection
def add_listing(current_user_id, role, *args, **kwargs):
    response = fetch_add_listing(current_user_id, role, *args, **kwargs)  # call module function that handles DB
    return response