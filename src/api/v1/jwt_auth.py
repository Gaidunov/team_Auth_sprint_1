from functools import wraps

from flask_jwt_extended import (JWTManager,
                                set_access_cookies,
                                verify_jwt_in_request,
                                get_jwt, 
                                create_access_token
                                )

def require_jwt(*args, **kwargs):
    #TODO: переделвыаю (кирилл)
    '''
    как декоратор можно вешать на все защищенные вьюхи
    1. проверяет jwt 
    2. обновляет его, если надо и если позволяет refresh токен 
    3. выкидывает на логин форму, если истек refresh токен
    '''
    def wrapper(view_function):
        @wraps(view_function)
        def decorator(*args, **kwargs):
            # верефицируем jwt  
            # verify_jwt_in_request()
            # # берем данные из токена
            # jwt_data = get_jwt()
            # user_token_data = jwt_data['sub']
            # user_id = user_token_data['user_id']

            # проверяем не истек ли access_token    
            # access_token = redis_cli.get(user_id)
            # if access_token:
            #     print('access_token ВАЛИДЕН ВСЕ ОК')
            #     return view_function()

            # проверка на refresh токена на свежесть
            # token_is_fresh = db_manager.check_if_refresh_token_is_fresh(user_id)
            # if not token_is_fresh:
            #     return alert_and_redirect(text='Все токены просрочены, надо залогиниться', url=url_for('login'))
                
            # print('access_token просрочен, делаем новый с помощью refresh')
            # new_access_token = create_access_token(identity=user_token_data)
            # print('новый access_token -- ', new_access_token )
            
            # # кладем его в редис 
            # redis_cli.setex(user_id, ACCESS_TOKEN_LIFE, new_access_token)
            # добавляем пользователю в кукис
            resp = view_function()
            # set_access_cookies(resp, new_access_token)
            return resp 
             
        return decorator
    return wrapper
