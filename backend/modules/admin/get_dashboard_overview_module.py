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
import psutil
import secrets


from flask import jsonify
from decimal import Decimal
from ...utils.db_connection import get_db


def percent_change(current, previous):
    if previous == 0:
        return 100.0 if current > 0 else 0.0
    return round(((current - previous) / previous) * 100, 2)


def fetch_overview():
    db = get_db()
    cursor = db.cursor()

    try:
        # -------------------------------
        # OVERVIEW
        # -------------------------------

        cursor.execute("SELECT COUNT(*) AS total FROM users")
        total_users = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT COUNT(*) AS total 
            FROM listings_data 
            WHERE availability_status = 'available'
        """)
        active_listings = cursor.fetchone()["total"]

        cursor.execute("SELECT COALESCE(SUM(amount),0) AS total FROM e_earnings")
        total_revenue = cursor.fetchone()["total"]
        total_revenue = float(total_revenue) if isinstance(total_revenue, Decimal) else total_revenue

        cursor.execute("""
            SELECT COUNT(*) AS total 
            FROM security_checks 
            WHERE status = 'pending'
        """)
        pending_verifications = cursor.fetchone()["total"]

        # -------------------------------
        # ANALYTICS (CURRENT 30 DAYS)
        # -------------------------------

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM users
            WHERE created_at >= NOW() - INTERVAL 30 DAY
        """)
        users_current = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM listings_data
            WHERE listed_at >= NOW() - INTERVAL 30 DAY
        """)
        listings_current = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT COALESCE(SUM(amount),0) AS total
            FROM e_earnings
            WHERE earning_date >= NOW() - INTERVAL 30 DAY
        """)
        revenue_current = cursor.fetchone()["total"]
        revenue_current = float(revenue_current) if isinstance(revenue_current, Decimal) else revenue_current

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM security_checks
            WHERE performed_at >= NOW() - INTERVAL 30 DAY
        """)
        verifications_current = cursor.fetchone()["total"]

        # -------------------------------
        # ANALYTICS (PREVIOUS 30 DAYS)
        # -------------------------------

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM users
            WHERE created_at BETWEEN 
                NOW() - INTERVAL 60 DAY AND NOW() - INTERVAL 30 DAY
        """)
        users_previous = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM listings_data
            WHERE listed_at BETWEEN 
                NOW() - INTERVAL 60 DAY AND NOW() - INTERVAL 30 DAY
        """)
        listings_previous = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT COALESCE(SUM(amount),0) AS total
            FROM e_earnings
            WHERE earning_date BETWEEN 
                NOW() - INTERVAL 60 DAY AND NOW() - INTERVAL 30 DAY
        """)
        revenue_previous = cursor.fetchone()["total"]
        revenue_previous = float(revenue_previous) if isinstance(revenue_previous, Decimal) else revenue_previous

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM security_checks
            WHERE performed_at BETWEEN 
                NOW() - INTERVAL 60 DAY AND NOW() - INTERVAL 30 DAY
        """)
        verifications_previous = cursor.fetchone()["total"]

        # -------------------------------
        # CALCULATE PERCENT CHANGE
        # -------------------------------

        users_pct = percent_change(users_current, users_previous)
        listings_pct = percent_change(listings_current, listings_previous)
        revenue_pct = percent_change(revenue_current, revenue_previous)
        verifications_pct = percent_change(verifications_current, verifications_previous)

        # -------------------------------
        # SYSTEM HEALTH
        # -------------------------------

        cpu_percent = None
        memory_percent = None
        disk_usage = None

        try:
            

            cpu_percent = psutil.cpu_percent(interval=0.5)
            memory_percent = psutil.virtual_memory().percent

            disk = psutil.disk_usage('/')
            disk_usage = {
                "used_gb": round(disk.used / (1024**3), 2),
                "total_gb": round(disk.total / (1024**3), 2)
            }

        except Exception:
            cpu_percent = "unavailable"
            memory_percent = "unavailable"
            disk_usage = "unavailable"

        db_connections = None
        try:
            cursor.execute("SHOW STATUS LIKE 'Threads_connected'")
            row = cursor.fetchone()
            db_connections = row["Value"] if row else "unknown"
        except Exception:
            db_connections = "unavailable"

        # -------------------------------
        # FINAL RESPONSE
        # -------------------------------

        return jsonify({
            "overview": {
                "total_users": total_users,
                "active_listings": active_listings,
                "total_revenue": total_revenue,
                "pending_verifications": pending_verifications
            },

            "analytics_percent_change": {
                "users": users_pct,
                "listings": listings_pct,
                "revenue": revenue_pct,
                "verifications": verifications_pct
            },

            "system_health": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "database_connections": db_connections,
                "disk_usage": disk_usage
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
