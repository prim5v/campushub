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

def fetch_e_service(current_user_id, role):
    db = get_db()
    cursor = db.cursor()

    try:
        fetch_e_service_sql = """
            SELECT *
            FROM e_service_data
            WHERE availability_status = "available"
        """

        cursor.execute(fetch_e_service_sql, (current_user_id,))
        services = cursor.fetchall()

        if not services:
            return jsonify({"services": []}), 200
        
        # get user_ids for the services
        service_ids = [service["user_id"] for service in services]

        # fetch images for the services
        fetch_images_sql ="""
            SELECT * 
            FROM images
            WHERE user_id IN (%s)
        """ % ",".join(["%s"] * len(service_ids))
        cursor.execute(fetch_images_sql, service_ids)
        images = cursor.fetchall()

        # group images by user_id
        images_map = {} 
        for image in images:
            user_id = image["user_id"]
            if user_id not in images_map:
                images_map[user_id] = []
            images_map[user_id].append(image["image_url"])
        # attach images to services
        for service in services:
            service["images"] = images_map.get(service["user_id"], [])
        return jsonify({"services": services}), 200
    except Exception as e:
        logging.error(f"Error fetching e-services: {e}")
        return jsonify({"message": "Internal server error"}), 500
    