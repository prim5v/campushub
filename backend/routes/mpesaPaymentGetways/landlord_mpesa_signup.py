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


from . import mpesaPaymentGetways
from ...utils.limiter import limiter
from ...modules.mpesaPaymentGetways.landlord_mpesa_signup_module import perform_landlord_mpesa_signup
from ...utils.jwt_setup import token_required, require_role

@mpesaPaymentGetways.route("/landlord_mpesa_signup", methods=['POST'])
# @token_required
# @require_role("landlord")
@limiter.limit("5 per minute")
def landlord_mpesa_signup():
    data = request.json or request.form
    response = perform_landlord_mpesa_signup(data)  # call module function that handles DB
    return response
