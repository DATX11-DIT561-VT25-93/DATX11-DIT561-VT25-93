from flask import Blueprint, render_template, jsonify, request, current_app, redirect, url_for, session
from .functionality.detection import detect_face
from .utils.dbUser import save_user_to_db, check_existing_user
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
@face_auth_bp.route('/register/scan', methods=['POST', 'GET'])
def register_scan():
    return render_template('register-face-scan.html', user_obj = session['user'])

@face_auth_bp.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        data = request.json  # Receive { "username": "johndoe", "email": "john@example.com" }
        
        session['user'] = {
            'username': data['username'],
            'email': data['email'],
            'address': data['address'],
            'phone': data['phone'],
            'biometric_data': None  # Not set yet
        }

        return jsonify({"message": "User registered", "next": "/register/scan"})
    return render_template('register.html')



# Old code below?

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
                # Check for existing user
                existing_user_check = check_existing_user(email)
                print("apapa")
                
                if existing_user_check[1] == 409:  
                    pass
                else: 
                    return existing_user_check  
                
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