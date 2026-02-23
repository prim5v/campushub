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
from ...modules.mpesaPaymentGetways.mpesa_callback_module import handle_mpesa_transaction_callback

@mpesaPaymentGetways.route("/mpesa_callback", methods=['POST', 'GET'])
@limiter.limit("3 per minute")
def mpesa_callback():
    data = request.get_json(silent=True) or {}
    response = handle_mpesa_transaction_callback(data)
    return response
