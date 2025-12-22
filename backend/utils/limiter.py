# backend/utils/limiter.py

import jwt
from flask import request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


def user_or_ip():
    """
    Identify the requestor for rate limiting.
    Uses user_id from JWT cookie if available, otherwise client IP.
    """
    token = request.cookies.get("access_token")

    if token:
        try:
            decoded = jwt.decode(
                token,
                request.app.config["SECRET_KEY"],
                algorithms=["HS256"]
            )
            return decoded.get("user_id", get_remote_address())
        except Exception:
            pass

    return get_remote_address()


# ⚠️ DO NOT bind to app here
limiter = Limiter(
    key_func=user_or_ip,
    default_limits=["200 per day", "50 per hour"],
)
