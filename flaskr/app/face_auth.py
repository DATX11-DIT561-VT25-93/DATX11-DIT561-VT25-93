import json
import uuid
from flask import Blueprint, render_template, jsonify, request, current_app, redirect, url_for, session
import numpy as np
from .functionality.detection import detect_face
from .utils.dbUser import get_user_from_db, save_user_to_db, check_existing_user
from .utils.dbRegisterUser import store_temp_imagedata, get_temp_image_data
from .functionality.feature_extraction import extract_feature
from.functionality.verification import compare_faces_euclidean
from deepface.models.facial_recognition import Facenet

import os


face_auth_bp = Blueprint('face_auth_bp', __name__)

base_dir = os.path.abspath(os.path.dirname(__file__))
new_deepface_home = os.path.join(base_dir, "functionality", "facenet_weights")
os.makedirs(new_deepface_home, exist_ok=True)
os.environ["DEEPFACE_HOME"] = new_deepface_home

rec_model = Facenet.load_facenet512d_model()


# New code
@face_auth_bp.route('/register', methods=['POST', 'GET'])
def pre_register():
    if request.method == 'POST':
        data = request.json  # Receive { "username": "johndoe", "email": "john@example.com" ... etc }

        # Check existing user (checks -> email, might need to update to also check phone number? etc)
        existing_user_check = check_existing_user(data['email'])
                
        if existing_user_check[1] != 200:  
            print("Email already in use.")
            return existing_user_check  
        
        session['user'] = {
            'username': data['username'],
            'email': data['email'],
            'address': data['address'],
            'phone': data['phone'],
            'face_data_id': None,  # Not set yet (set in pre_register_scan),
            'status_logged_in': False 
        }

        return jsonify({"message": "User registered", "next": "/register/scan"})
    return render_template('register.html')

@face_auth_bp.route('/register/scan', methods=['POST', 'GET'])
def pre_register_scan():
    session_user = session['user']
    if 'user' not in session:
        # Redirect to registration start if no session exists
        return redirect(url_for('face_auth_bp.pre_register'))
    
    if session_user['status_logged_in']: # Prevents the user from registering 'again' and getting errors bcs of it
        return redirect(url_for('face_auth_bp.account'))
        
    if request.method == 'POST':
        try:
            data = request.json # Retrieve image data
            temp_id = str(uuid.uuid4())
            store_temp_imagedata(temp_id, data['webcam_data'])

            session_user = session['user']
            session_user['face_data_id'] = temp_id
            session['user'] = session_user
            session.modified = True
            return jsonify({"message": "User face scan registered", "next": "/register/summary"})
        except Exception as e:
            return jsonify({"error": str(e)}), 400
    
    return render_template('register-face-scan.html', user_obj=session['user'])

@face_auth_bp.route('/register/summary', methods=['POST', 'GET'])
def register():
    session_user = session['user']
    if 'user' not in session:
    # Redirect to registration start if no session exists
        return redirect(url_for('face_auth_bp.pre_register'))
    if session_user['status_logged_in']: # Prevents the user from registering 'again' and getting errors bcs of it
        return redirect(url_for('face_auth_bp.account'))
    
    if request.method == 'POST':
        try:
            image_data_id = session_user['face_data_id']
            image_data = get_temp_image_data(image_data_id)
            face_data, new_image_data, image_rgb = detect_face(image_data)
            
            if face_data is not None:
                feature_vector = extract_feature(face_data, image_rgb, rec_model)
                save_user_to_db(session_user['email'], feature_vector)
                session_user['status_logged_in'] = True
                session['user'] = session_user
                session.modified = True
                return jsonify({"message": "Success, user registered", "next": "/account"})
        except Exception as e:
            return jsonify({"error": str(e)}), 400
        
    return render_template('register-summary.html', user_obj=session['user'])

@face_auth_bp.route('/get-face-image', methods=['POST'])
def get_face_image():
    try:
        data = request.json
        image_id = data.get('imageId')
        
        image_data = get_temp_image_data(image_id)
        if not image_data:
            return jsonify({'error': 'Image not found or decryption failed'}), 404

        face_data, new_image_data, image_rgb = detect_face(image_data)
        
        if face_data is None:
            return jsonify({
                'image_data': image_data,
                'warning': 'No face detected in image'
            })
        
        return jsonify({
            'image_data': f'data:image/jpeg;base64,{new_image_data}',
            'face_detected': True
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500



# Old code below, saved to show difference on meeting
@face_auth_bp.route('/register-face-detection', methods=['POST', 'GET']) 
def register_old():
    if request.method == 'POST':
        data = request.get_json()
        
        if 'image' not in data or 'email' not in data:
            return jsonify({'error': 'Missing image or email'}), 400

        try:
            image_data = data['image'] # Webcam image in shape of base64 string        
            email = data['email']

            print("Webcam frame received from " + str(email))
            
            face_data, new_image_data, image_rgb = detect_face(image_data) # Get array containing face data and image with marked faces in shape of base64 string
           
            if face_data is not None:
                feature_vector = extract_feature(face_data, image_rgb, rec_model)
                # Check for existing user
                existing_user_check = check_existing_user(email)
                
                if existing_user_check[1] != 200:  
                    print("Email already in use.")
                    return existing_user_check  

                else:
                    print("user saved")
                    save_user_to_db(email, feature_vector) # Adds new user to database
                    session['user'] = email
                    return jsonify({'message': 'Successful registration', 'new_image_data': new_image_data, "redirect": url_for('face_auth_bp.account')})
      
        except Exception as e:
            return jsonify({"error": f"Invalid image data: {str(e)}"}), 400

        return jsonify({'message': 'No face detected'})

    return render_template('register-face-detection.html')


@face_auth_bp.route('/login-fr', methods=['POST', 'GET'])
def login():

    if request.method == 'POST':
        data = request.get_json()
        
        if 'image' not in data or 'email' not in data:
            return jsonify({'error': 'Missing image or username'}), 400

        try:
            image_data = data['image'] # Webcam image in shape of base64 string        
            email = data['email']

            print("Webcam frame received from " + str(email))
            
            face_data, new_image_data, image_rgb = detect_face(image_data) # Get array containing face data and image with marked faces in shape of base64 string
            
            if face_data is not None:
                response = get_user_from_db(email)  
                
                if response[1] == 200:  
                    user_data = response[0].get_json()  
                    stored_email = user_data.get("email")  
                    stored_face_features = user_data.get("face_features")
                    
                    # Compare webcam face features with stored face features
                    stored_face_features = np.array(json.loads(stored_face_features), dtype=np.float32)
                    webcam_feature_vector = extract_feature(face_data, image_rgb, rec_model)
                    
                    if(not compare_faces_euclidean(webcam_feature_vector, stored_face_features)):
                        return jsonify({"error": f"Face comparison returned false: {str(e)}"}), 400
                    
                    session['user'] = stored_email  # Store session data
                    
                    return jsonify({
                        'message': 'Successful login',
                        'new_image_data': new_image_data,
                        "redirect": url_for('face_auth_bp.account')
                    })
                response = get_user_from_db(email)  
                
                if response[1] == 200:  
                    user_data = response[0].get_json()  
                    stored_email = user_data.get("email")  

                    stored_face_features = user_data.get("face_features")
                    print("apapa2 " + stored_face_features)
                    # Compare webcam face features with stored face features
                    stored_face_features = np.array(json.loads(stored_face_features), dtype=np.float32)
                    webcam_feature_vector = extract_feature(face_data, image_rgb, rec_model)
                    
                    if(not compare_faces_euclidean(webcam_feature_vector, stored_face_features)):
                        return jsonify({"error": f"Face comparison returned false: {str(e)}"}), 400
                    
                    session['user'] = stored_email  # Store session data
                    
                    return jsonify({
                        'message': 'Successful login',
                        'new_image_data': new_image_data,
                        "redirect": url_for('face_auth_bp.account')
                    })

        except Exception as e:
            return jsonify({"error": f"Invalid image data: {str(e)}"}), 400 # TODO: remove str(e) for security

        return jsonify({'message': 'No face detected'})

    return render_template('login.html')



@face_auth_bp.route('/account')
def account():
    if 'user' not in session:
        return redirect(url_for('face_auth_bp.login'))
    return render_template('account.html', username=session['user'])