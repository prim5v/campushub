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

import json
import logging
from flask import jsonify
from ...utils.db_connection import get_db

logger = logging.getLogger(__name__)


def delete_listing(listing_id):
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM listings_data WHERE listing_id = %s",
            (listing_id,)
        )

        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Listing not found"}), 404

        return jsonify({
            "status": "success",
            "message": "Listing deleted successfully"
        }), 200

    except Exception as e:
        logger.error(f"delete_listing error: {e}", exc_info=True)
        return jsonify({"error": "internal server error"}), 500