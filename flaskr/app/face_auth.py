from flask import Blueprint, render_template, jsonify, request, current_app, redirect, url_for, session
from .functionality.detection import detect_face


face_auth_bp = Blueprint('face_auth_bp', __name__)

@face_auth_bp.route('/register-face-detection', methods=['POST', 'GET']) 
def register():
    #supabase = current_app.supabase
    if request.method == 'POST':
        data = request.get_json()
        
        if 'image' not in data or 'username' not in data:
            return jsonify({'error': 'Missing image or username'}), 400

        try:
            image_data = data['image'] # Webcam image in shape of base64 string        
            username = data['username']

            print("Webcam frame received from " + str(username))
            
            face_data, new_image_data = detect_face(image_data) # Get array containing face data and image with marked faces in shape of base64 string
            
            if face_data is not None:
                return jsonify({'message': 'Face detected', 'new_image_data': new_image_data})

        except Exception as e:
            return jsonify({"error": f"Invalid image data: {str(e)}"}), 400

        return jsonify({'message': 'No face detected'})

    return render_template('register-face-detection.html')



@face_auth_bp.route('/login-face-detection', methods=['POST', 'GET'])
def login():
    #supabase = current_app.supabase

    if request.method == 'POST':
        data = request.get_json()
        
        if 'image' not in data or 'username' not in data:
            return jsonify({'error': 'Missing image or username'}), 400

        try:
            image_data = data['image'] # Webcam image in shape of base64 string        
            username = data['username']

            print("Webcam frame received from " + str(username))
            
            face_data, new_image_data = detect_face(image_data) # Get array containing face data and image with marked faces in shape of base64 string
            
            if face_data is not None:
                return jsonify({'message': 'Face detected', 'new_image_data': new_image_data})

        except Exception as e:
            return jsonify({"error": f"Invalid image data: {str(e)}"}), 400

        return jsonify({'message': 'No face detected'})

    return render_template('login-face-detection.html')