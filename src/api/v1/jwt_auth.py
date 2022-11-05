from datetime import datetime
from functools import wraps
from typing import Optional

from flask_jwt_extended import (
    verify_jwt_in_request,
    get_jwt_identity,
    create_access_token,
    create_refresh_token
)

from src.db import errors
from src.db.redis_client import redis_cli


def generate_jwt_tokens(token_data: dict):
    now = datetime.now().timestamp()
    token_data.update(
        {'created': now}
    )
    new_access_token = create_access_token(identity=token_data)
    new_refresh_token = create_refresh_token(identity=token_data)
    return new_access_token, new_refresh_token


def custom_jwt_required(
    admin_only: Optional[bool] = None
):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            jwt_data = get_jwt_identity()

            if admin_only:
                # в ручки управления ролями
                # пускаются только суперюзеры
                user_roles = jwt_data['user_roles']
                if 'superuser' not in user_roles:
                    raise errors.Forbidden(reason='вход только для админов')

            user_login = jwt_data['user_login']
            token_created = jwt_data['created']
            # если в базе есть инфа о "выходе со всех аккаунтов",
            # заставляем залогиниться, если текущий токены был
            # создан до этого момента
            last_total_logout = redis_cli.get(user_login)
            if not last_total_logout:
                return fn()
            last_total_logout = float(last_total_logout.decode('utf-8'))
            if last_total_logout and last_total_logout < token_created:
                return fn()

            raise errors.Forbidden(reason='Залогинься')

        return decorator

    return wrapper
