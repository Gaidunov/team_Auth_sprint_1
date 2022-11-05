from flask import Blueprint

from src.db.manager import db_manager

routes = Blueprint('users_roles', __name__)


@routes.get('/<string:login>')
def add_user_a_role(login):
    user = db_manager.users.get_user_roles(login)
    return {
        'user_id': user.id,
        'login': user.login,
    }
