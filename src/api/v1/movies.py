
from http import HTTPStatus

from flask import Blueprint, request, make_response
from src.db.manager import db_manager
from flask_jwt_extended import jwt_required, get_jwt

routes = Blueprint('movies', __name__)


@routes.get('/public')
def public_data():
    return 'public data'


@routes.get('/protected')
@jwt_required()
def data_for_logged_users():
    """отдаст только если в куках access token"""
    return 'protected data'