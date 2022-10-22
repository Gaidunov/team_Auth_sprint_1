""" Тип если бы jwt надо было генерить и проверять самому """

from datetime import datetime, timedelta
import pytz

from flask import (Flask, 
                request, 
                session,
                make_response,
                render_template,
                url_for,
                redirect) 

import jwt
from db import init_db, db
from models import User, RefreshTokens
from redis_client import redis_cli

app = Flask(__name__)

BASE_URL = 'http://127.0.0.1:5000/'

@app.route('/')
def hello_world():
    return 'Hello, World!'

def alert_and_redirect(text, url):
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
        return render_template('redirect_registred.html', context={'message':'ты уже зареган', 'redirect':url_for("login")})

def set_or_update_refresh_token(user_name):
    existing_user = User.query.filter_by(login=user_name).first() 
    if not existing_user:
        raise ValueError('ошибка, нет такого юзера')
    


@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html',title='Log in')
    user_name, user_pass = request.form['name'], request.form['pass']
    existing_user = User.query.filter_by(login=user_name).first() 
    
    if not existing_user:
        return alert_and_redirect('ошибка, нет такого юзера. зарегайся сначала', url_for('register'))

    if not existing_user.check_password(user_pass):
        return 'ошибка, неправильный пароль'

    # Залогинились
    
    # Делаем refresh и access токены                                    
    user_token_data = {"Iss":user_name, "logged": "true"}
    new_access_token = jwt.encode(user_token_data, "secret", algorithm="HS256")
    new_refresh_token = jwt.encode({"refresh":"true"}, "secret_2", algorithm="HS256")
    
    # сохраняем access_token в redis
    import json
    json_access_token = json.dumps(new_access_token)
    redis_cli.setex(user_name, 15, json_access_token)
    
    # добавляем refresh_token в БД или обновляем существующий
    token_expiration_date = datetime.now(tz=pytz.timezone('Europe/Moscow')) + timedelta(minutes=15)
    
    refresh_token_for_db = RefreshTokens.query.filter_by(user_id=existing_user.id).first()

    if not refresh_token_for_db:
        refresh_token_for_db = RefreshTokens(user_id=existing_user.id, token=new_refresh_token, token_expiration_date=token_expiration_date)
        db.session.add(refresh_token_for_db)
        db.session.commit()
    else:
        refresh_token_for_db.token_expiration_date = token_expiration_date
        refresh_token_for_db.token = new_refresh_token
        db.session.commit()

    resp = make_response(redirect(url_for('protected')))
    
    resp.set_cookie('access_token', new_access_token, httponly=True)
    resp.set_cookie('refresh_cookie', new_refresh_token, httponly=True)
    resp.set_cookie('user_name', user_name)
    
    return resp

@app.route("/public")
def public():
    return "some public data"


@app.route("/protected")
def protected():
    jwt_access_token = request.cookies.get('access_token')
    user_name = request.cookies.get('user_name')
    
    try:
        decoded = jwt.decode(jwt_access_token, "secret", algorithms=["HS256"]) # если раскордировался - значит валидный
        token_from_redis = redis_cli.get(user_name)

        if not token_from_redis:
            raise jwt.exceptions.ExpiredSignatureError('токен истек!')
        print('ACCSESS ТОКЕН ОК')
        return "this is protected info"


    except (jwt.exceptions.InvalidSignatureError, jwt.exceptions.ExpiredSignatureError):
        print('jwt_access_token НЕ ВАЛИДЕН, проверяем refresh token и отдаем')
    
        # проверка не истек ли access token 
        # пытаемся обновить access токен с помощью refresh токена        
        user = User.query.filter_by(login=user_name).first() 
        token = RefreshTokens.query.filter_by(user_id=user.id).first()
        token_expiration = token.token_expiration_date
        if datetime.now() > token_expiration:
            return f'refresh токен истек, надо <a href="{BASE_URL + url_for("login")}">логиниться</a>'
        else:
            # если не истек - выдаем новый access
            print('РЕФРЕШ ТОКЕН НЕ ИСТЕК - ВЫДАЕМ НОВЫЙ')
            user_token_data = {"Iss":user_name, "Exp":15, "logged": "true"}
            new_access_token = jwt.encode(user_token_data, "secret", algorithm="HS256")
            redis_cli.setex(user_name, 15, new_access_token)
            resp = make_response(redirect(url_for('protected')))
            resp.set_cookie('access_token', new_access_token, httponly=True)
            return resp

def main():
    init_db(app)        
    app.run()


if __name__ == '__main__':
    main() 