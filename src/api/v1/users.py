
from http import HTTPStatus

from flask import Blueprint, request
from src.db.manager import db_manager
from src.api.v1.jwt_auth import require_jwt


routes = Blueprint('users', __name__)


@routes.get('/<string:uid>')
def get_all(uid):
    user = db_manager.get_user_by_id(uid)
    return user.id


@routes.post('/<string:uid>')
def add_a_user(uid):
    """берем пароль из body post запроса"""
    body = request.json
    user_login, user_pass = body['login'], body['pass']
    try:
        db_manager.add_user(user_login, user_pass)
        return f'юзер {user_login} добавлен', HTTPStatus.CREATED
    except ValueError:
        return 'такой юзер уже есть', HTTPStatus.CONFLICT, 

