from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

from models import User, RefreshTokens


def init_db(app):
    with app.app_context():
        import models
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///MY_DB.db'
        db.init_app(app) 
        db.create_all()

class DataBase:

    def update_refresh_token(self, user_id:str, new_refresh_token:str, expiration_datetime:datetime):
        """
        если у юзера нет refresh_token - добавляем
        если есть - обвновляем
        """
        refresh_token_for_db = RefreshTokens.query.filter_by(user_id=user_id).first()
        if not refresh_token_for_db:
            refresh_token_for_db = RefreshTokens(user_id=user_id, token=new_refresh_token, token_expiration_date=expiration_datetime)
            db.session.add(refresh_token_for_db)
            db.session.commit()
        else:
            refresh_token_for_db.token_expiration_date = expiration_datetime
            refresh_token_for_db.token = new_refresh_token
            db.session.commit()

    @staticmethod
    def get_user_by_name(user_name:str)->User:
        existing_user = User.query.filter_by(login=user_name).first() 
        if not existing_user:
            raise ValueError('нет такого юзера')
        return existing_user

    @staticmethod
    def get_user_by_id(user_id:str)->User:
        existing_user = User.query.filter_by(id=user_id).first() 
        if not existing_user:
            raise ValueError('нет такого юзера')
        return existing_user

    def check_if_refresh_token_is_fresh(self, user_id:str):
        user = self.get_user_by_id(user_id)
        token = RefreshTokens.query.filter_by(user_id=user.id).first()
        if datetime.now() < token.token_expiration_date:
            return True
        return False

        
db_manager = DataBase()