from datetime import datetime, timedelta
import time
import pytz
import json
from functools import wraps


from flask import (Flask, 
                request, 
                session,
                make_response,
                render_template,
                url_for,
                redirect) 

from flask_jwt_extended import (JWTManager,
                                set_access_cookies,
                                verify_jwt_in_request,
                                get_jwt, 
                                create_access_token
                                )


from db import init_db, db, db_manager
from models import User
from redis_client import redis_cli


app = Flask(__name__)
jwt = JWTManager(app)

ACCESS_TOKEN_LIFE = 15 # sec
REFRESH_TOKEN_LIFE = 45 # sec

START_TIME = ''

@app.route('/')
def hello_world():
    return 'Hello, World!'

def alert_and_redirect(text, url):
    '''оповещение с переадресацией (когда токен просрочился)'''
    return render_template('redirect.html', context={'message':text, 'redirect':url})


@app.route("/register", methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        return render_template('login.html', title='Register')

    user_name, user_pass = request.form['name'], request.form['pass']
    existing_user = User.query.filter_by(login=user_name).first() 
    if not existing_user:
        new_user = User(login=user_name, password=user_pass)
        new_user.set_password(user_pass)
        db.session.add(new_user)
        db.session.commit()
        return alert_and_redirect(text='Удачно зарегались, теперь залогинься', url=url_for('login'))
    else:
        return render_template('redirect.html', context={'message':'ты уже зареган', 'redirect':url_for("login")})


@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html',title='Log in')

    user_name, user_pass = request.form['name'], request.form['pass']
    existing_user = User.query.filter_by(login=user_name).first() 
    
    if not existing_user:
        return alert_and_redirect('ошибка, нет такого юзера. зарегайся сначала', url_for('register'))

    if not existing_user.check_password(user_pass):
        return alert_and_redirect('ошибка, неправильный пароль', url_for('login'))

    # в токен можно засовывать инфу любую о пользователе, в том числе наверно его роль
    user_token_data = {"user_name":user_name, "user_id":existing_user.id, "logged": "true"} 

    new_access_token = create_access_token(identity=user_token_data) 
    print('сделали access_token', new_access_token)

    new_refresh_token = create_access_token(identity={"refresh":"true"})
    print('сделали refresh_token', new_refresh_token)

    # сохраняем access_token в redis
    json_access_token = json.dumps(new_access_token)
    redis_cli.setex(user_name, ACCESS_TOKEN_LIFE, json_access_token)
    
    # добавляем refresh_token в БД или обновляем время существующего
    token_expiration_date = datetime.now(tz=pytz.timezone('Europe/Moscow')) + timedelta(seconds=REFRESH_TOKEN_LIFE)
    db_manager.update_refresh_token(user_id=existing_user.id, new_refresh_token=new_refresh_token, expiration_datetime=token_expiration_date)

    resp = make_response(redirect(url_for('protected')))
    # добавляем access_token в cookies
    set_access_cookies(resp, new_access_token)
    global START_TIME
    START_TIME = time.time()
    return resp

@app.route("/public")
def public():
    return "some public data"


def require_jwt(*args, **kwargs):
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
            verify_jwt_in_request()
            # берем данные из токена
            jwt_data = get_jwt()
            user_token_data = jwt_data['sub']
            user_id = user_token_data['user_id']

            # проверяем не истек ли access_token    
            access_token = redis_cli.get(user_id)
            if access_token:
                print('access_token ВАЛИДЕН ВСЕ ОК')
                return view_function()

            # проверка на refresh токена на свежесть
            token_is_fresh = db_manager.check_if_refresh_token_is_fresh(user_id)
            if not token_is_fresh:
                return alert_and_redirect(text='Все токены просрочены, надо залогиниться', url=url_for('login'))
                
            print('access_token просрочен, делаем новый с помощью refresh')
            new_access_token = create_access_token(identity=user_token_data)
            print('новый access_token -- ', new_access_token )
            
            # кладем его в редис 
            redis_cli.setex(user_id, ACCESS_TOKEN_LIFE, new_access_token)
            # добавляем пользователю в кукис
            resp = view_function()
            set_access_cookies(resp, new_access_token)
            return resp 
             
        return decorator
    return wrapper


@app.route("/protected")
@require_jwt()
def protected():
    return make_response(f'ты залогинен. \n\n тебя разлогинет через {int(START_TIME + REFRESH_TOKEN_LIFE - time.time())} секунд')



def main():
    init_db(app)
    app.config["JWT_SECRET_KEY"] = "secret"  
    app.config['JWT_TOKEN_LOCATION'] = ['headers', 'cookies']
    app.run()


if __name__ == '__main__':
    main() 