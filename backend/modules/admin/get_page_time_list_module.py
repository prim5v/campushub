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

def get_page_time_list():
    try:
        db = get_db()
        cursor = db.cursor(pymysql.cursors.DictCursor)

        query = """
        SELECT 
            pt.page_id,
            pt.page_name,
            pt.user,
            pt.paged_at,
            u.username,
            u.email,
            u.role
        FROM page_time pt
        LEFT JOIN users u ON pt.user = u.user_id
        INNER JOIN (
            SELECT page_id, MAX(paged_at) AS latest_time
            FROM page_time
            GROUP BY page_id
        ) latest 
        ON pt.page_id = latest.page_id 
        AND pt.paged_at = latest.latest_time
        ORDER BY pt.paged_at DESC
        """

        cursor.execute(query)
        rows = cursor.fetchall()

        members = []
        anonymous = []

        online_members = 0
        online_anonymous = 0

        now = datetime.utcnow()

        for row in rows:

            paged_at = row["paged_at"]

            # determine online/offline
            # status = "offline"
            # if paged_at and (now - paged_at).total_seconds() <= 120:
            #     status = "online"
            seconds = (now - paged_at).total_seconds()

            if seconds <= 30:
                status = "online"
            elif seconds <= 90:
                status = "idle"
            else:
                status = "offline"

            entry = {
                "page_id": row["page_id"],
                "page_name": row["page_name"],
                "paged_at": paged_at,
                "status": status
            }

            # MEMBER
            if row["username"]:
                entry["user"] = {
                    "user_id": row["user"],
                    "username": row["username"],
                    "email": row["email"],
                    "role": row["role"]
                }

                members.append(entry)

                # if status == "online":
                #     online_members += 1
                if status in ["online", "idle"]:
                    online_members += 1

            # ANONYMOUS
            else:
                anonymous.append(entry)

                if status in ["online", "idle"]:
                    online_anonymous += 1

        response = {
            "online_data": {
                "total_counts": online_members + online_anonymous,
                "anonymous": online_anonymous,
                "members": online_members
            },
            "lists": {
                "members": members,
                "anonymous": anonymous
            }
        }

        return jsonify(response), 200

    except pymysql.MySQLError as db_error:
        logging.error(f"Database error: {db_error}")
        return jsonify({"error": "Database error"}), 500

    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

    # finally:
    #     try:
    #         cursor.close()
    #     except:
    #         pass