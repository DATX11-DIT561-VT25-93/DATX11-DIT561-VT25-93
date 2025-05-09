from flask import Blueprint, render_template, jsonify, request, current_app, redirect, url_for, session

# RENAME FILE to 'password_auth.py'

password_auth_bp = Blueprint('password_auth_bp', __name__)

@password_auth_bp.route('/')
def home():
    return render_template('index.html')

@password_auth_bp.route('/planets')
def get_planets():
    supabase = current_app.supabase
    response = supabase.table('test_planets').select("description").execute()
    return jsonify(response.data)

@password_auth_bp.route('/login', methods=['POST', 'GET'])
def login():
    supabase = current_app.supabase

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400

        # Fetch user from database
        user_response = supabase.table('registered_users').select("password").eq("username", username).execute()

        if not user_response.data:
            return jsonify({"error": "Invalid username or password"}), 401

        stored_password = user_response.data[0]["password"]

        # Verify password
        if not stored_password:
            return jsonify({"error": "Invalid username or password"}), 401
        elif stored_password != password:
            return jsonify({"error": "Invalid username or password"}), 401
            

        session['user'] = username  # Store user in session  (this way we can retrive user information like username and display it)
        
        # Redirect to account page (success)
        return redirect(url_for('face_auth_bp.account'))

    return render_template('login-face-detection.html')

@password_auth_bp.route('/logout')
def logout():
    session.pop('user', None)  # Remove user from session
    return redirect(url_for('face_auth_bp.login_fr'))

@password_auth_bp.route('/account')
def account():
    if 'user' not in session or not session['user']['status_logged_in']:
        return redirect(url_for('face_auth_bp.login_fr'))
    
    return render_template('account.html', user_obj=session['user'])
