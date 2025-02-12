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

