from flask import Blueprint

landlord = Blueprint("landlord", __name__, url_prefix="/landlord")

# Import the route modules so they are registered with the blueprint
from . import add_listing, add_property, add_tenant, add_transaction, delete_listing,delete_property, delete_tenant, delete_transaction, edit_listing, edit_property, edit_tenant, get_listings, get_properties, get_reports, get_tenants, get_transaction, update_report_status, get_plans, get_plan_details, get_overview



