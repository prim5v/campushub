from flask import Blueprint

admin = Blueprint("admin", __name__, url_prefix="/admin")

# Import the route modules so they are registered with the blueprint
from . import get_all_users_from_database, get_listings, get_unverified_users, set_status


