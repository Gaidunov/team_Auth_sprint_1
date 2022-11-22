from datetime import timedelta

from flask import Flask
from flask import request
from flask_jwt_extended import JWTManager
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor

from src.api.v1 import roles, users
from src.api.v1.doc_spectree import spec
from src.config import (
    DB_CONNECTION_STRING,
    flask_app_settings,
    ENABLE_TRACER,
)
from src.db.manager import db_manager
from src.db.redis_client import redis_cli
from src.flask_commands import commands_bp
from src.limiter_config import (
    configure_limiter,
    LIMITER_SECOND_LIMIT,
)
from src.models import models
from src.tracer import configure_tracer


def create_app() -> Flask:
    configure_tracer()
    app = Flask(__name__)
    FlaskInstrumentor().instrument_app(app)
    limiter = configure_limiter(app)

    @limiter.limit(limit_value=LIMITER_SECOND_LIMIT)
    @app.before_request
    def before_request():
        request_id = request.headers.get('X-Request-Id')
        if not request_id:
            raise RuntimeError('request id is required')

        if ENABLE_TRACER:
            tracer = trace.get_tracer(__name__)
            span = tracer.start_span(name='api-request')
            span.set_attribute('http.request_id', request_id)
            span.end()

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

    return app
