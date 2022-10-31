
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

routes = Blueprint('users_roles', __name__)



@routes.get('/<string:login>')
def add_user_a_role(login):

    user = db_manager.users.get_user_roles(login)
    return {'user_id':user.id, 'login':user.login}




