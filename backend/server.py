# backend/server.py

import os
import logging
from dotenv import load_dotenv

from flask import Flask, jsonify
from flask_cors import CORS

from backend.utils.limiter import limiter
from backend.utils.email_setup import mail

from flask_mail import Mail, Message


load_dotenv()

# ================= FLASK APP SETUP =================
app = Flask(__name__)

# === EMAIL CONFIG ===
app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER")
app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", 587))
app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS", "true").lower() in ("true", "1", "yes")
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_DEFAULT_SENDER")

# print("MAIL_SERVER =", os.getenv("MAIL_SERVER"))
# print("MAIL_PORT =", os.getenv("MAIL_PORT"))
# import socket
# print(socket.gethostbyname("smtp.gmail.com"))


mail.init_app(app)


app.config["SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config["UPLOAD_FOLDER"] = "/home/campushub4293/campushub/backend/static/images"

CORS(
    app,
    supports_credentials=True,
    resources={r"/*": {
        "origins": [
            "http://localhost:5173",
            "https://campushub-website.vercel.app"
        ]
    }}
)




# ================= EXTENSIONS =================
limiter.init_app(app)

# ================= ERROR HANDLERS =================
@app.errorhandler(429)
def ratelimit_error(e):
    return jsonify({
        "error": "Too many requests — slow down.",
        "details": str(e.description)
    }), 429

# ================= BLUEPRINTS =================
from backend.routes.auth import auth_bp
from backend.routes.admin import admin
from backend.routes.landlord import landlord
from backend.routes.comrade import comrade
from backend .routes.mpesaPaymentGetways import mpesaPaymentGetways

app.register_blueprint(auth_bp)
app.register_blueprint(admin)
app.register_blueprint(landlord)
app.register_blueprint(comrade)
app.register_blueprint(mpesaPaymentGetways)


# ================= LOGGING =================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logging.info("Starting the Flask application...")
logging.info("Flask application started successfully.")

# test routes
@app.route("/")
def index():
    return "Am Backend and am up and running"

@app.route("/test-email")
def test_email():
    msg = Message(
        subject="Flask Mail Test",
        recipients=["your_other_email@gmail.com"],
        body="If you received this, Flask-Mail is working correctly!"
    )
    mail.send(msg)
    return "✅ Test email sent successfully!"


# ================= RUN =================
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=os.getenv("FLASK_DEBUG") == "1",
        ssl_context = (
            "./192.168.100.2+1.pem",
            "./192.168.100.2+1-key.pem" 
        )
    )


