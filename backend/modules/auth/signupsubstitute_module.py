from flask import jsonify, request, make_response
import logging
import uuid
import bcrypt
import secrets
from datetime import datetime

from ...utils.jwt_setup import generate_jwt
from ...utils.db_connection import get_db
from ...utils.extra_functions import get_device_info

logger = logging.getLogger(__name__)

def substitute_signup(data):

    try:
        logger.info("🚀 Substitute signup request received")

        email = data.get("email")
        password = data.get("password")
        username = data.get("username")
        role = data.get("role")
        institution = data.get("institution")
        acceptedTerms = data.get("acceptedTerms")

        logger.info(f"📥 Payload received: email={email}, username={username}, role={role}, institution={institution}")
        

        ALLOWED_ROLES = {"comrade", "landlord", "e_service"}

        if role not in ALLOWED_ROLES:
            logger.warning(f"❌ Invalid role attempted: {role}")
            return jsonify({"error": "invalid role"}), 400

        if not email or not password or not username or not role:
            logger.warning("❌ Missing required fields in signup payload")
            return jsonify({"error": "missing required fields"}), 400

        if role == "comrade" and not institution:
            return jsonify({"error": "institution required"}), 400

        if not acceptedTerms:
            return jsonify({"error": "must accept terms and conditions"}), 400

        conn = get_db()
        cursor = conn.cursor()
        logger.info("✅ Database connection opened")

        # ==============================
        # Check username
        # ==============================
        logger.info(f"🔎 Checking if username exists: {username}")
        cursor.execute("SELECT 1 FROM users WHERE username=%s", (username,))
        if cursor.fetchone():
            logger.warning(f"❌ Username already exists: {username}")
            return jsonify({"error": "username already exists"}), 400

        # ==============================
        # Check email
        # ==============================
        logger.info(f"🔎 Checking if email exists: {email}")
        cursor.execute("SELECT 1 FROM users WHERE email=%s", (email,))
        if cursor.fetchone():
            logger.warning(f"❌ Email already exists: {email}")
            return jsonify({"error": "email already exists"}), 400
        

        logger.info("✅ All validations passed, proceeding with substitute signup process")
        role_prefixes = {"landlord": "lnrd", "comrade": "cd"}
        prefix = role_prefixes.get(role, "usr")
        user_id = f"{prefix}-{str(uuid.uuid4())[:16].upper()}"
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        cursor.execute("""
            INSERT INTO users (user_id, username, email, password_hash, role, institution)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            user_id,
            username,
            email,
            password_hash,
            role,
            institution
        ))
        conn.commit()

        logger.info(f"✅ User created successfully: user_id={user_id}, email={email}, role={role}")

        # create session immediately after signup
        # ✅ Create session immediately
        device_id = request.cookies.get("device_id")
        if not device_id:
            device_id = f"DEV-{uuid.uuid4().hex[:10].upper()}"

        session_id = str(uuid.uuid4())
        token, expiry, token_hash = generate_jwt(user_id, role, device_id, session_id)

        # Fetch device info
        device_info = get_device_info()

        cursor.execute("""
                INSERT INTO sessions (
                    session_id, user_id, token_hash, expires_at, device_id, browser, os, ip_address, location_address
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                session_id,
                user_id,
                token_hash,
                expiry,
                device_id,
                device_info["browser"],
                device_info["os"],
                device_info["ip"],
                device_info["location"]
            ))
        conn.commit()

        # insert user_id and statusin security_checks table
        cursor.execute("""
                INSERT INTO security_checks (user_id, status, check_type)
                VALUES (%s, %s, %s)
            """, (user_id, "verified", role))
            # overide verification
        conn.commit()

        # get user status
        cursor.execute("SELECT status FROM security_checks WHERE user_id=%s", (user_id,))
        status = cursor.fetchone()["status"]

        # ✅ Prepare response with cookie
        resp = make_response(jsonify({
                "status": "success",
                "message": "Email verified successfully. Account created!",
                "user": {
                    "user_id": user_id,
                    "username": username,
                    "role": role,
                    "email": email,
                    "status": status
                },
            }))
        resp.set_cookie(
                "device_id",
                device_id,
                max_age=365*24*60*60,  # 1 year
                httponly=True,
                secure=True,  # set to False if testing on HTTP
                samesite="None",  # allow cross-site sending,
                path="/"
            )

        resp.set_cookie(
                "access_token",
                token,
                max_age=int((expiry - datetime.utcnow()).total_seconds()),
                httponly=True,
                secure=True,
                samesite="None",
                path="/"
            )

        csrf_token = secrets.token_hex(32)

        resp.set_cookie(
                "csrf_token",
                csrf_token,
                httponly=False,   # MUST be readable by JS
                secure=True,
                samesite="None",
                path="/"
            )

        return resp

    except Exception as e:
        logger.error("Error occurred while processing substitute signup request: %s", str(e))
        raise