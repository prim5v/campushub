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


from . import admin  # your blueprint
from ...utils.limiter import limiter
# reuse func
from ...modules.admin.delete_plan_module import delete_plan

@admin.route("/delete_plan/<int:plan_id>", methods=['POST', 'GET'])
@limiter.limit("10 per minute")
def remove_plan(plan_id):
    response = delete_plan(plan_id)
    return response