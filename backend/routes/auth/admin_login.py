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


from flask import request, jsonify
from . import auth_bp  # your blueprint
from ...modules.auth.admin_login_module import perform_admin_login  # import function from your module
from ...utils.limiter import limiter

@auth_bp.route("/admin_login", methods=["POST"])
@limiter.limit("4 per minute")  # still light protection
def admin_login():
    data = request.json or request.form
    response = perform_admin_login(data)  # call module function that handles DB + JWT
    return response
