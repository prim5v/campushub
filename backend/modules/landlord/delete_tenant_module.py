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


from ...utils.db_connection import get_db

def remove_tenant(current_user_id, role, tenant_id):
    db = get_db()
    cursor = db.cursor()

    try:
        deletesql = "DELETE FROM tenants WHERE tenant_id = %s AND landlord_id = %s"
        data = (tenant_id, current_user_id)
        cursor.execute(deletesql, data)

        deleteimagesql = "DELETE FROM images WHERE tenant_id = %s"
        cursor.execute(deleteimagesql, (tenant_id,))

        return jsonify(
            {
                "status" : "success" 
            }
        )
    
    except Exception as e:
        print(f"[ERROR] Exception occurred: {e}")
        return jsonify({"error": str(e)}), 500