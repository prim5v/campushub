from flask import Blueprint
ai_bp = Blueprint("ai", __name__, url_prefix="/ai")

# Import the route modules so they are registered with the blueprint
from . import chat, verify_ids, verify_selfie