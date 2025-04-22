import uuid
from flask import Blueprint, render_template, jsonify, request, current_app, redirect, url_for, session
from datetime import datetime, timezone, timedelta
import json
from .utils.dbUser import check_existing_email_or_username, check_existing_username, get_user_from_db, save_user_to_db, check_existing_email
from .utils.userOTP import generate_otp, verify_otp



OTP_bp = Blueprint('bp_OTP', __name__)

@OTP_bp.before_request
def check_otp_session_expiry():
    otp_session = session.get('otp_session')
    if otp_session:
        expiry_str = otp_session.get('expires_at')
        if expiry_str:
            expiry = datetime.fromisoformat(expiry_str)
            if datetime.utcnow() > expiry:
                session.pop('otp_session', None)

@OTP_bp.route('/login-otp')
def route_render_template():
    return render_template("login_otp.html")


@OTP_bp.route('/generate-otp', methods=['POST'])
def route_generate_otp():
    data = request.get_json()
    session_id =  str(uuid.uuid4())
    user_email = data.get('email')

    if not user_email:
        return jsonify({'error': 'Wrong email or account does not exist'}), 400

    try:
        generate_otp(session_id, user_email)

        session['otp_session'] = {
            'session_id': session_id,
            'email': user_email,
            'expires_at': (datetime.utcnow() + timedelta(minutes=5)).isoformat()
        }

        return jsonify({'message': 'OTP generated and sent'}), 200
    except Exception as e:
        print(f"Error generating OTP: {e}")
        return jsonify({'error': 'Failed to generate OTP'}), 500


@OTP_bp.route('/verify-otp', methods=['POST'])
def route_verify_otp():
    data = request.get_json()
    typed_otp = data.get('otp')

    otp_session = session.get('otp_session')
    if not otp_session:
        return jsonify({'error': 'No active OTP session'}), 400

    session_id = otp_session.get('session_id')
    email = otp_session.get('email')
    response_get_user = get_user_from_db(email)

    if response_get_user[1] == 200:  
                user_data = response_get_user[0].get_json()  
                stored_email = user_data.get("email")  
                stored_username = user_data.get("username")

    if not session_id or not typed_otp:
        return jsonify({'error': 'OTP and session are required'}), 400

    try:
        if verify_otp(session_id, typed_otp):
            # OTP success: cleanup session and add user to session
            session.pop('otp_session', None)
            session['user'] = {
                'username': stored_username,
                'email': stored_email,
                'status_logged_in': True 
                }
            return jsonify({'message': 'OTP verified'}), 200
        else:
            return jsonify({'error': 'Invalid or expired OTP'}), 401
    except Exception as e:
        print(f"Error verifying OTP: {e}")
        return jsonify({'error': 'OTP verification failed'}), 500