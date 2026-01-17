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
from ...modules.landlord.delete_property_module import remove_property
from ...utils.jwt_setup import token_required, require_role, require_verified_user


@landlord.route("/delete_property/<property_id>", methods=["DELETE"])
@token_required
@require_role("landlord")
@require_verified_user
@limiter.limit("10 per minute")  # moderate protection
def delete_property(current_user_id, role, *args, **kwargs):
    property_id = kwargs.get("property_id")
    response = remove_property(current_user_id, role, property_id)  # call module function that handles DB
    return response