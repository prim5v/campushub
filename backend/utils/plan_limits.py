from functools import wraps
from flask import request, jsonify
import pymysql

from .db_connection import get_db

def plan_limit_required(action_type):
    """
    Decorator to check if the current user can add a listing or property
    based on their plan limits.

    action_type: "listing" or "property"
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            db = get_db()  # your DB connection helper
            cursor = db.cursor(pymysql.cursors.DictCursor)

            # 1️⃣ Get current user (assuming you have user_id in session or token)
            current_user_id = getattr(request, "user_id", None)  # adjust based on your auth
            if not current_user_id:
                return jsonify({"error": "Unauthorized"}), 401

            # 2️⃣ Fetch user's plan
            cursor.execute("SELECT plan FROM users WHERE user_id = %s", (current_user_id,))
            user = cursor.fetchone()
            if not user:
                return jsonify({"error": "User not found"}), 404

            user_plan_name = user["plan"]

            # 3️⃣ Get plan limits
            cursor.execute(
                "SELECT properties_limit, listings_limit FROM plan_data WHERE name = %s",
                (user_plan_name,)
            )
            plan = cursor.fetchone()
            if not plan:
                return jsonify({"error": "Plan not found"}), 404

            # 4️⃣ Count current user's listings or properties
            if action_type == "listing":
                cursor.execute(
                    "SELECT COUNT(*) AS count FROM listings_data WHERE user_id = %s",
                    (current_user_id,)
                )
            elif action_type == "property":
                cursor.execute(
                    "SELECT COUNT(*) AS count FROM properties_data WHERE user_id = %s",
                    (current_user_id,)
                )
            else:
                return jsonify({"error": "Invalid action type"}), 400

            count_result = cursor.fetchone()
            current_count = count_result["count"]

            # 5️⃣ Check against plan limits
            limit = plan["listings_limit"] if action_type == "listing" else plan["properties_limit"]
            if current_count >= limit:
                return jsonify({
                    "error": f"Your current plan ({user_plan_name}) allows only {limit} {action_type}(s). Upgrade to add more."
                }), 403

            # ✅ Proceed to route
            return f(*args, **kwargs)
        return wrapped
    return decorator
