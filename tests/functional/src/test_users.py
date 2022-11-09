import json
from unittest.mock import ANY

import pytest
from flask import Flask

from src.db.db import db_session
from src.models import models


@pytest.fixture()
def f_login_response(
    f_client: Flask
):
    f_client.post(
        '/api/v1/users/account/register',
        json={
            'login': 'foo',
            'pass': 'bar',
        }
    )

    response = f_client.post(
        '/api/v1/users/account/login',
        json={
            'login': 'foo',
            'pass': 'bar',
        }
    )
    return response


@pytest.mark.usefixtures('f_prepare_db_for_tests')
def test_successfull_register(f_client: Flask) -> None:
    response = f_client.post(
        '/api/v1/users/account/register',
        json={
            'login': 'foo',
            'pass': 'bar',
        }
    )
    assert response.status_code == 201
    assert response.json == {'msg': 'юзер foo добавлен в БД'}

    query = db_session.query(models.User)
    user = query.filter_by(login='foo').first()

    assert user


@pytest.mark.usefixtures('f_prepare_db_for_tests')
def test_successfull_login(
    f_client: Flask,
    f_login_response,
) -> None:

    assert f_login_response.status_code == 200
    assert f_login_response.text == 'юзер foo залогинен'

    headers = [
        header[0]
        for header in f_login_response.headers._list
    ]
    assert 'Set-Cookie' in headers

    response = f_client.get(
        '/api/v1/users/foo/sessions',
    )

    assert json.loads(response.json[0]) == {
        'date': ANY,
        'action': 'login',
        'user_agent': 'werkzeug/2.2.2'
    }


@pytest.mark.usefixtures('f_prepare_db_for_tests')
def test_change_password(
    f_client: Flask,
    f_login_response,
) -> None:
    query = db_session.query(models.User)
    user = query.filter_by(login='foo').first()
    preview_pass_hash = user.password_hash

    access_token = dict(
        f_login_response.headers
    )['Set-Cookie'].split('=')[1].split(';')[0]

    response = f_client.post(
        '/api/v1/users/account/change_password',
        json={
            'login': 'foo',
            'pass': 'bar',
            'new_pass': 'baz',
        },
        headers={
            'Authorization': f'Bearer {access_token}'
        }
    )

    assert response.text == 'сменили пароль'
    query = db_session.query(models.User)
    user = query.filter_by(login='foo').first()

    assert user.password_hash != preview_pass_hash


@pytest.mark.usefixtures('f_prepare_db_for_tests')
def test_logout(
    f_client: Flask,
    f_login_response,
) -> None:
    access_token = dict(
        f_login_response.headers
    )['Set-Cookie'].split('=')[1].split(';')[0]

    response = f_client.get(
        '/api/v1/users/account/logout',
        headers={
            'Authorization': f'Bearer {access_token}'
        }
    )

    assert response.text == 'юзер foo разлогинен'
    query = db_session.query(models.SessionHistory)
    session = query.filter_by(action='logout').first()

    assert session


@pytest.mark.usefixtures('f_prepare_db_for_tests')
def test_logout_all_devices(
    f_client: Flask,
    f_login_response,
) -> None:
    access_token = dict(
        f_login_response.headers
    )['Set-Cookie'].split('=')[1].split(';')[0]

    response = f_client.get(
        '/api/v1/users/account/logout-all',
        headers={
            'Authorization': f'Bearer {access_token}'
        }
    )

    assert any([
        'deleted access_token' in header[1]
        for header in response.headers._list
    ])

    assert response.text == 'юзер foo разлогинен на всех устройствах'


@pytest.mark.usefixtures('f_prepare_db_for_tests')
def test_refresh_access_token(
    f_client: Flask,
    f_login_response,
) -> None:
    refresh_token = f_login_response.headers[3][1].split(
        '='
    )[1].split(';')[0]

    response = f_client.post(
        '/api/v1/users/account/refresh_token',
        headers={
            'Authorization': f'Bearer {refresh_token}'
        }
    )

    assert response.json == {
        'access_token': ANY,
    }


@pytest.mark.usefixtures('f_prepare_db_for_tests')
def test_get_user_by_logging(
    f_client: Flask,
    f_login_response,
) -> None:
    response = f_client.get(
        '/api/v1/users/foo',
    )

    assert response.json == {
        'login': 'foo', 'user_id': ANY
    }
