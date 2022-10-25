
from http import HTTPStatus


from flask import Blueprint, request, make_response, jsonify
from src.db.manager import db_manager   
from src.api.v1.jwt_auth import generate_jwt_tokens
from flask_jwt_extended import (JWTManager,
                                set_access_cookies,
                                set_refresh_cookies,
                                verify_jwt_in_request,
                                get_jwt, 
                                create_access_token,
                                create_refresh_token,
                                get_jwt_identity,
                                jwt_required
                                )

routes = Blueprint('users', __name__)


@routes.post('account/register')
def register():
    body = request.json
    user_login, user_pass = body['login'], body['pass'] 
    try:
        db_manager.register_user(user_login, user_pass)        
        return f'юзер {user_login} добавлен', HTTPStatus.CREATED
    except ValueError:
        return 'такой юзер уже есть', HTTPStatus.CONFLICT, 



@routes.post('account/change_password')
@jwt_required()
def change_password():
    body = request.json
    user_login, user_pass, new_passw  = body['login'], body['pass'], body['new_pass']
    try:
        db_manager.change_password(user_login, user_pass, new_passw)
        user_token_data = get_jwt()
        access_token, refresh_token = generate_jwt_tokens(user_token_data)
        response = make_response(f'сменили пароль', HTTPStatus.OK)
        set_access_cookies(response, access_token)
        set_refresh_cookies(response, refresh_token)
        return  response   

    except ValueError:
        return 'направильный пароль', HTTPStatus.FORBIDDEN, 


@routes.get('account/logout')
@jwt_required()
def logout():
    """просто портим access и refresh токены пользователя"""
    user_login = get_jwt_identity().get('user_login', 'user')
    response = make_response(f'юзер {user_login} разлогинен', HTTPStatus.OK)
    set_access_cookies(response, 'deleted access_token')
    set_refresh_cookies(response, 'deleted  refresh_token')
    return response



@routes.post('account/login')
def login():
    """берем пароль из body post запроса"""
    body = request.json
    user_login, user_pass = body['login'], body['pass']
    try:
        user = db_manager.login_user(user_login, user_pass)
        
        #TODO: добавить роль
        user_token_data = {'user_id':user.id,'user_login':user_login}
        access_token, refresh_token = generate_jwt_tokens(user_token_data)
        response = make_response(f'юзер {user_login} залогинен', HTTPStatus.OK)
        set_access_cookies(response, access_token)
        set_refresh_cookies(response, refresh_token)
        return response 

    except Exception as ex:
        return str(ex), HTTPStatus.CONFLICT, 


@routes.post("/refresh_token")
@jwt_required(refresh=True)
def refresh():
    """обновляем access_token"""
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify(access_token=access_token)



@routes.get('/<string:login>')
def get_user_by_loging(login):
    user = db_manager.get_user_by_login(login)
    return {'user_id':user.id, 'login':user.login}


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

