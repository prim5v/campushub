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
from ...modules.mpesaPaymentGetways.check_transaction_status_module import check_transaction_status

@mpesaPaymentGetways.route("/check_transaction_status", methods=['POST', 'GET'])
@limiter.limit("15 per minute")
def callback():
    data = request.get_json(silent=True) or {}
    checkout_id = data.get("checkout_id")
    response = check_transaction_status(checkout_id)
    return response
