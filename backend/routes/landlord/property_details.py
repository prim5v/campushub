from flask import Blueprint
from . import landlord
from ...utils.jwt_setup import token_required, require_role
from ...utils.limiter import limiter
from ...modules.landlord.get_property_details_module import fetch_property_details

@landlord.route("/property/<property_id>", methods=["GET"])
@token_required
@require_role("landlord")
@limiter.limit("20 per minute")
def get_property_details(current_user_id, role, property_id):
    return fetch_property_details(current_user_id, role, property_id)
