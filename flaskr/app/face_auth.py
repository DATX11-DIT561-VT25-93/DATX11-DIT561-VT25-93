from flask import Blueprint, render_template, jsonify, request, current_app, redirect, url_for, session
from .functionality.detection import detect_face
from .utils.dbUser import save_user_to_db, check_existing_user, get_user_from_db
from .functionality.feature_extraction import extract_feature, init_facenet
from.functionality.verification import compare_faces_euclidean
import numpy as np
import json


face_auth_bp = Blueprint('face_auth_bp', __name__)

rec_model = init_facenet()

@face_auth_bp.route('/register-face-detection', methods=['POST', 'GET']) 
def register():
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



@face_auth_bp.route('/login-face-detection', methods=['POST', 'GET'])
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

        except Exception as e:
            return jsonify({"error": f"Invalid image data: {str(e)}"}), 400

        return jsonify({'message': 'No face detected'})

    return render_template('login-face-detection.html')



@face_auth_bp.route('/account')
def account():
    if 'user' not in session:
        return redirect(url_for('face_auth_bp.login'))
    return render_template('account.html', username=session['user'])