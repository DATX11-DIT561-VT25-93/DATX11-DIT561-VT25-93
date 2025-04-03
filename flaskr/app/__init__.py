import datetime
from flask import Flask, render_template
from config import Config
from supabase import create_client

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(minutes=30)

    # Initialize Supabase
    app.supabase = create_client(app.config['SUPABASE_URL'], app.config['SUPABASE_KEY'])

    from app.routes import password_auth_bp
    app.register_blueprint(password_auth_bp)
    app.secret_key = "super_secret_move to .env"

    from app.face_auth import face_auth_bp
    app.register_blueprint(face_auth_bp)


    return app

