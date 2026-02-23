from flask import Blueprint

comrade = Blueprint("comrade", __name__, url_prefix="/comrade")

from . import get_e_service, get_listings, get_listing_details, request, maintenace_status
