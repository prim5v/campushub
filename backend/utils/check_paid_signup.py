import hashlib
from functools import wraps
from datetime import datetime, timedelta
import pymysql
import logging

logger = logging.getLogger("auth")  # make sure your app configures logger properly

from flask import request, jsonify
from flask_mail import Message
from .db_connection import get_db
from .email_setup import mail
from .extra_functions import generate_otp
from .audit import log_audit

def require_paid_signup(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        db = get_db()
        cursor = db.cursor(pymysql.cursors.DictCursor)

        logger.info("🔍 Checking for paid signup...")

        # Extract email safely
        def extract_email():
            if request.form.get("email"):
                logger.info(f"📥 Email found in form: {request.form.get('email')}")
                return request.form.get("email")

            data = request.get_json(silent=True) or {}
            if data.get("email"):
                logger.info(f"📥 Email found in JSON body: {data.get('email')}")
                return data.get("email")

            if isinstance(data.get("user"), dict) and data["user"].get("email"):
                logger.info(f"📥 Email found in nested user object: {data['user']['email']}")
                return data["user"]["email"]

            logger.warning("⚠️ Email not found in request")
            return None

        email = extract_email()
        if not email:
            logger.error("❌ Email is required but missing")
            return jsonify({"error": "Email is required"}), 400

        logger.info(f"🔎 Checking pending_landlord_signups for email={email}")
        cursor.execute("""
            SELECT *
            FROM pending_landlord_signups
            WHERE email = %s AND status = 'paid'
        """, (email,))
        pending = cursor.fetchone()

        if pending:
            logger.info(f"✅ Found pending paid signup for {email}, preparing OTP")

            # Generate OTP
            otp = generate_otp()
            expires_at = datetime.utcnow() + timedelta(minutes=5)
            logger.info(f"🕒 OTP generated: {otp}, expires at {expires_at}")

            # Save / update OTP
            try:
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
                logger.info(f"💾 OTP saved to database for {email}")
            except Exception as e:
                logger.exception(f"❌ Failed to save OTP for {email}: {e}")
                return jsonify({"error": "Failed to generate OTP"}), 500

            # Send OTP email
            try:
                msg = Message("Verify Your Email", recipients=[pending["email"]])
                msg.body = f"""Hello {pending['username']},

Your verification code is: {otp}

This code expires in 5 minutes.

— CompassHub
"""
                mail.send(msg)
                logger.info(f"📧 OTP email sent to {email}")
            except Exception as e:
                logger.exception(f"❌ Failed to send OTP email to {email}: {e}")
                return jsonify({"error": "Failed to send OTP email"}), 500

            # Return paid response
            logger.info(f"🚀 Returning paid response for {email}")
            return jsonify({
                "status": "paid",
                "message": "Verify email for OTP to complete signup",
                "checkout_request_id": pending.get("checkout_request_id"),
                "mpesa_response": "user already paid for signup"
            }), 200

        # Otherwise continue to the wrapped route
        logger.info(f"ℹ️ No paid pending signup found for {email}, proceeding to route")
        return f(*args, **kwargs)

    return decorated
