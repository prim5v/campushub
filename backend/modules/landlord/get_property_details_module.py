from flask import jsonify
from ...utils.db_connection import get_db

def fetch_property_details(current_user_id, role, property_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    try:
        # 1️⃣ Fetch property (ownership enforced)
        property_sql = """
            SELECT
                property_id,
                property_name,
                property_description,
                property_type,
                listed_at
            FROM properties_data
            WHERE property_id = %s AND user_id = %s
            LIMIT 1
        """
        cursor.execute(property_sql, (property_id, current_user_id))
        prop = cursor.fetchone()

        if not prop:
            return jsonify({"error": "Property not found"}), 404

        # 2️⃣ Fetch property images
        images_sql = """
            SELECT image_url
            FROM images
            WHERE property_id = %s AND user_id = %s
        """
        cursor.execute(images_sql, (property_id, current_user_id))
        images = cursor.fetchall()

        prop["images"] = [img["image_url"] for img in images]

        return jsonify({"property": prop}), 200

    except Exception as e:
        print(f"[ERROR] fetch_property_details: {e}")
        return jsonify({"error": str(e)}), 500
