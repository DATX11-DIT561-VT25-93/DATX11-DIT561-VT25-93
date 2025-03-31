
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

def store_temp_imagedata(temp_id, image_data):
    with current_app.app_context():
        supabase = current_app.supabase
        try: 
            encrypted_data = encrypt_aes_gcm(image_data, AES_KEY)
        
            new_db_entry = {
                "uuid": temp_id,
                "image_data": encrypted_data["ciphertext"],  
                "iv": encrypted_data["iv"],  
                "auth_tag": encrypted_data["auth_tag"]  
            }

            supabase.table('temp_image_data').insert(new_db_entry).execute()
        except Exception as e:
            print("dbRegisterUser store_temp_imagedata() returned error: " + e)
            return jsonify({"error": "Error storing temp image"}), 500    

        return jsonify({"message": "Success, temp image stored in db"}), 200
    
def get_temp_image_data(face_data_id):
    with current_app.app_context():
        supabase = current_app.supabase
        try:
            result = supabase.table('temp_image_data').select('image_data', 'iv', 'auth_tag').eq('uuid', face_data_id).execute()

            if result.data:
                db_response = result.data[0]
                ciphertext = db_response["image_data"]
                iv = db_response["iv"]
                auth_tag = db_response["auth_tag"]
                
                try:
                    decrypted_data = decrypt_aes_gcm(ciphertext, AES_KEY, iv, auth_tag)
                    print(decrypted_data[:50])
                    return decrypted_data
                except Exception as e:
                    print(e)
                    return None
            return None
        except Exception as e:
            print("dbRegisterUser get_temp_imagedata() returned error: " + e)
            return None
