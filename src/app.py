from dotenv import load_dotenv
import os
from datetime import timedelta, datetime, timezone
load_dotenv()

from flask import Flask
from flask_jwt_extended import (JWTManager,
                                set_access_cookies,
                                verify_jwt_in_request,
                                get_jwt, 
                                get_jwt_identity,
                                create_access_token,
                                create_refresh_token
                                )


from src.db.db import db_session, create_db
from src.models import models 

#Views
from src.api.v1 import users, movies


def main():

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URI']
    with app.app_context():
        create_db()
        models.db.init_app(app) 
        models.db.create_all()
        
    app.config["JWT_SECRET_KEY"] = "secret"  
    app.config['JWT_TOKEN_LOCATION'] = ['headers', 'cookies']
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
    # TODO: надо понять, почему без этого защищенные вьюхи отдают "msg": "CSRF double submit tokens do not match" 
    app.config["JWT_COOKIE_CSRF_PROTECT"] = False

    jwt = JWTManager(app)

    app.register_blueprint(users.routes, url_prefix='/api/v1/users/')
    app.register_blueprint(movies.routes, url_prefix='/api/v1/movies/')
    

    app.run()


if __name__ == '__main__':
    main() 