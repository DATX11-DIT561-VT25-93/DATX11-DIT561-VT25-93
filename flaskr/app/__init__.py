from flask import Flask
from config import Config
from supabase import create_client

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize Supabase
    app.supabase = create_client(app.config['SUPABASE_URL'], app.config['SUPABASE_KEY'])

    from app.routes import password_auth_bp
    app.register_blueprint(password_auth_bp)

    from app.face_auth import face_auth_bp
    app.register_blueprint(face_auth_bp)

    return app
