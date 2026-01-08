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


from ...utils.db_connection import get_db

def fetch_transactions(current_user_id, role):
    db = get_db()
    cursor = db.cursor()

    try:
        # 1️⃣ Fetch all transactions
        fetch_transactions_sql = """
            SELECT
                transaction_id,
                title,
                category,
                transaction_type,
                amount,
                payment_method,
                mpesa_code,
                transaction_date,
                status
            FROM transactions
            WHERE user_id = %s
            ORDER BY transaction_date DESC
        """
        cursor.execute(fetch_transactions_sql, (current_user_id,))
        transactions = cursor.fetchall()

        # 2️⃣ Calculate totals (SQL is best for this)
        totals_sql = """
            SELECT
                COALESCE(SUM(CASE WHEN transaction_type = 'income' THEN amount END), 0) AS total_income,
                COALESCE(SUM(CASE WHEN transaction_type = 'expense' THEN amount END), 0) AS total_expense
            FROM transactions
            WHERE user_id = %s
        """
        cursor.execute(totals_sql, (current_user_id,))
        totals = cursor.fetchone()

        total_income = float(totals["total_income"])
        total_expense = float(totals["total_expense"])
        total_amount = total_income + total_expense

        # 3️⃣ Group transactions
        income_transactions = []
        expense_transactions = []

        for tx in transactions:
            tx["amount"] = float(tx["amount"])  # Decimal → JSON safe

            if tx["transaction_type"] == "income":
                income_transactions.append(tx)
            else:
                expense_transactions.append(tx)

        return jsonify({
            "summary": {
                "total_amount": total_amount,
                "total_income": total_income,
                "total_expense": total_expense
            },
            "transactions": {
                "income": income_transactions,
                "expense": expense_transactions
            }
        }), 200

    except Exception as e:
        print(f"[ERROR] Exception occurred: {e}")
        return jsonify({"error": "Internal server error"}), 500

