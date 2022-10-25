from dotenv import load_dotenv
import os

load_dotenv()

from flask import Flask
from flask_jwt_extended import JWTManager


from src.db.db import db_session, create_db
from src.models import models 

#Views
from src.api.v1 import users


def main():

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URI']
    with app.app_context():
        create_db()
        models.db.init_app(app) 
        models.db.create_all()
        
    app.config["JWT_SECRET_KEY"] = "secret"  
    app.config['JWT_TOKEN_LOCATION'] = ['headers', 'cookies']
    jwt = JWTManager(app)

    app.register_blueprint(users.routes, url_prefix='/api/v1/users/')

    app.run()


if __name__ == '__main__':
    main() 