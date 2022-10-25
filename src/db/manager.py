from datetime import datetime
from src.models.models import User, RefreshTokens
from src.db.db import db_session
from sqlalchemy.orm import Session


class DataBaseManager:
    """КЛАСС ДЛЯ ХОЖДЕНИЯ В БАЗУ"""

    def __init__(self, session: Session) -> None:
        self.session = session

    def update_refresh_token(self, user_id:str, new_refresh_token:str, expiration_datetime:datetime):
        """
        если у юзера нет refresh_token - добавляем
        если есть - обвновляем
        """
        refresh_token_for_db = RefreshTokens.query.filter_by(user_id=user_id).first()
        if not refresh_token_for_db:
            refresh_token_for_db = RefreshTokens(user_id=user_id, token=new_refresh_token, token_expiration_date=expiration_datetime)
            self.session.add(refresh_token_for_db)
            self.db.session.commit()
        else:
            refresh_token_for_db.token_expiration_date = expiration_datetime
            refresh_token_for_db.token = new_refresh_token
            self.session.commit()

    def get_user_by_login(self, login:str)->User:
        existing_user = self.session.query(User).filter_by(id=login).first() 
        if not existing_user:
            raise ValueError('нет такого юзера')
        return existing_user

    def get_user_by_id(self, user_id:str)->User:
        existing_user = self.session.query(User).filter_by(id=user_id).first() 
        if not existing_user:
            raise ValueError('нет такого юзера')
        return existing_user

    def add_user(self, login:str, password:str) -> User:
        query = self.session.query(User)
        user = query.filter_by(login=login).first()
        if user:
            #TODO: сделать кастомную ошибку
            raise ValueError('такой юзер уже есть')

        if not user:
            user = User(login=login)
            user.set_password(password)
            self.session.add(user)
            self.session.commit()
        return user

    def check_if_refresh_token_is_fresh(self, user_id:str):
        user = self.get_user_by_id(user_id)
        token = RefreshTokens.query.filter_by(user_id=user.id).first()
        if datetime.now() < token.token_expiration_date:
            return True
        return False

        
db_manager = DataBaseManager(db_session)