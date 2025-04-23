from datetime import datetime, timezone, timedelta
import json
import uuid
from flask import Blueprint, render_template, jsonify, request, current_app, redirect, url_for, session
import numpy as np
from .functionality.detection import detect_face
from .utils.dbUser import check_existing_email_or_username, check_existing_username, get_user_from_db, save_user_to_db, check_existing_email
from .utils.dbRegisterUser import store_temp_imagedata, get_temp_image_data
from .functionality.feature_extraction import extract_feature, init_facenet
from .functionality.verification import compare_faces_euclidean
from .functionality.anti_spoof import load_antispoof_model
from deepface.models.facial_recognition import Facenet
from user_agents import parse

import os


face_auth_bp = Blueprint('face_auth_bp', __name__)

rec_model = init_facenet()
antispoof_sess, antispoof_input = load_antispoof_model()

rec_model = Facenet.load_facenet512d_model()


@face_auth_bp.route('/account')
def account():
    if 'user' not in session or not session['user']['status_logged_in']:
        return redirect(url_for('face_auth_bp.login_fr'))

    try:
        supabase = current_app.supabase
        user_in_session = session.get('user', {})
        user_id = user_in_session.get('id')

        if not user_id:
            return redirect(url_for('face_auth_bp.login_fr'))

        # Fetch logs from Supabase
        response = (
            supabase.table("timelog")
            .select("*")
            .eq("id", user_id)
            .order("created_at", desc=True)  # Order by timestamp ascending
            .execute()
        )

        logs_raw = response.data

        # Format the logs for display (optional cleanup / renaming)
        logs = []

        for log in logs_raw:
            logs.append({
                'event': log.get('event'),
                'created_at': datetime.fromisoformat(log.get('created_at')).strftime('%Y-%m-%d %H:%M:%S'),
                'device': log.get('device'),
            })

        return render_template('account.html', user_obj=session['user'], logs=logs)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# New code
@face_auth_bp.route('/register', methods=['POST', 'GET'])
def pre_register():
    if request.method == 'POST':
        data = request.json  # Receive { "username": "johndoe", "email": "john@example.com" ... etc }

        # Check existing user
        existing_email_check = check_existing_email(data['email'])
        existing_username_check = check_existing_username(data['username'])

        if existing_email_check[1] != 200:  
            print("Email already in use.")
            return existing_email_check  
        if existing_username_check[1] != 200:  
            print("Username already in use.")
            return existing_username_check  
        
        session['user'] = {
            'username': data['username'],
            'email': data['email'],
            'face_data_id': str(uuid.uuid4()),
            'status_logged_in': False 
        }
        session['registration_start_time'] = datetime.now(timezone.utc).timestamp()
        session.modified = True

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
            store_temp_imagedata(session_user['face_data_id'], data['webcam_data'])
            session_user = session['user']
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
                print("Hello")
                feature_vector = extract_feature(face_data, image_rgb, rec_model, antispoof_sess, antispoof_input)
                if feature_vector is not None:
                    print("Hello2")
                    save_user_to_db(session_user['email'], feature_vector, session_user['username'])
                    session_user['status_logged_in'] = True
                    session['user'] = session_user
                    session.modified = True
                    response = get_user_from_db(session_user['email'])

                    user_data = response[0].get_json()  
                    stored_email = user_data.get("email")  
                    stored_username = user_data.get("username")
                    stored_user_id=user_data.get("id")

                    session['user'] = {
                        'username': stored_username,
                        'email': stored_email,
                        'status_logged_in': True, 
                        'id': stored_user_id
                    }  # Store session data
                    session.modified = True


                    log_event('register')
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
    

@face_auth_bp.route('/check-session-status', methods=['GET']) # Client side check
def check_session_status():
    if 'registration_start_time' in session and 'user' in session:
        start_time = session.get('registration_start_time')
        current_time = datetime.now(timezone.utc).timestamp()
        elapsed_time = current_time - start_time
        
        if elapsed_time > (10 * 60):  # 10 minute timeout
            # Clear session
            session.pop('user', None)
            session.pop('registration_start_time', None)
            return jsonify({'expired': True})
    
    return jsonify({'expired': False})

@face_auth_bp.before_request # Server side check
def check_registration_timeout():
    if request.path.startswith('/register') and request.path != '/register':  # Don't check on initial register page
        if 'registration_start_time' not in session or 'user' not in session:
            return redirect(url_for('face_auth_bp.pre_register'))
        
        start_time = session.get('registration_start_time')
        current_time = datetime.now(timezone.utc).timestamp()
        elapsed_time = current_time - start_time
        
        if elapsed_time > (10 * 60):  # 10 minute timeout
            session.pop('user', None)
            session.pop('registration_start_time', None)
            return redirect(url_for('face_auth_bp.pre_register'))

@face_auth_bp.route('/login-fr', methods=['POST', 'GET'])
def login_fr():

    if request.method == 'POST':
        data = request.get_json()

        email_username = data['email_username']
        
        if 'image' not in data or 'email_username' not in data:
            return jsonify({'error': 'Missing image or username'}), 400

        try:
            image_data = data['image'] # Webcam image in shape of base64 string        

            print("Webcam frame received from " + str(email_username))
            
            face_data, new_image_data, image_rgb = detect_face(image_data) # Get array containing face data and image with marked faces in shape of base64 string
            
            if face_data is not None:
                response = get_user_from_db(email_username)  
                
                if response[1] == 200:  
                    user_data = response[0].get_json()  
                    stored_email = user_data.get("email")  
                    stored_username = user_data.get("username")
                    stored_face_features = user_data.get("face_features")
                    stored_user_id=user_data.get("id")
                    
                    # Compare webcam face features with stored face features
                    stored_face_features = np.array(json.loads(stored_face_features), dtype=np.float32)
                    webcam_feature_vector = extract_feature(face_data, image_rgb, rec_model, antispoof_sess, antispoof_input)
                    print("Hello")
                    if webcam_feature_vector is not None:
                        print("Hello2")
                        if(not compare_faces_euclidean(webcam_feature_vector, stored_face_features)):
                            return jsonify({"error": f"Face comparison returned false: {str(e)}"}), 400
                        
                        # Store logged in user in session
                        if 'user' in session:
                            session.pop('user', None)

                        session['user'] = {
                            'username': stored_username,
                            'email': stored_email,
                            'status_logged_in': True, 
                            'id': stored_user_id
                        }  # Store session data
                        session['registration_start_time'] = datetime.now(timezone.utc).timestamp()
                        session.modified = True
                        log_event('login')

                        return jsonify({
                            'message': 'Successful login',
                            'new_image_data': new_image_data,
                            "redirect": "/account"
                        })

        except Exception as e:
            return jsonify({"error": f"Invalid image data: {str(e)}"}), 400 # TODO: remove str(e) for security

        return jsonify({'message': 'No face detected'})

    return render_template('login.html')

@face_auth_bp.route('/check-credentials', methods=['POST'])
def check_credentials():
    data = request.get_json()
    email_username = data.get('email_username')
    
    if not email_username:
        return jsonify({'error': 'Email or username is required'}), 400
        
    try:
        # Check if user exists in database
        if( not check_existing_email_or_username(email_username) ):
            return jsonify({'error': 'No account found with this email or username'}), 404 
            
        return jsonify({'message': 'Valid credentials'}), 200
        
    except Exception as e:
        return jsonify({'error': 'Error checking credentials'}), 500

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
            username = data['username']

            print("Webcam frame received from " + str(email))
            
            face_data, new_image_data, image_rgb = detect_face(image_data) # Get array containing face data and image with marked faces in shape of base64 string
           
            if face_data is not None:
                feature_vector = extract_feature(face_data, image_rgb, rec_model)
                # Check for existing user
                existing_user_check = check_existing_email(email)
                
                if existing_user_check[1] != 200:  
                    print("Email already in use.")
                    return existing_user_check  

                else:
                    print("user saved")
                    save_user_to_db(email, feature_vector, username) # Adds new user to database
                    session['user'] = email
                    return jsonify({'message': 'Successful registration', 'new_image_data': new_image_data, "redirect": url_for('face_auth_bp.account')})
      
        except Exception as e:
            return jsonify({"error": f"Invalid image data: {str(e)}"}), 400

        return jsonify({'message': 'No face detected'})

    return render_template('register-face-detection.html')


@face_auth_bp.route('/update_username', methods=['POST', 'GET'])
def update_username():
    if request.method == 'POST':

        try:
            
            supabase = current_app.supabase

            user_in_session = session['user']
            user_id = user_in_session['id']
            old_username = user_in_session['username']
            new_username = request.form['username']
            old_email = user_in_session['email']

            existing_username_check = check_existing_username(new_username)

            if existing_username_check[1] != 200:  
                return redirect(url_for('face_auth_bp.account'))

            updated_user = (
                supabase.table("Users")
                .update({"username": new_username})
                .eq("username", old_username)
                .execute()
            )

            log_event('updated username')

            session['user'] = {
                            'username': new_username,
                            'email': old_email,
                            'status_logged_in': True, 
                            'id': user_id
                        }  # Store session data
            
            
            return redirect(url_for('face_auth_bp.account')) 

        except Exception as e:
            return jsonify({"Error": str(e)}), 500
        
    return redirect(url_for('face_auth_bp.account'))


@face_auth_bp.route('/update_email', methods=['POST', 'GET'])
def update_email():
    
    try:

        supabase = current_app.supabase

        user_in_session = session['user']
        user_id = user_in_session['id']
        old_username = user_in_session['username']
        old_email = user_in_session['email']
        new_email = request.form['email']

        existing_email_check = check_existing_email(new_email)

        if existing_email_check[1] != 200:  
            return render_template("account.html", user_obj=session['user'])
        
        updated_user = (
            supabase.table("Users")
            .update({"email": new_email})
            .eq("email", old_email)
            .execute()
        )

        log_event('updated email')

        session['user'] = {
                        'username': old_username,
                        'email': new_email,
                        'status_logged_in': True, 
                        'id': user_id
                    }  # Store session data
        
        return redirect(url_for('face_auth_bp.account')) 
    
    except Exception as e:
        return jsonify({"Error": str(e)}), 500
    


@face_auth_bp.route('/delete-user', methods=['POST', 'GET'])
def delete_user():
    
    try:

        user_in_session = session['user']
        username = user_in_session['username']
        user_id = user_in_session['id']

        if not username:
            return jsonify({"Error": "Username Not Provided."}), 400

        supabase = current_app.supabase

        # Delete the user's timelog
        deleted_timelog = (
            supabase.table("timelog")
            .delete()
            .eq("id", user_id)
            .execute()
        )

        # Delete The User 
        deleted_user = (
            supabase.table("Users")
            .delete()
            .eq("username", username)
            .execute()
        )

        return redirect('/')


    except Exception as e:
        return jsonify({"Error": str(e)}), 500



def log_event(event):
    try:
        supabase = current_app.supabase

        user_in_session = session.get('user', {})
        user_id = user_in_session.get('id')

        user_agent_string = request.headers.get('User-Agent', 'Unknown')
        user_agent = parse(user_agent_string)

        if user_agent.is_mobile:
            device_type = 'mobile'
        elif user_agent.is_tablet:
            device_type = 'tablet'
        elif user_agent.is_pc:
            device_type = 'desktop'
        elif user_agent.is_bot:
            device_type = 'bot'
        else:
            device_type = 'unknown'


        supabase.table("timelog").insert({
            "id": user_id,
            "event": event,
            "device": device_type
        }).execute()
        
    except Exception as e:
        print(f"[LOGGING ERROR]: {e}")