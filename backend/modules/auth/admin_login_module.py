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

from ...utils.email_setup import mail   
from ...utils.db_connection import get_db
from ...utils.jwt_setup import generate_jwt
import bcrypt, uuid
from datetime import datetime, timedelta
from ...utils.extra_functions import (generate_otp, send_security_email, send_informational_email, get_device_info)

def perform_admin_login(data):
    #use email and provided otp
    email = data.get("email")
    otp = data.get("otp")

    # validation
    if not email or not otp:
        return jsonify({"error": "required fields"}), 400
    
    conn = get_db()
    cursor = conn.cursor()

    # check if email exists in user table
    cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cursor.fetchone()
    if not user:
        return jsonify({"error": "user not found"}), 404
    
    # check otp if it exists in admin
    cursor.execute("""
            SELECT * FROM email_otp
            WHERE email = %s
            ORDER BY created_at DESC
            LIMIT 1
        """, (email,))
    record = cursor.fetchone()

    if not record:
        return jsonify({"error": "No OTP found for this email. Please request a new one."}), 404
    

    # Check if user exceeded attempts
    if record["attempts"] >= 5:
        return jsonify({"error": "Too many incorrect attempts. OTP locked. Request a new OTP."}), 403

    # Check expiration
    if datetime.utcnow() > record["expires_at"]:
        return jsonify({"error": "OTP has expired"}), 400
    
    
    # validate otp
    if record["otp_code"] != otp:
        # Increment attempt count
        cursor.execute("""
                    UPDATE email_otp SET attempts = attempts + 1
                    WHERE email = %s
                """, (email,))
        conn.commit()

        attempts_left = 5 -(record["attempts"] + 1)
        return jsonify({
                    "error": "Incorrect OTP",
                    "attempts_left": max(attempts_left, 0)
                }), 400
    
    # otp correct
    # Device and session handling
    device_id = request.cookies.get("device_id") or f"DEV-{uuid.uuid4().hex[:10].upper()}"
    session_id = str(uuid.uuid4())
    token, expiry, token_hash = generate_jwt(user["user_id"], record["role"], device_id, session_id)

    # insert into sessions table
    device_info = get_device_info()
    cursor.execute("""
        INSERT INTO sessions (session_id, user_id, token_hash, expires_at, device_id, device_name, browser, os, ip_address, location_address)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s, %s)
    """, (
        session_id, user["user_id"], token_hash, expiry, device_id, device_info["device"],
        device_info["browser"], device_info["os"], device_info["ip"], device_info["location"]
    ))
    conn.commit()

    
    # Trust score evaluation
    cursor.execute("""
        SELECT device_id, COUNT(*) as usage_count
        FROM sessions
        WHERE user_id=%s
        GROUP BY device_id
        ORDER BY usage_count DESC
        LIMIT 1
    """, (user["user_id"],))
    primary_device = cursor.fetchone()

    cursor.execute("""
        SELECT device_id, ip_address, location_address, browser, os
        FROM sessions
        WHERE user_id=%s
        ORDER BY created_at DESC
        LIMIT 1
    """, (user["user_id"],))
    last_session = cursor.fetchone()

    trust_score, reasons = 0, []

     # IP Check
    if last_session and last_session["ip_address"] == device_info["ip"]:
        trust_score += 40
    else:
        trust_score -= 50
        reasons.append("New IP address detected")

    # Location Check
    if last_session and last_session["location_address"] == device_info["location"]:
        trust_score += 30
    else:
        trust_score -= 30
        reasons.append("Login from a different location")

    # Device Check
    if primary_device and primary_device["device_id"] == device_id:
        trust_score += 20
    else:
        trust_score -= 20
        reasons.append("Unfamiliar device detected")

    # Browser Check
    if last_session and last_session["browser"] == device_info["browser"]:
        trust_score += 10
    else:
        trust_score -= 10
        reasons.append("Browser differs from previous login")

    # Send alerts based on trust
    if trust_score < 50:
        send_security_email(user["email"], device_info, reasons)
    elif trust_score < 80:
        send_informational_email(user["email"], device_info, reasons)

    # get user status
    cursor.execute("SELECT status FROM security_checks WHERE user_id=%s", (user["user_id"],))
    status = cursor.fetchone()["status"]
    
    csrf_token = secrets.token_hex(32)

    # Set cookies and return response
    resp = make_response(jsonify({
        "status": "success",
        "user": {
            "user_id": user["user_id"],
            "username": user["username"],
            "role": user["role"],
            "email": user["email"],
            "status": status,
            "csrf_token": csrf_token
        },
    }))
    resp.set_cookie("device_id", device_id, max_age=365*24*60*60, httponly=True, secure=True, samesite="None", path="/")
    resp.set_cookie("access_token", token, max_age=int((expiry - datetime.utcnow()).total_seconds()), httponly=True, secure=True, samesite="None", path="/")
    resp.set_cookie("csrf_token", csrf_token, httponly=False, secure=True, samesite="None", path="/")

    return resp




