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
from ...modules.landlord.make_badge_request_module import make_badge_request
from ...utils.jwt_setup import token_required, require_role


@landlord.route("/badge_request", methods=["POST", "PUT"])
@require_role("landlord")
@limiter.limit("3 per minute")  # moderate protection
def badge_request(current_user_id, role, *args, **kwargs):
    data= request.get_json()  # get JSON data from request
    response = make_badge_request(current_user_id, role, data)  # call module function that handles DB
    return response