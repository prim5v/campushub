import hashlib
from functools import wraps
from datetime import datetime, timedelta
import pymysql
import logging

logger = logging.getLogger("auth")


from flask import (
    request,
    jsonify,
    current_app
)
from flask_mail import Mail, Message
from .db_connection import get_db
from .email_setup import mail
from .extra_functions import generate_otp

from .audit import log_audit
def require_paid_signup(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        db = get_db()
        cursor = db.cursor(pymysql.cursors.DictCursor)

        data = request.json or request.form
        email = data.get("email")

        if not email:
            return jsonify({"error": "Email is required"}), 400

        # 1️⃣ Check if user already paid
        cursor.execute("""
            SELECT *
            FROM pending_landlord_signups
            WHERE email = %s AND status = 'paid'
        """, (email,))
        pending = cursor.fetchone()

        if pending:
            # 2️⃣ Generate OTP
            otp = generate_otp()
            expires_at = datetime.utcnow() + timedelta(minutes=5)

            # 3️⃣ Save / update OTP
            cursor.execute("""
                INSERT INTO email_otp (email, otp_code, expires_at, plan)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                    otp_code = VALUES(otp_code),
                    expires_at = VALUES(expires_at),
                    plan = VALUES(plan)
            """, (
                pending["email"],
                otp,
                expires_at,
                pending.get("plan")
            ))

            db.commit()

            # 4️⃣ Send OTP email
            msg = Message("Verify Your Email", recipients=[pending["email"]])
            msg.body = f"""Hello {pending['username']},

Your verification code is: {otp}

This code expires in 5 minutes.

— CompassHub
"""
            mail.send(msg)

            # 5️⃣ Return paid response
            return jsonify({
                "status": "paid",
                "message": "Verify email for OTP to complete signup",
                "checkout_request_id": pending.get("checkout_request_id"),
                "mpesa_response": "user already paid for signup"
            }), 200

        # 6️⃣ Otherwise continue to actual route
        return f(*args, **kwargs)

    return decorated
