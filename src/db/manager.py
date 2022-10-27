from datetime import datetime
from sqlalchemy.orm import Session

from src.models.models import User, RefreshTokens, Role
from src.models.schemas import RoleSchema
from src.db.db import db_session

#TODO: сделать кастомную ошибку


class UserManager():
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_user_by_login(self, login:str)->User:
        existing_user = self.session.query(User).filter_by(login=login).first() 
        if not existing_user:
            raise ValueError('нет такого юзера')
        return existing_user

    def get_user_by_id(self, user_id:str)->User:
        existing_user = self.session.query(User).filter_by(id=user_id).first() 
        if not existing_user:
            raise ValueError('нет такого юзера')
        return existing_user

    def change_password(self, login:str, password:str, new_password:str):
        user = self.get_user_by_login(login)
        if user.check_password(password):
            user.set_password(new_password)
            self.session.add(user)
            self.session.commit()
        else:
            raise ValueError('направильный пароль')

    def register_user(self, login:str, password:str) -> User:
        query = self.session.query(User)
        user = query.filter_by(login=login).first()
        if user:
            raise ValueError('такой юзер уже есть')
        if not user:
            user = User(login=login)
            user.set_password(password)
            self.session.add(user)
            self.session.commit()
        return user

    def login_user(self, login:str, password:str) -> User|None:
        query = self.session.query(User)
        user = query.filter_by(login=login).first()
        
        if not user:
            raise ValueError('такого юзера нет')
        if user.check_password(password):
            return user
        raise ValueError('неправильный пароль')


class TokenManager(UserManager):
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

    def check_if_refresh_token_is_fresh(self, user_id:str):
        user = self.get_user_by_id(user_id)
        token = RefreshTokens.query.filter_by(user_id=user.id).first()
        if datetime.now() < token.token_expiration_date:
            return True
        return False

            
class RoleManager(UserManager):
    def __init__(self, session: Session) -> None:
        self.session = session

    def add_role(self, role_name):
        role = Role(name=role_name)
        self.session.add(role)
        self.session.commit()
        return f'{role_name} добавлена'

    def get_user_roles(self, user_id:str)->list[str]|None:
        user = self.get_user_by_id(user_id)
        return user.roles
    
    def get_role_by_name(self, role_name:str)->Role|None:  
        role = self.session.query(Role).filter_by(name=role_name).first()
        if not role:
            raise ValueError(f'роли {role} нет в базе!')
        return role

    def add_user_role(self, user_id:str, role_name:str):
        user = self.get_user_by_id(user_id)
        role = self.get_role_by_name(role_name)
        role_schema = RoleSchema(many=True)
        user_rolser_parsed = [role['name'] for role in role_schema.dump(user.roles)]
        if role in user_rolser_parsed:
            raise ValueError('такая роль у юзера уже есть')
        user.roles.append(role)
        self.session.add(user)
        self.session.commit()
        return f'добавили {role} юзеру {user_id}'



class DataBaseManager():
    def __init__(self, session: Session) -> None:
        self.session = session
        self.users = UserManager(session)
        self.roles = RoleManager(session)
        self.tokens = TokenManager(session) 


db_manager = DataBaseManager(db_session)