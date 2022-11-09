from http import HTTPStatus
from datetime import datetime, timedelta
from flask import Blueprint, request, make_response, jsonify, Response
from flask_jwt_extended import (
    set_access_cookies,
    set_refresh_cookies,
    get_jwt,
    create_access_token,
    get_jwt_identity,
    jwt_required
)
from spectree import Response

from src.api.v1.doc_spectree import spec, Profile, Message
from src.db.manager import db_manager
from src.db.errors import catch_http_errors
from src.api.v1.jwt_auth import generate_jwt_tokens
from src.db.redis_client import redis_cli

routes = Blueprint('users', __name__)


@routes.post('account/register')
@catch_http_errors
@spec.validate(
    json=Profile, resp=Response(HTTP_200=Message, HTTP_403=None), tags=["users"]
)
def register():
    body = request.json
    user_login, user_pass = body['login'], body['pass']
    db_manager.users.register_user(user_login, user_pass)
    return jsonify(msg=f'юзер {user_login} добавлен в БД'), HTTPStatus.CREATED


@routes.post('account/change_password')
@jwt_required()
@catch_http_errors
@spec.validate(
    json=Profile, resp=Response(HTTP_200=Message, HTTP_403=None), tags=["users"]
)
def change_password():
    body = request.json
    user_login = body['login']
    user_pass = body['pass']
    new_passw = body['new_pass']
    db_manager.users.change_password(user_login, user_pass, new_passw)
    response = make_response('сменили пароль', HTTPStatus.OK)
    return response


@routes.get('account/logout-all')
@jwt_required()
@catch_http_errors
@spec.validate(
    json=Profile, resp=Response(HTTP_200=Message, HTTP_403=None), tags=["users"]
)
def logout_all_devices():
    """
    1. добавляяем в редис протухшего юзера
    2.добалвяем в редис время тотального логаута,
    с которым потом будем сравнивать дату из токена
    в jwt_auth.custom_jwt_required
    """
    jwt_data = get_jwt_identity()
    user_login = jwt_data['user_login']
    now = datetime.now().timestamp()
    redis_cli.setex(name=user_login, value=now, time=timedelta(minutes=11))
    response = make_response(
        f'юзер {user_login} разлогинен на всех устройствах', HTTPStatus.OK)
    set_access_cookies(response, 'deleted access_token')
    set_refresh_cookies(response, 'deleted  refresh_token')
    return response


@routes.get('account/logout')
@jwt_required()
@spec.validate(
    json=Profile, resp=Response(HTTP_200=Message, HTTP_403=None), tags=["users"]
)
def logout():
    """
    1. добавляем токен в черный список
    (проверяется автоматически в @jwt_required() )
    2. записываем действие в историю
    """
    jwt_data = get_jwt_identity()
    jti = get_jwt()["jti"]
    redis_cli.set(jti, "", ex=timedelta(minutes=11))
    user_login, user_agent = jwt_data['user_login'], jwt_data['user_agent']
    response = make_response(f'юзер {user_login} разлогинен', HTTPStatus.OK)
    db_manager.users.logout_user(login=user_login, user_agent=user_agent)
    return response


@routes.post('account/login')
@catch_http_errors
@spec.validate(
    json=Profile, resp=Response(HTTP_200=Message, HTTP_403=None), tags=["users"]
)
def login():
    """берем пароль из body post запроса"""
    body = request.json
    user_login, user_pass = body['login'], body['pass']
    user_agent = request.headers.get('User-Agent')
    user = db_manager.users.login_user(user_login, user_pass, user_agent)
    user_roles = db_manager.roles.get_user_roles_by_login(user_login)

    user_token_data = {
        'user_id': user.id,
        'user_login': user_login,
        'user_roles': user_roles,
        'user_agent': user_agent
    }
    access_token, refresh_token = generate_jwt_tokens(user_token_data)
    response = make_response(f'юзер {user_login} залогинен')
    set_access_cookies(response, access_token)
    set_refresh_cookies(response, refresh_token)
    return response, HTTPStatus.OK


@routes.post("account/refresh_token")
@jwt_required(refresh=True)
@spec.validate(
    json=Profile, resp=Response(HTTP_200=Message, HTTP_403=None), tags=["users"]
)
def refresh() -> Response:
    """обновляем access_token"""
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify(access_token=access_token)


@routes.get('/<string:login>/roles')
@catch_http_errors
@spec.validate(
    json=Profile, resp=Response(HTTP_200=Message, HTTP_403=None), tags=["users"]
)
def get_user_roles(login: str) -> dict:
    roles = db_manager.roles.get_user_roles_by_login(
        login
    )
    return roles


@routes.get('/<string:login>/sessions')
@catch_http_errors
@spec.validate(
    json=Profile, resp=Response(HTTP_200=Message, HTTP_403=None), tags=["users"]
)
def get_user_session(login: str) -> dict:
    sessions = db_manager.users.get_user_sessions(
        login
    )
    return sessions


@routes.get('/<string:login>')
@catch_http_errors
@spec.validate(
    json=Profile, resp=Response(HTTP_200=Message, HTTP_403=None), tags=["users"]
)
def get_user_by_loging(login: str) -> dict:
    user = db_manager.users.get_user_by_login(login)
    return {
        'user_id': user.id,
        'login': user.login,
    }
