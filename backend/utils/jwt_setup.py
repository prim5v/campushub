# backend/utils/jwt_setup.py

import jwt
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

from .db_connection import get_db
from .audit import log_audit



# ================= JWT GENERATION =================
def generate_jwt(user_id, role, device_id, session_id):
    # Set expiry based on role
    if role == "admin":
        expiry = datetime.utcnow() + timedelta(minutes=1)
    elif role == "comrade":
        expiry = datetime.utcnow() + timedelta(hours=8)
    elif role == "landlord":
        expiry = datetime.utcnow() + timedelta(hours=6)
    else:
        expiry = datetime.utcnow() + timedelta(hours=5)

    payload = {
        "user_id": user_id,
        "role": role,
        "device_id": device_id,
        "session_id": session_id,
        "exp": expiry,
    }

    token = jwt.encode(
        payload,
        current_app.config["SECRET_KEY"],
        algorithm="HS256"
    )

    token_hash = hashlib.sha256(token.encode()).hexdigest()

    return token, expiry, token_hash


# ================= TOKEN PROTECTION =================

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        logger.info("=== AUTH CHECK START ===")
        logger.info("Path=%s Method=%s IP=%s", request.path, request.method, request.remote_addr)

        # ---- Device ID ----
        device_id = request.cookies.get("device_id")
        logger.info("Device ID from cookie: %s", device_id)

        if not device_id:
            logger.warning("AUTH FAIL: Device ID missing")
            return jsonify({"error": "Device ID missing"}), 400

        # ---- JWT from cookie ----
        token = request.cookies.get("access_token")
        logger.info("Access token present: %s", bool(token))

        if not token:
            logger.warning("AUTH FAIL: Token missing")
            return jsonify({"error": "Token missing"}), 401

        # ---- Decode JWT ----
        try:
            data = jwt.decode(
                token,
                current_app.config["SECRET_KEY"],
                algorithms=["HS256"]
            )
            logger.info("JWT decoded successfully")

        except jwt.ExpiredSignatureError:
            logger.warning("AUTH FAIL: JWT expired")
            return jsonify({"error": "Token expired"}), 401

        except jwt.InvalidTokenError:
            logger.warning("AUTH FAIL: Invalid JWT")
            return jsonify({"error": "Invalid token"}), 401

        current_user = data.get("user_id")
        role = data.get("role")
        token_device_id = data.get("device_id")
        session_id = data.get("session_id")

        logger.info(
            "JWT Payload: user_id=%s role=%s device_id=%s session_id=%s",
            current_user, role, token_device_id, session_id
        )

        if not all([current_user, role, token_device_id, session_id]):
            logger.warning("AUTH FAIL: JWT missing required fields")
            return jsonify({"error": "Invalid token payload"}), 401

        # ---- Device binding ----
        if token_device_id != device_id:
            logger.warning(
                "AUTH FAIL: Device mismatch. token_device_id=%s cookie_device_id=%s",
                token_device_id, device_id
            )
            return jsonify({"error": "Token not valid for this device"}), 401

        # ---- Token hash (optional but logged) ----
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        logger.info("Token hash: %s", token_hash)

        # ---- Session check ----
        try:
            conn = get_db()
            cursor = conn.cursor()

            logger.info("Querying session from DB...")
            cursor.execute(
                """
                SELECT * FROM sessions
                WHERE session_id=%s AND user_id=%s AND device_id=%s
                """,
                (session_id, current_user, device_id)
            )
            session = cursor.fetchone()

        except Exception as db_err:
            logger.exception("AUTH FAIL: Database error during session lookup")
            return jsonify({"error": "Auth system failure"}), 500

        if not session:
            logger.warning(
                "AUTH FAIL: Session not found. user_id=%s session_id=%s device_id=%s",
                current_user, session_id, device_id
            )

            log_audit(
                current_user,
                "SESSION_INVALID",
                request,
                role=role,
                status="failure",
                metadata={"reason": "session not found"}
            )

            return jsonify({"error": "Session invalid or revoked"}), 401

        logger.info(
            "Session found in DB. expires_at=%s created_at=%s",
            session["expires_at"], session["created_at"]
        )

        # ---- Expiry check ----
        now = datetime.utcnow()
        logger.info("Current UTC time: %s", now)

        if now > session["expires_at"]:
            logger.warning(
                "AUTH FAIL: Session expired. now=%s expires_at=%s",
                now, session["expires_at"]
            )

            log_audit(
                current_user,
                "SESSION_EXPIRED",
                request,
                role=role,
                status="failure"
            )

            return jsonify({"error": "Session expired"}), 401

        # ---- CSRF protection ----
        if request.method in ("POST", "PUT", "PATCH", "DELETE"):
            csrf_header = request.headers.get("X-CSRF-Token")
            csrf_cookie = request.cookies.get("csrf_token")

            logger.info(
                "CSRF check: header_present=%s cookie_present=%s match=%s",
                bool(csrf_header),
                bool(csrf_cookie),
                csrf_header == csrf_cookie
            )

            if not csrf_header or not csrf_cookie or csrf_header != csrf_cookie:
                logger.warning(
                    "AUTH FAIL: CSRF validation failed. header=%s cookie=%s",
                    csrf_header, csrf_cookie
                )

                log_audit(
                    current_user,
                    "CSRF_FAILURE",
                    request,
                    role=role,
                    status="failure"
                )

                return jsonify({"error": "CSRF validation failed"}), 403

        # ---- Audit protected access ----
        if request.method != "GET":
            log_audit(
                current_user,
                "PROTECTED_ROUTE_ACCESS",
                request,
                role=role,
                status="success"
            )

        logger.info("=== AUTH CHECK PASSED === user_id=%s role=%s", current_user, role)

        return f(current_user, role, *args, **kwargs)

    return decorated

# role based access decorator





def require_role(required_roles):
    """
    Role-based access control decorator.
    - required_roles: str or list/tuple/set of roles
    - MUST be used after token_required
    """

    if isinstance(required_roles, str):
        required_roles_set = {required_roles.lower()}
    else:
        required_roles_set = {r.lower() for r in required_roles}

    def decorator(f):
        @token_required
        @wraps(f)
        def wrapper(current_user, role, *args, **kwargs):

            path = request.path
            method = request.method
            ip = request.remote_addr

            role_normalized = (role or "unknown").lower()

            logger.info(
                "=== ROLE CHECK START === path=%s method=%s ip=%s user_id=%s role=%s required=%s",
                path, method, ip, current_user, role_normalized, list(required_roles_set)
            )

            # ❌ Access denied
            if role_normalized not in required_roles_set:
                logger.warning(
                    "❌ ROLE CHECK FAILED path=%s user_id=%s role=%s required=%s",
                    path, current_user, role_normalized, list(required_roles_set)
                )

                log_audit(
                    user_id=current_user,
                    action="ROLE_ACCESS_DENIED",
                    request=request,
                    role=role_normalized,
                    status="failure",
                    metadata={
                        "required_roles": list(required_roles_set),
                        "attempted_role": role_normalized,
                        "path": path,
                        "method": method,
                    },
                )

                return jsonify({
                    "error": "Forbidden",
                    "message": "You do not have permission to access this resource"
                }), 403

            # ✅ Access granted
            logger.info(
                "✅ ROLE CHECK PASSED path=%s user_id=%s role=%s",
                path, current_user, role_normalized
            )

            log_audit(
                user_id=current_user,
                action="ROLE_ACCESS_GRANTED",
                request=request,
                role=role_normalized,
                status="success",
                metadata={
                    "required_roles": list(required_roles_set),
                    "path": path,
                    "method": method,
                },
            )

            return f(current_user, role, *args, **kwargs)

        return wrapper

    return decorator


logger = logging.getLogger(__name__)

# ================= VERIFIED USER DECORATOR =================
def require_verified_user(f):
    """
    Ensures that the user has a verified security check.
    Must be used **after** token_required (directly or indirectly),
    so `current_user` and `role` are already available.
    """
    @wraps(f)
    def wrapper(current_user, role, *args, **kwargs):

        logger.info(
            "=== VERIFICATION CHECK START === path=%s method=%s ip=%s user_id=%s role=%s",
            request.path,
            request.method,
            request.remote_addr,
            current_user,
            role
        )

        try:
            db = get_db()
            cursor = db.cursor(pymysql.cursors.DictCursor)

            logger.info(
                "Querying security_checks for user_id=%s check_type=landlord",
                current_user
            )

            cursor.execute(
                """
                SELECT status
                FROM security_checks
                WHERE user_id = %s AND check_type = 'landlord'
                """,
                (current_user,)
            )
            check = cursor.fetchone()

            logger.info("Verification query result: %s", check)

            if not check:
                logger.warning(
                    "❌ VERIFICATION FAILED: No security_checks row for user_id=%s",
                    current_user
                )
                return jsonify({
                    "error": "User not verified",
                    "message": "Verification record not found."
                }), 403

            if check.get("status") != "verified":
                logger.warning(
                    "❌ VERIFICATION FAILED: status=%s user_id=%s",
                    check.get("status"),
                    current_user
                )
                return jsonify({
                    "error": "User not verified",
                    "message": "You need to complete verification before accessing this feature."
                }), 403

            logger.info(
                "✅ VERIFICATION PASSED user_id=%s role=%s",
                current_user,
                role
            )

        except Exception as e:
            logger.exception(
                "🔥 VERIFICATION CHECK ERROR user_id=%s error=%s",
                current_user,
                str(e)
            )
            return jsonify({"error": "Verification check failed"}), 500

        # ✅ Proceed to the wrapped route
        return f(current_user, role, *args, **kwargs)

    return wrapper


