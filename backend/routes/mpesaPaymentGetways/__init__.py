from flask import Blueprint

mpesaPaymentGetways = Blueprint("mpesaPaymentGetways", __name__, url_prefix="/mpesaPaymentGetways")

from . import landlord_mpesa_signup, mpesa_landlord_signup_callback, landlord_payment_status_check, mpesa_callback, check_transaction_status