
import numpy as np
import base64
from flask import jsonify, request, current_app, redirect, url_for, session


def save_user_to_db(email, face_data):
    with current_app.app_context():
        supabase = current_app.supabase

        if isinstance(face_data, np.ndarray):
            face_data = face_data.tolist()
        elif isinstance(face_data, bytes):  
            face_data = base64.b64encode(face_data).decode('utf-8')

        new_user = {
            "email": email,
            "face_features": face_data  
        }

        print("Ja")
        response = supabase.table('registered_users_detection').insert(new_user).execute()
        
        if isinstance(response, dict) and "error" in response and response["error"]:
            return jsonify({"error": "Database error", "details": response["error"]}), 500
        return jsonify({"success": "User was successfully registered"}), 200