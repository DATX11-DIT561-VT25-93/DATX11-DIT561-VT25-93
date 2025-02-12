from flask import Flask
from config import Config
from supabase import create_client

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize Supabase
    app.supabase = create_client(app.config['SUPABASE_URL'], app.config['SUPABASE_KEY'])

    from app.routes import main
    app.register_blueprint(main)

    return app
