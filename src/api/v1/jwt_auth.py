from functools import wraps

from flask_jwt_extended import (JWTManager,
                                set_access_cookies,
                                verify_jwt_in_request,
                                get_jwt, 
                                create_access_token,
                                create_refresh_token
                                )


def generate_jwt_tokens(token_data:dict):
    new_access_token = create_access_token(identity=token_data) 
    print('сделали access_token', new_access_token)
    new_refresh_token = create_refresh_token(identity=token_data)
    print('сделали refresh_token', new_refresh_token)
    return new_access_token, new_refresh_token

