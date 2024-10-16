from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import redis
from dotenv import load_dotenv
import os
import ast
from datetime import timedelta


load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
ma = Marshmallow()
jwt = JWTManager()
redis_client = redis.Redis(host='127.0.0.1', port=6379, db=1, decode_responses=True)


def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    jwt_access_expires = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES'))
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(seconds=jwt_access_expires)
    jwt_refresh_expires = int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES', 604800))
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(seconds=jwt_refresh_expires)
    jwt_token_location = os.getenv('JWT_TOKEN_LOCATION', "['headers']")
    try:
        app.config['JWT_TOKEN_LOCATION'] = ast.literal_eval(jwt_token_location)
    except (ValueError, SyntaxError):
        app.config['JWT_TOKEN_LOCATION'] = ['headers']
    app.config['JWT_COOKIE_SECURE'] = os.getenv('JWT_COOKIE_SECURE')
    app.config['JWT_COOKIE_CSRF_PROTECT'] = os.getenv('JWT_COOKIE_CSRF_PROTECT')
    app.config['JWT_ACCESS_COOKIE_PATH'] = os.getenv('JWT_ACCESS_COOKIE_PATH')
    app.config['JWT_REFRESH_COOKIE_PATH'] = os.getenv('JWT_REFRESH_COOKIE_PATH')

    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})
    jwt.init_app(app)

    from .routes import init_app as init_routes
    init_routes(app)

    from .models import models

    return app
