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
import os
import json
from ...utils.email_setup import mail   
from ...utils.db_connection import get_db
from ...utils.jwt_setup import generate_jwt
import bcrypt, uuid
from datetime import datetime, timedelta
from ...utils.extra_functions import (generate_otp, send_security_email, send_informational_email, get_device_info)
from ...utils.gemini_setup import client, respond_to_prompt_only  # Gemini client setup

def perform_chat(data):
    prompt = data.get("prompt")
    username = "Barack Obama"  # Example static username
    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400

    response = respond_to_prompt_only(prompt, username)
    return jsonify({"response": response})