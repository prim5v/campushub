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
from ...utils.limiter import limiter
from . import ai_bp  # your blueprint
from ...modules.AI.chat_module import perform_chat  # import function from your module

@ai_bp.route("/chat", methods=["POST"])
@limiter.limit("10 per minute")  # limit to 10 requests per minute
def chat():
    data = request.json
    response = perform_chat(data)  # call module function that handles chat
    return response
    # return {"message": "AI chat endpoint is under construction."}