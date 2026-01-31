# utils/__init__.py
from .limiter import limiter
from .jwt_setup import generate_jwt, token_required
from .db_connection import get_db, close_db
from .email_setup import mail
from .extra_functions import get_device_info, send_security_email, send_informational_email
from .gemini_setup import client as gemini_client
from .gemini_setup import GEMINI_API_KEY
from .audit import log_audit
from .plan_limits import plan_limit_required
from .check_paid_signup import require_paid_signup
from .vision import is_blurry, extract_face_embedding, compare_faces
