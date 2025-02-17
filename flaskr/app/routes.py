from flask import Blueprint, render_template, jsonify, request, current_app

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('index.html')

@main.route('/planets')
def get_planets():
    supabase = current_app.supabase
    response = supabase.table('test_planets').select("description").execute()
    return jsonify(response.data)

@main.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        data = request.get_json()

        if not data:
            return jsonify({"error": "No JSON data received"}), 400
        
        username = data.get('username')
        password = data.get('password')

        if not username:
            return jsonify({"error": "Username is required"}), 400
        elif not password:
            return jsonify({"error": "Password is required"}), 400
        
        # TODO: Check if username password combination exists in DB. Return appropriate messages for incorrect username and password, respectively.
        # TODO: Add redirect for successfull sign in attempt

        return jsonify({"message": f"Sign in attempt for user {username}"})
        #return render_template('login.html')

    return 'This is the login page'
    #return render_template('login.html')

# TODO: Implement logout function below
@main.route('/logout')
def logout():
    return 'This is the logout page'

@main.route('/register', methods=['POST', 'GET'])
def register():
    supabase = current_app.supabase

    if request.method == 'POST':
        data = request.get_json()

        if not data:
            return jsonify({"error": "No JSON data received"}), 400
        
        username = data.get('username')
        password = data.get('password')

        if not username:
            return jsonify({"error": "Username is required"}), 400
        elif not password:
            return jsonify({"error": "Password is required"}), 400
        
        new_user = {
            "username": data.get("username"),
            "password": data.get("password") 
            # TODO: Hash the password before storing
        }
        
        # Insert new user into Supabase
        response = supabase.table('registered_users').insert(new_user).execute()
        # TODO: Handle case where user already exists

        return jsonify({"message": "User added successfully", "data": response.data}), 201
        #return render_template('register.html')

    # Get registered users
    response = supabase.table('registered_users').select("username").execute()

    return jsonify(response.data)
    #return render_template('register.html')


# For later
@main.route('/frame', methods=['POST'])
def handle_frame():
    #frame = request...
    return 'Frame handled'

