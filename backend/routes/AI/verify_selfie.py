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

from . import ai_bp  # your blueprint
from flask import request, jsonify
from ...modules.AI.verify_selfie_module import verify_selfie_route  # import function from your module
from ...utils.jwt_setup import token_required, require_role
from ...utils.limiter import limiter

@ai_bp.route("/verify_selfie", methods=["POST"])
@token_required
@require_role("landlord")
@limiter.limit("5 per minute")  # limit to 5 requests per minute
def verify_selfie(current_user_id, role, *args, **kwargs):
    response = verify_selfie_route(current_user_id, *args, **kwargs)  # call module function that handles selfie verification
    return response
    # return {"message": "Selfie verification endpoint is under construction."}