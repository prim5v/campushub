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
import json
import logging
from flask import jsonify
from ...utils.db_connection import get_db

logger = logging.getLogger(__name__)

def create_cli(data):
    try:
        logger.info("📦 Create CLI request received")

        query = data.get("query")
        if not query:
            logger.warning("❌ Missing required field: query")
            return jsonify({"error": "missing required field: query"}), 400

        db = get_db()
        cursor = db.cursor(pymysql.cursors.DictCursor)

        cursor.execute(query)

        # Determine query type
        query_type = query.strip().split()[0].lower()

        if query_type == "select":
            result = cursor.fetchall()
            columns = [col[0] for col in cursor.description]

            logger.info("✅ SELECT query executed")
            return jsonify({
                "type": "select",
                "columns": columns,
                "rows": len(result),
                "data": result
            }), 200

        elif query_type == "insert":
            db.commit()
            logger.info("✅ INSERT query executed")
            return jsonify({
                "type": "insert",
                "insert_id": cursor.lastrowid
            }), 201

        elif query_type in ["update", "delete"]:
            db.commit()
            logger.info("✅ UPDATE/DELETE query executed")
            return jsonify({
                "type": query_type,
                "affected_rows": cursor.rowcount
            }), 200

        else:
            db.commit()
            return jsonify({
                "type": "other",
                "message": "Query executed successfully"
            }), 200

    except Exception as e:
        logger.error(f"❌ Error creating CLI: {str(e)}")
        return jsonify({"error": str(e)}), 500