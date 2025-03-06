
import numpy as np
import base64
from flask import jsonify, request, current_app, redirect, url_for, session


def save_user_to_db(email, face_data):
    with current_app.app_context():
        supabase = current_app.supabase

        existing_user = supabase.table('registered_users_detection').select("id").eq("email", email).execute()
        
        if existing_user.data:
            return jsonify({"error": "Username already taken"}), 409 

        if isinstance(face_data, np.ndarray):
            face_data = face_data.tolist()
        elif isinstance(face_data, bytes):  
            face_data = base64.b64encode(face_data).decode('utf-8')

        new_user = {
            "email": email,
            "face_features": face_data  
        }
        
        response = supabase.table('registered_users_detection').insert(new_user).execute()
        
        if isinstance(response, dict) and "error" in response and response["error"]:
            return jsonify({"error": "Database error", "details": response["error"]}), 500
        return jsonify({"success": "User was successfully registered"}), 200
    

def get_feature_vector_from_db(email):
    with current_app.app_context():
        
        supabase = current_app.supabase
        response = supabase.table("registered_users_detection").select("face_features").eq("email", email).execute()

        if response.data:
            face_features = response.data[0]["face_features"]
            return face_features
        else:
            print("No matching entry found or error in the query.")
            return None