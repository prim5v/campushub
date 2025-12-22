from flask import Blueprint

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# Import the route modules so they are registered with the blueprint
from . import signup, login, profile, verifyotp


