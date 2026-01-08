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


from ...utils.db_connection import get_db


def fetch_add_tenant(current_user_id, role):

    upload_folder = current_app.config["UPLOAD_FOLDER"]



    db = get_db()
    cursor = db.cursor()

    data = request.get_json() or request.form

    tenant_name = data.get("tenant_name")
    tenant_email = data.get("tenant_email")
    tenant_phone = data.get("tenant_phone")
    listing_id = data.get("listing_id")
    lease_start_date = data.get("lease_start_date")
    lease_end_date = data.get("lease_end_date")
    rent_amount = data.get("rent_amount")

    images = request.files.getlist("product_images")

    if not images or len(images) == 0:
        return jsonify({"error": "At least one listing image is required"})
    
    os.makedirs(upload_folder, exist_ok=True)
    


    if not all([tenant_name, tenant_email, tenant_phone, listing_id, lease_start_date, lease_end_date, rent_amount]):
        return jsonify({"error": "All fields are required"}), 400

    try:
        tenant_id = str(uuid.uuid4())

        insertsql = """
            INSERT INTO Tenants_data (
                tenant_id, tenant_name, tenant_email, tenant_phone, user_id,
                listing_id, lease_start_date, lease_end_date, rent_amount
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        cursor.execute(
            insertsql,
            (
                tenant_id,
                tenant_name,
                tenant_email,
                tenant_phone,
                current_user_id,
                listing_id,
                lease_start_date,
                lease_end_date,
                rent_amount,
            ),
        )
        db.commit()

         # 2️⃣ Insert images
        insert_image = """
            INSERT INTO images (user_id, tenant_id, image_url)
            VALUES (%s, %s, %s)
        """

        saved_files = []

        for image in images:
            filename = f"{uuid.uuid4().hex}_{image.filename}"
            image_path = os.path.join(upload_folder, filename)
            image.save(image_path)

            cursor.execute(
                insert_image,
                (current_user_id, listing_id, filename)
            )

            saved_files.append(filename)

        db.commit()

        # set the listing to be rented
        updatelisting = """
            UPDATE listings_data
            SET availability_status = 'rented'
            WHERE listing_id = %s
        """
        cursor.execute(updatelisting, (listing_id,))
        db.commit()

        return jsonify({"message": "Tenant added successfully", 
                        "tenant_id": tenant_id,
                        "images": saved_files
                        }), 201

    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500