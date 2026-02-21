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
import psutil
import secrets

from flask import jsonify
from ...utils.db_connection import get_db

def delete_plan(plan_id):
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM plan_data WHERE id = %s",
            (plan_id,)
        )

        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Plan not found"}), 404

        return jsonify({
            "status": "success",
            "message": "Plan deleted successfully"
        }), 200

    except Exception as e:
        return jsonify({"error": "internal server error"}), 500