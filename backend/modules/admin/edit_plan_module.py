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


def update_plan(plan_id, data):
    try:
        conn = get_db()
        cursor = conn.cursor()

        # Allowed fields
        fields = [
            "name",
            "price",
            "period",
            "description",
            "features",
            "not_included",
            "popular",
            "properties_limit",
            "listings_limit"
        ]

        updates = []
        values = []

        for field in fields:
            if field in data:
                updates.append(f"{field} = %s")
                values.append(data[field])

        if not updates:
            return jsonify({"error": "No fields to update"}), 400

        values.append(plan_id)

        sql = f"""
            UPDATE plan_data
            SET {", ".join(updates)}
            WHERE id = %s
        """

        cursor.execute(sql, values)
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Plan not found"}), 404

        return jsonify({
            "status": "success",
            "message": "Plan updated successfully"
        }), 200

    except Exception as e:
        return jsonify({"error": "internal server error"}), 500