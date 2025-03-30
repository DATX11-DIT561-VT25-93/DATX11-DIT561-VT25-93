import numpy as np
import base64
from flask import jsonify, request, current_app
from dotenv import load_dotenv
from .crypto_utils import encrypt_aes_gcm, decrypt_aes_gcm
import os
import json

load_dotenv()
AES_KEY = bytes.fromhex(os.getenv("AESGCM_SECRET_KEY"))


def save_user_to_db(email, face_data):
    with current_app.app_context():
        supabase = current_app.supabase

        existing_user = supabase.table('Users').select("id").eq("email", email).execute()
        
        if existing_user.data:
            return jsonify({"error": "Username already taken"}), 409 

        # Convert face_data into a storable format
        if isinstance(face_data, np.ndarray):
            face_data = json.dumps(face_data.tolist())  # Convert list to JSON string
        elif isinstance(face_data, list):
            face_data = json.dumps(face_data)  # Convert list to JSON string
        elif isinstance(face_data, bytes):  
            face_data = base64.b64encode(face_data).decode('utf-8')  # Convert bytes to Base64 string
        
        # Encrypt face features before saving
        encrypted_data = encrypt_aes_gcm(face_data, AES_KEY)
        
        new_user = {
            "email": email,
            "face_features": encrypted_data["ciphertext"],  
            "iv": encrypted_data["iv"],  
            "auth_tag": encrypted_data["auth_tag"]  
        }
        
        response = supabase.table('Users').insert(new_user).execute()
        
        if isinstance(response, dict) and "error" in response and response["error"]:
            return jsonify({"error": "Database error", "details": response["error"]}), 500
        
        return jsonify({"success": "User was successfully registered"}), 200

def get_user_from_db(email):
    with current_app.app_context():
        supabase = current_app.supabase

        response = supabase.table('Users').select("face_features", "iv", "auth_tag").eq("email", email).execute()

        if not response.data:
            return jsonify({"error": "User not found"}), 404

        user_data = response.data[0]
        ciphertext = user_data["face_features"]
        iv = user_data["iv"]
        auth_tag = user_data["auth_tag"]

        # Decrypt face data
        try:
            decrypted_face_data = decrypt_aes_gcm(ciphertext, AES_KEY, iv, auth_tag)
        except Exception as e:
            return jsonify({"error": "Decryption failed", "details": str(e)}), 500

        return jsonify({
            "email": email,
            "face_features": decrypted_face_data
        }), 200
    

def check_existing_user(email):
    if not email:
        return jsonify({"error": "Email is null"}), 400  
    
    with current_app.app_context():
        supabase = current_app.supabase

        existing_user = supabase.table('Users').select("id").eq("email", email).execute()
        
        if existing_user.data:  
            return jsonify({"error": "Email already taken"}), 409
        
        return jsonify({"success": "Email not in use"}), 200  
    
