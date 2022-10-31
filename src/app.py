import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()
from flask import Flask
from flask_jwt_extended import JWTManager

#Views
from src.api.v1 import movies, roles, users
from src.db.db import create_db
from src.db.redis_client import redis_cli
from src.models import models


def main():

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URI']
    with app.app_context():
        create_db()
        models.db.init_app(app) 
        models.db.create_all()
        
    app.config["JWT_SECRET_KEY"] = "secret"  
    app.config['JWT_TOKEN_LOCATION'] = ['headers', 'cookies']
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=os.environ['JWT_ACCESS_TOKEN_EXPIRES'])
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(minutes=os.environ['JWT_REFRESH_TOKEN_EXPIRES'])
    app.config["JWT_COOKIE_CSRF_PROTECT"] = False
 
    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_is_revoked(jwt_header, jwt_payload: dict):
        """база просроченных токенов"""
        jti = jwt_payload["jti"]
        token_in_redis = redis_cli.get(jti)
        return token_in_redis is not None

    app.register_blueprint(users.routes, url_prefix='/api/v1/users/')
    app.register_blueprint(movies.routes, url_prefix='/api/v1/movies/')
    app.register_blueprint(roles.routes, url_prefix='/api/v1/roles/')
    
    app.run(debug=True)


if __name__ == '__main__':
    main() 
