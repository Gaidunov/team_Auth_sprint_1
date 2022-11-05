from datetime import timedelta

from dotenv import load_dotenv
from flask import Flask
from flask_jwt_extended import JWTManager

from src.api.v1 import roles, users
from src.config import flask_app_settings
from src.db.db import create_db
from src.db.manager import db_manager
from src.db.redis_client import redis_cli
from src.flask_commands import commands_bp
from src.models import models

load_dotenv()

 
def create_app():
    app = Flask(__name__)
    # app.config['SQLALCHEMY_DATABASE_URI'] = flask_app_settings.database_uri
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///API_DB.db?check_same_thread=False'
    with app.app_context():
        create_db() 
        models.db.init_app(app)
        models.db.create_all()
        db_manager.utils.prepopulate_db()  # добавяет дефолтные роли в БД

    app.config['JWT_SECRET_KEY'] = 'secret'
    app.config['JWT_TOKEN_LOCATION'] = ['headers', 'cookies']
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(
        # minutes=int(flask_app_settings.jwt_access_token_ttl)
        minutes=10
    )
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(
        # minutes=int(flask_app_settings.jwt_refresh_token_ttl)
        minutes=43800
    )
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False

    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_is_revoked(jwt_header, jwt_payload: dict):
        """база просроченных токенов"""
        jti = jwt_payload["jti"]
        token_in_redis = redis_cli.get(jti)
        return token_in_redis is not None

    app.register_blueprint(users.routes, url_prefix='/api/v1/users/')
    app.register_blueprint(roles.routes, url_prefix='/api/v1/roles/')
    app.register_blueprint(commands_bp)

    return app
