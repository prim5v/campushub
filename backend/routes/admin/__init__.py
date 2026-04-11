from flask import Blueprint

admin = Blueprint("admin", __name__, url_prefix="/admin")

# Import the route modules so they are registered with the blueprint
from . import get_all_users_from_database, get_listings, get_unverified_users, set_status, get_dashboard_overview, get_recent_system_activity, get_properties, check_transaction, get_plans, delete_plan, edit_plan, create_plan, delete_listing, fetch_listings, get_bookings_and_requests, book, pay, set_maintenance, edit_listing, get_page_time_list, cli, post_announcements, get_recent_announcements, get_waitlist
# added ,ma     