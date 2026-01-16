# backend/utils/jwt_setup.py

import jwt
import hashlib
from functools import wraps
from datetime import datetime, timedelta


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
        # ---- Device ID ----
        # device_id = (
        #     request.headers.get("X-Device-ID")
        #     or request.cookies.get("device_id")
        # )
        device_id = request.cookies.get("device_id")
        if not device_id:
            return jsonify({"error": "Device ID missing"}), 400

        # ---- JWT from cookie ----
        token = request.cookies.get("access_token")
        if not token:
            return jsonify({"error": "Token missing"}), 401

        # ---- Decode JWT ----
        try:
            data = jwt.decode(
                token,
                current_app.config["SECRET_KEY"],
                algorithms=["HS256"]
            )
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        current_user = data.get("user_id")
        role = data.get("role")
        token_device_id = data.get("device_id")

        # ---- Device binding ----
        # code 401 bug here below
        if token_device_id != device_id:
            return jsonify({"error": "Token not valid for this device"}), 401

        # ---- Token hash ----
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        # ---- Session check ----
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM sessions
            WHERE user_id=%s AND token_hash=%s AND device_id=%s
            """,
            (current_user, token_hash, device_id)
        )
        session = cursor.fetchone()

        if not session:
            return jsonify({"error": "Session invalid or revoked"}), 401
        log_audit(
                    current_user,
                    "SESSION_INVALID",
                    request,
                    role=role,
                    status="failure",
                    metadata={"reason": "token revoked or mismatch"}
                )


        if datetime.utcnow() > session["expires_at"]:
            return jsonify({"error": "Session expired"}), 401

        # ---- CSRF protection ----
        if request.method in ("POST", "PUT", "PATCH", "DELETE"):
            csrf_header = request.headers.get("X-CSRF-Token")
            csrf_cookie = request.cookies.get("csrf_token")

            if not csrf_header or csrf_header != csrf_cookie:
                return jsonify({"error": "CSRF validation failed"}), 403
            log_audit(
                        current_user,
                        "CSRF_FAILURE",
                        request,
                        role=role,
                        status="failure"
                    )

            # 🔥 Log only sensitive or mutating access
        if request.method != "GET":
            log_audit(
                current_user,
                "PROTECTED_ROUTE_ACCESS",
                request,
                role=role
            )


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
            role_normalized = (role or "unknown").lower()

            # ❌ Access denied
            if role_normalized not in required_roles_set:
                log_audit(
                    user_id=current_user,
                    action="ROLE_ACCESS_DENIED",
                    request=request,
                    role=role_normalized,
                    status="failure",
                    metadata={
                        "required_roles": list(required_roles_set),
                        "attempted_role": role_normalized,
                    },
                )

                return jsonify({
                    "error": "Unauthorized",
                    # "required_roles": list(required_roles_set)
                }), 403

            # ✅ Access granted
            log_audit(
                user_id=current_user,
                action="ROLE_ACCESS_GRANTED",
                request=request,
                role=role_normalized,
                status="success",
                metadata={
                    "required_roles": list(required_roles_set)
                },
            )

            return f(current_user, role, *args, **kwargs)

        return wrapper

    return decorator

