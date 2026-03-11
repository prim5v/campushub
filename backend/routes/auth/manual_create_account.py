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


from . import auth_bp  # your blueprint
from ...utils.limiter import limiter
from ...modules.auth.manual_create_account_module import perform_manual_create_account

@auth_bp.route("/manual_create_account", methods=['POST'])
@limiter.limit("3 per minute")
def manual_create_account():
    response = perform_manual_create_account()
    return response