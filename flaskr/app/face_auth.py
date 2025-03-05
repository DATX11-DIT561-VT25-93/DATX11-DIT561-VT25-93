from flask import Blueprint, render_template, jsonify, request, current_app, redirect, url_for, session
from .functionality.detection import detect_face
from .utils.dbUser import save_user_to_db


face_auth_bp = Blueprint('face_auth_bp', __name__)


@face_auth_bp.route('/register-face-detection', methods=['POST', 'GET']) 
def register():
    supabase = current_app.supabase
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
                existing_user = supabase.table('registered_users_detection').select("id").eq("email", email).execute()
                
                if existing_user.data:

                    print("Email already in use.")
                    return jsonify({"error": "Email already taken"}), 409, 
                else:
                    print("user saved")
                    save_user_to_db(email, face_data) # Adds new user to database
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
            
            face_data, new_image_data, image_rgb = detect_face(image_data) # Get array containing face data and image with marked faces in shape of base64 string
            
            if face_data is not None:
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