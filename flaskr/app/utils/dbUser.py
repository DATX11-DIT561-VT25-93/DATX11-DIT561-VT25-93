
import numpy as np
import base64
from flask import jsonify, request, current_app, redirect, url_for, session


def save_user_to_db(email, face_data):

    # Check if the user already exists
    existing_user_check = check_existing_user(email)
    if existing_user_check[1] != 200:  # If response != 200, the email is taken
        return existing_user_check  

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

        response = supabase.table('registered_users_detection').insert(new_user).execute()
        
        if isinstance(response, dict) and "error" in response and response["error"]:
            return jsonify({"error": "Database error", "details": response["error"]}), 500

        return jsonify({"success": "User was successfully registered"}), 200
    

def check_existing_user(email):
    if not email:
        return jsonify({"error": "Email is null"}), 400  
    
    with current_app.app_context():
        supabase = current_app.supabase

        existing_user = supabase.table('registered_users_detection').select("id").eq("email", email).execute()
        
        if existing_user.data:  
            return jsonify({"error": "Email already taken"}), 409
        
        return jsonify({"success": "Email not in use"}), 200  
