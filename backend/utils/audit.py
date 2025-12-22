import jwt
import hashlib
from functools import wraps
from datetime import datetime, timedelta
import json


from flask import (
    request,
    jsonify,
    current_app
)

from .db_connection import get_db


def log_audit(
    user_id,
    action,
    request,
    role="unknown",
    status="success",
    metadata=None
):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO audit_logs (
            user_id,
            action,
            role,
            endpoint,
            method,
            ip_address,
            user_agent,
            device_id,
            status,
            metadata
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            user_id,
            action,
            role,
            request.path,
            request.method,
            request.remote_addr,
            request.headers.get("User-Agent"),
            request.headers.get("X-Device-ID") or request.cookies.get("device_id"),
            status,
            json.dumps(metadata) if metadata else None
        )
    )

    conn.commit()

