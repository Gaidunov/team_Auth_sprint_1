
from flask import Blueprint
from src.api.v1.jwt_auth import custom_jwt_required
from src.db.errors import catch_http_errors


routes = Blueprint('movies', __name__)


@routes.get('/public')
def public_data():
    return 'public data'


@routes.get('/protected')
@catch_http_errors
@custom_jwt_required()
def data_for_logged_users():
    return 'protected data'
