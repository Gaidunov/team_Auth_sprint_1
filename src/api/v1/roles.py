from http import HTTPStatus

from flask import Blueprint, request
from spectree import Response

from src.api.v1.doc_spectree import spec, Role, RoleLogin, RenRole, Cookies
from src.db.errors import catch_http_errors
from src.db.manager import db_manager
from src.api.v1.jwt_auth import custom_jwt_required

routes = Blueprint('roles', __name__)


@routes.post('add')
@catch_http_errors
@custom_jwt_required(admin_only=True)
@spec.validate(
    json=Role, cookies=Cookies, tags=["roles"]
)
def add_user_role():
    role_name = request.json['role']
    result = db_manager.roles.add_role(role_name)
    return result, HTTPStatus.CREATED


@routes.post('add-to-user')
@catch_http_errors
@custom_jwt_required(admin_only=True)
@spec.validate(
    json=RoleLogin, cookies=Cookies, tags=["roles"]
)
def add_role_to_user():
    role_name, login = request.json['role'], request.json['login']
    result = db_manager.roles.add_user_a_role(login, role_name)
    return result, HTTPStatus.CREATED


@routes.post('remove-role-from-user')
@catch_http_errors
@custom_jwt_required(admin_only=True)
@spec.validate(
    json=RoleLogin, cookies=Cookies, tags=["roles"]
)
def remove_role_from_user():
    role_name, login = request.json['role'], request.json['login']
    result = db_manager.roles.remove_role_from_user(login, role_name)
    return result, HTTPStatus.ACCEPTED


@routes.patch('change-role-name')
@catch_http_errors
@custom_jwt_required(admin_only=True)
@spec.validate(
    json=RenRole, cookies=Cookies, tags=["roles"]
)
def rename_role():
    role_name = request.json['role']
    new_name_role_name = request.json['new_name_role_name']
    result = db_manager.roles.rename_role(role_name, new_name_role_name)
    return result, HTTPStatus.ACCEPTED


@routes.get('all')
@custom_jwt_required(admin_only=True)
@spec.validate(
    cookies=Cookies, tags=["roles"]
)
def all_roles():
    roles = db_manager.roles.get_all_roles()
    return roles
