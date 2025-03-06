from flask import Blueprint, render_template, jsonify, request, current_app, redirect, url_for, session
from .functionality.detection import detect_face
from .utils.dbUser import save_user_to_db, get_feature_vector_from_db
from .functionality.feature_extraction import extract_feature
from.functionality.verification import compare_faces_euclidean
from deepface.models.facial_recognition import Facenet
import os

face_auth_bp = Blueprint('face_auth_bp', __name__)

new_deepface_home = "flaskr/app/functionality/facenet_weights"
os.makedirs(new_deepface_home, exist_ok=True)
os.environ["DEEPFACE_HOME"] = new_deepface_home

rec_model = Facenet.load_facenet512d_model()

@face_auth_bp.route('/register-face-detection', methods=['POST', 'GET']) 
def register():
    #supabase = current_app.supabase

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
             
                save_user_to_db(email, feature_vector) # Adds new user to database

                session['user'] = email
                return jsonify({'message': 'Successful registration', 'new_image_data': new_image_data, "redirect": url_for('face_auth_bp.account')})

        except Exception as e:
            return jsonify({"error": f"Invalid image data: {str(e)}"}), 400

        return jsonify({'message': 'No face detected'})

    return render_template('register-face-detection.html')



@face_auth_bp.route('/login-face-detection', methods=['POST', 'GET'])
def login():
    #supabase = current_app.supabase

    if request.method == 'POST':
        data = request.get_json()
        
        if 'image' not in data or 'email' not in data:
            return jsonify({'error': 'Missing image or username'}), 400

        try:
            image_data = data['image'] # Webcam image in shape of base64 string        
            email = data['email']

            print("Webcam frame received from " + str(email))

            is_verified = False
            old_feature_vector = get_feature_vector_from_db(email)
            if old_feature_vector is None:
                return jsonify({'message': 'Email is not registered'})
            
            face_data, new_image_data, image_rgb = detect_face(image_data) # Get array containing face data and image with marked faces in shape of base64 string

            if face_data is None:
                return jsonify({'message': 'No face detected'})
                
            new_feature_vector = extract_feature(face_data, image_rgb, rec_model)
            is_verified = compare_faces_euclidean(new_feature_vector, old_feature_vector)

            if is_verified:
                session['user'] = email
                return jsonify({'message': 'Successful login', 'new_image_data': new_image_data, "redirect": url_for('face_auth_bp.account')})

        except Exception as e:
            return jsonify({"error": f"Invalid image data: {str(e)}"}), 400

        return jsonify({'message': 'No face detected'})

    return render_template('login-face-detection.html')



@face_auth_bp.route('/account')
def account():
    if 'user' not in session:
        return redirect(url_for('face_auth_bp.login'))
    return render_template('account.html', username=session['user'])