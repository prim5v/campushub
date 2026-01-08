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


from ...utils.db_connection import get_db

def change_report_status(current_user_id, role):
    db = get_db()
    cursor = db.cursor()

    data = request.get_json()

    report_id = data.get("report_id")
    new_status = data.get("new_status")

    if not report_id or not new_status:
        return jsonify({"error": "report_id and new_status are required"}), 400

    try:
        updatesql = """
            UPDATE reports
            SET status = %s
            WHERE report_id = %s AND user_id = %s
        """

        cursor.execute(
            updatesql,
            (
                new_status,
                report_id,
                current_user_id
            )
        )
        db.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "No report found or no changes made"}), 404

        return jsonify({"message": "Report status updated successfully"}), 200

    except Exception as e:
        print(f"[ERROR] Exception occurred: {e}")
        return jsonify({"error": "Internal server error"}), 500