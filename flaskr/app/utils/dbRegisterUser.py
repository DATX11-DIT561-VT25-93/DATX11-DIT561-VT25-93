
import uuid
import numpy as np
import base64
from flask import jsonify, request, current_app
from dotenv import load_dotenv
from .crypto_utils import encrypt_aes_gcm, decrypt_aes_gcm
import os
import json

load_dotenv()
AES_KEY = bytes.fromhex(os.getenv("AESGCM_SECRET_KEY"))

# TODO: encrypt before storing

def store_temp_imagedata(temp_id, image_data):
    with current_app.app_context():
        supabase = current_app.supabase
        try: 
            supabase.table('temp_image_data').insert({
                'uuid': temp_id,
                'image_data': image_data
            }).execute()
        except Exception as e:
            print("dbRegisterUser store_temp_imagedata() returned error: " + e)
            return jsonify({"error": "Error storing temp image"}), 500    

        return jsonify({"message": "Success, temp image stored in db"}), 200
    
def get_temp_image_data(face_data_id):
    with current_app.app_context():
        supabase = current_app.supabase
        try:
            result = supabase.table('temp_image_data').select('image_data').eq('uuid', face_data_id).execute()
            if result.data:
                return result.data[0]['image_data']
        except Exception as e:
            print("dbRegisterUser get_temp_imagedata() returned error: " + e)
            return jsonify({"error": "Error retrieving temp image: " + e}), 500
        
        return jsonify({"error": "Error retrieving temp image"}), 500
    
