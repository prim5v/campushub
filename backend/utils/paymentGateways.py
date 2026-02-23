import os
import base64
import requests
import uuid
import json
from datetime import datetime
from requests.auth import HTTPBasicAuth
from decimal import Decimal

from .db_connection import get_db


def trigger_mpesa_stk(phone, amount, user_id):
    try:
        # -------------------------
        # Validation
        # -------------------------
        if not phone or not amount or not user_id:
            return {"error": "Phone, amount and user_id required"}, 400

        try:
            amount = Decimal(str(amount))
            if amount <= 0:
                return {"error": "Invalid amount"}, 400
        except:
            return {"error": "Amount must be numeric"}, 400

        # -------------------------
        # Credentials
        # -------------------------
        consumer_key = os.getenv("MPESA_CONSUMER_KEY")
        consumer_secret = os.getenv("MPESA_CONSUMER_SECRET")
        passkey = os.getenv("MPESA_PASSKEY")
        business_short_code = os.getenv("MPESA_SHORTCODE")

        if not all([consumer_key, consumer_secret, passkey, business_short_code]):
            return {"error": "MPESA credentials not configured"}, 500

        # -------------------------
        # Access Token
        # -------------------------
        auth_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        auth_response = requests.get(
            auth_url,
            auth=HTTPBasicAuth(consumer_key, consumer_secret)
        )

        access_token = "Bearer " + auth_response.json().get("access_token")
        callbackurl = "https://campushub4293.pythonanywhere.com/mpesaPaymentGetways/callback"

        # -------------------------
        # Generate Password
        # -------------------------
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        encoded_password = base64.b64encode(
            (business_short_code + passkey + timestamp).encode()
        ).decode()

        # -------------------------
        # Build Payload
        # -------------------------
        payload = {
            "BusinessShortCode": business_short_code,
            "Password": encoded_password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": float(amount),
            "PartyA": phone,
            "PartyB": business_short_code,
            "PhoneNumber": phone,
            "CallBackURL": callbackurl,
            "AccountReference": "CampassHubBooking",
            "TransactionDesc": "CampassHub Payment"
        }

        headers = {
            "Authorization": access_token,
            "Content-Type": "application/json"
        }

        stk_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        response = requests.post(stk_url, json=payload, headers=headers)
        mpesa_response = response.json()

        if mpesa_response.get("ResponseCode") != "0":
            return {
                "error": "STK push failed",
                "details": mpesa_response
            }, 400

        checkout_request_id = mpesa_response.get("CheckoutRequestID")

        # -------------------------
        # Insert into transactions table
        # -------------------------
        transaction_id = f"TX-{uuid.uuid4().hex[:12].upper()}"

        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
            INSERT INTO transactions (
                transaction_id,
                user_id,
                paid_by,
                paid_to,
                title,
                category,
                transaction_type,
                amount,
                payment_method,
                checkout_request_id,
                status
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            transaction_id,
            user_id,
            json.dumps({"phone": phone}),
            json.dumps({"shortcode": business_short_code}),
            "CampassHub Booking Payment",
            "booking",
            "income",
            amount,
            "mpesa",
            checkout_request_id,
            "pending"
        ))

        db.commit()
        # cursor.close()
        # db.close()

        return {
            "message": "STK push sent",
            "transaction_id": transaction_id,
            "checkout_request_id": checkout_request_id
        }, 200

    except Exception as e:
        return {"error": "Internal server error"}, 500
    
# https://campushub4293.pythonanywhere.com/mpesaPaymentGetways/