from datetime import timedelta

from flask import Flask
from flask_jwt_extended import JWTManager
from src.api.v1.doc_spectree import spec

from src.api.v1 import roles, users
from src.db.manager import db_manager
from src.db.redis_client import redis_cli
from src.flask_commands import commands_bp
from src.models import models
from src.config import (
    DB_CONNECTION_STRING,
    flask_app_settings,
)


def create_app() -> Flask:
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = DB_CONNECTION_STRING
    models.db.init_app(app)
    db_manager.utils.prepopulate_db()  # добавяет дефолтные роли в БД

    app.config['JWT_SECRET_KEY'] = 'secret'
    app.config['JWT_TOKEN_LOCATION'] = ['headers', 'cookies']
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(
        minutes=int(flask_app_settings.jwt_access_token_ttl)
    )
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(
        minutes=int(flask_app_settings.jwt_refresh_token_ttl)
    )
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False

    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_is_revoked(jwt_header, jwt_payload: dict):
        """база просроченных токенов"""
        jti = jwt_payload["jti"]
        token_in_redis = redis_cli.get(jti)
        return token_in_redis is not None
 
    spec.register(app)

    app.register_blueprint(users.routes, url_prefix='/api/v1/users/')
    app.register_blueprint(roles.routes, url_prefix='/api/v1/roles/')
    app.register_blueprint(commands_bp)

    @app.route('/')
    def test():
        return 'ok'

    return app

