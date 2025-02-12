from flask import Blueprint, render_template, jsonify, request, current_app

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('index.html')


@main.route('/planets')
def get_planets():
    supabase = current_app.supabase
    response = supabase.table('test_planets').select("name").execute()
    return jsonify(response.data)

@main.route('/sign_in', methods=['POST', 'GET'])
def sign_in():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Needs login functionality
        msg = 'Login attempt for ' + str(username)
        return msg
    return 'This is the login page'

@main.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Needs registration functionality
        msg = 'Registration attempt for user ' + str(username)
        return msg
    return 'This is the registration page'


# For later
@main.route('/frame', methods=['POST'])
def handle_frame():
    #frame = request...
    return 'Frame handled'

