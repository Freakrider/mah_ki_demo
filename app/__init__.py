from flask import Flask
from flask_cors import CORS
from app.config import Config
from app.routes import register_routes

def create_app():
    print("Creating app")
    app = Flask(__name__,)
    app.config.from_object(Config)
    CORS(app, supports_credentials=True)
    register_routes(app)
    return app
