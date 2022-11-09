import pytest
from flask import Flask
from src.db.manager import db_manager
from src.db.db import db_session
from src.models import models


@pytest.fixture()
def f_superuser_login_response(
    f_client: Flask
):
    db_manager.utils.create_super_user('foo', 'bar')

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


@pytest.fixture()
def f_create_test_role(
    f_client: Flask,
    f_superuser_login_response,
) -> None:
    access_token = dict(
        f_superuser_login_response.headers
    )['Set-Cookie'].split('=')[1].split(';')[0]

    f_client.post(
        '/api/v1/roles/add',
        json={
            'role': 'test_role',
        },
        headers={
            'Authorization': f'Bearer {access_token}'
        }
    )


@pytest.mark.usefixtures('f_prepare_db_for_tests')
def test_add_role(
    f_client: Flask,
    f_superuser_login_response,
) -> None:
    access_token = dict(
        f_superuser_login_response.headers
    )['Set-Cookie'].split('=')[1].split(';')[0]

    response = f_client.post(
        '/api/v1/roles/add',
        json={
            'role': 'test_role',
        },
        headers={
            'Authorization': f'Bearer {access_token}'
        }
    )
    assert response.status_code == 201

    query = db_session.query(models.Role)
    role = query.filter_by(name='test_role').first()

    assert role


@pytest.mark.usefixtures('f_create_test_role')
@pytest.mark.usefixtures('f_prepare_db_for_tests')
def test_add_role_to_user(
    f_client: Flask,
    f_superuser_login_response,
) -> None:
    access_token = dict(
        f_superuser_login_response.headers
    )['Set-Cookie'].split('=')[1].split(';')[0]

    response = f_client.post(
        '/api/v1/roles/add-to-user',
        json={
            'role': 'test_role',
            'login': 'foo'
        },
        headers={
            'Authorization': f'Bearer {access_token}'
        }
    )
    assert response.status_code == 201

    query = db_session.query(models.Role)
    role = query.filter_by(name='test_role').first()

    assert role.users[0].login == 'foo'


@pytest.mark.usefixtures('f_create_test_role')
@pytest.mark.usefixtures('f_prepare_db_for_tests')
def test_remove_role_from_user(
    f_client: Flask,
    f_superuser_login_response,
) -> None:
    access_token = dict(
        f_superuser_login_response.headers
    )['Set-Cookie'].split('=')[1].split(';')[0]

    response = f_client.post(
        '/api/v1/roles/add-to-user',
        json={
            'role': 'test_role',
            'login': 'foo'
        },
        headers={
            'Authorization': f'Bearer {access_token}'
        }
    )
    assert response.status_code == 201

    query = db_session.query(models.Role)
    role = query.filter_by(name='test_role').first()

    assert role.users[0].login == 'foo'

    response = f_client.post(
        '/api/v1/roles/remove-role-from-user',
        json={
            'role': 'test_role',
            'login': 'foo'
        },
        headers={
            'Authorization': f'Bearer {access_token}'
        }
    )
    assert response.status_code == 202

    query = db_session.query(models.Role)
    role = query.filter_by(name='test_role').first()

    assert not role.users


@pytest.mark.usefixtures('f_create_test_role')
@pytest.mark.usefixtures('f_prepare_db_for_tests')
def test_rename_role(
    f_client: Flask,
    f_superuser_login_response,
) -> None:
    access_token = dict(
        f_superuser_login_response.headers
    )['Set-Cookie'].split('=')[1].split(';')[0]

    response = f_client.patch(
        '/api/v1/roles/change-role-name',
        json={
            'role': 'test_role',
            'new_name_role_name': 'new_test_role'
        },
        headers={
            'Authorization': f'Bearer {access_token}'
        }
    )
    assert response.status_code == 202

    query = db_session.query(models.Role)
    role = query.filter_by(name='new_test_role').first()

    assert role


@pytest.mark.usefixtures('f_create_test_role')
@pytest.mark.usefixtures('f_prepare_db_for_tests')
def test_list_roles(
    f_client: Flask,
    f_superuser_login_response,
) -> None:
    access_token = dict(
        f_superuser_login_response.headers
    )['Set-Cookie'].split('=')[1].split(';')[0]

    response = f_client.get(
        '/api/v1/roles/all',
        headers={
            'Authorization': f'Bearer {access_token}'
        }
    )
    assert response.status_code == 200

    assert sorted(response.json) == [
        'superuser', 'test_role', 'user'
    ]


@pytest.mark.usefixtures('f_create_test_role')
@pytest.mark.usefixtures('f_prepare_db_for_tests')
def test_get_user_roles(
    f_client: Flask,
    f_superuser_login_response,
) -> None:
    access_token = dict(
        f_superuser_login_response.headers
    )['Set-Cookie'].split('=')[1].split(';')[0]

    response = f_client.post(
        '/api/v1/roles/add-to-user',
        json={
            'role': 'test_role',
            'login': 'foo'
        },
        headers={
            'Authorization': f'Bearer {access_token}'
        }
    )
    assert response.status_code == 201

    response = f_client.get(
        '/api/v1/users/foo/roles',
        headers={
            'Authorization': f'Bearer {access_token}'
        }
    )
    assert response.status_code == 200

    assert response.json == ['superuser', 'test_role']
