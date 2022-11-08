from flask import Blueprint
from spectree import Response

from src.api.v1.doc_spectree import spec, Profile, Message
from src.db.manager import db_manager

routes = Blueprint('users_roles', __name__)


@routes.get('/<string:login>')
@spec.validate(
    json=Profile, resp=Response(HTTP_200=Message, HTTP_403=None), tags=["user-roles"]
)
def add_user_a_role(login):
    user = db_manager.users.get_user_roles(login)
    return {
        'user_id': user.id,
        'login': user.login,
    }
