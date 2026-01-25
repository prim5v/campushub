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
from ...modules.comrade.get_listing_details_module import fetch_listing_details
from ...utils.jwt_setup import token_required, require_role

@comrade.route("/get_listing_details/<listing_id>", methods=['POST'])
# @token_required
# @require_role("comrade")
@limiter.limit("10 per minute")
def get_listing_details(listing_id):
    data = request.json or request.form
    response = fetch_listing_details(listing_id, data)  # call module function that handles DB
    return response