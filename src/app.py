from datetime import timedelta

from flask import Flask, url_for
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from src.api.v1.doc_spectree import spec

from src.api.v1 import roles, users
from src.db.manager import db_manager
from src.db.redis_client import redis_cli
from src.flask_commands import commands_bp
from src.models import models
from src.config import (
    DB_CONNECTION_STRING,
    flask_app_settings,
    redis_settings,
)
from src.tracer import configure_tracer
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from flask import request
from opentelemetry import trace


def create_app() -> Flask:
    configure_tracer()
    app = Flask(__name__)
    FlaskInstrumentor().instrument_app(app)

    limiter = Limiter(
        app,
        key_func=get_remote_address,
        default_limits=["100 per minute", "1 per second"],
        storage_uri=f"redis://:{redis_settings.password}@redis:{redis_settings.port}/3",
        strategy="fixed-window",  # or "moving-window"
    )

    @limiter.limit(limit_value='1 per second')
    @app.before_request
    def before_request():
        request_id = request.headers.get('X-Request-Id')
        if not request_id:
            raise RuntimeError('request id is required')

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

    @app.route('/api/pizda')
    def test():
        return 'ok'

    def has_no_empty_params(rule):
        defaults = rule.defaults if rule.defaults is not None else ()
        arguments = rule.arguments if rule.arguments is not None else ()
        return len(defaults) >= len(arguments)

    @app.route("/api/site-map")
    def site_map():
        links = []
        for rule in app.url_map.iter_rules():
            # Filter out rules we can't navigate to in a browser
            # and rules that require parameters
            if "GET" in rule.methods and has_no_empty_params(rule):
                url = url_for(rule.endpoint, **(rule.defaults or {}))
                links.append((url, rule.endpoint))

        for link in links:
            print(link)

        return links

    return app
