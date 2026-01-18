import logging
from functools import wraps
from flask import request, jsonify
import pymysql

from .db_connection import get_db

logger = logging.getLogger(__name__)

def plan_limit_required(action_type):
    """
    Decorator to check if the current user can add a listing or property
    based on their plan limits.

    action_type: "listing" or "property"
    MUST be used after token_required / require_role
    """

    def decorator(f):
        @wraps(f)
        def wrapper(current_user, role, *args, **kwargs):

            logger.info(
                "=== PLAN LIMIT CHECK START === path=%s method=%s ip=%s user_id=%s action=%s",
                request.path,
                request.method,
                request.remote_addr,
                current_user,
                action_type
            )

            try:
                db = get_db()
                cursor = db.cursor(pymysql.cursors.DictCursor)

                # 1️⃣ Fetch user's plan
                logger.info("Fetching plan for user_id=%s", current_user)
                cursor.execute(
                    "SELECT plan FROM users WHERE user_id = %s",
                    (current_user,)
                )
                user = cursor.fetchone()

                logger.info("User row: %s", user)

                if not user:
                    logger.warning("❌ PLAN CHECK FAILED: User not found user_id=%s", current_user)
                    return jsonify({"error": "User not found"}), 404

                user_plan_name = user["plan"]

                # 2️⃣ Fetch plan limits
                logger.info("Fetching limits for plan=%s", user_plan_name)
                cursor.execute(
                    "SELECT properties_limit, listings_limit FROM plan_data WHERE name = %s",
                    (user_plan_name,)
                )
                plan = cursor.fetchone()

                logger.info("Plan row: %s", plan)

                if not plan:
                    logger.warning("❌ PLAN CHECK FAILED: Plan not found name=%s", user_plan_name)
                    return jsonify({"error": "Plan not found"}), 404

                # 3️⃣ Count current user's resources
                if action_type == "listing":
                    logger.info("Counting listings for user_id=%s", current_user)
                    cursor.execute(
                        "SELECT COUNT(*) AS count FROM listings_data WHERE user_id = %s",
                        (current_user,)
                    )
                    limit = plan["listings_limit"]

                elif action_type == "property":
                    logger.info("Counting properties for user_id=%s", current_user)
                    cursor.execute(
                        "SELECT COUNT(*) AS count FROM properties_data WHERE user_id = %s",
                        (current_user,)
                    )
                    limit = plan["properties_limit"]

                else:
                    logger.error("❌ Invalid action_type passed to plan_limit_required: %s", action_type)
                    return jsonify({"error": "Invalid action type"}), 500

                count_result = cursor.fetchone()
                current_count = count_result["count"]

                logger.info(
                    "Plan usage: user_id=%s action=%s count=%s limit=%s",
                    current_user,
                    action_type,
                    current_count,
                    limit
                )

                # 4️⃣ Enforce limit
                if current_count >= limit:
                    logger.warning(
                        "❌ PLAN LIMIT EXCEEDED user_id=%s plan=%s action=%s count=%s limit=%s",
                        current_user,
                        user_plan_name,
                        action_type,
                        current_count,
                        limit
                    )
                    return jsonify({
                        "error": f"Your current plan ({user_plan_name}) allows only {limit} {action_type}(s). Upgrade to add more."
                    }), 403

                logger.info(
                    "✅ PLAN LIMIT CHECK PASSED user_id=%s action=%s",
                    current_user,
                    action_type
                )

            except Exception as e:
                logger.exception(
                    "🔥 PLAN LIMIT CHECK ERROR user_id=%s action=%s error=%s",
                    current_user,
                    action_type,
                    str(e)
                )
                return jsonify({"error": "Plan limit check failed"}), 500

            # ✅ Proceed to route
            return f(current_user, role, *args, **kwargs)

        return wrapper
    return decorator
