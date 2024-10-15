import pytest
import os
import sys
import json
from werkzeug.security import generate_password_hash

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app_package import create_app, db
from app_package.models.models import User


@pytest.fixture(scope='session')
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
    app.config['WTF_CSRF_ENABLED'] = False

    with app.app_context():
        yield app


@pytest.fixture(scope='function')
def client(app):
    return app.test_client()


@pytest.fixture(scope='function')
def init_database(app):
    with app.app_context():
        user = User(username='testuser', email='test@example2.com', password=generate_password_hash('password'))
        db.session.add(user)
        db.session.commit()

        yield

        db.session.query(User).filter_by(username='testuser').delete()
        db.session.commit()


def test_login_success(client, init_database):
    response = client.post('/login', json={
        'username': 'testuser',
        'password': 'password'
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'access_token' in data
    assert 'refresh_token' in data


def test_login_failure(client, init_database):
    response = client.post('/login', json={
        'username': 'testuser',
        'password': 'wrongpassword'
    })
    assert response.status_code == 401


def test_protected_route(client, init_database):
    # First, login to get the token
    login_response = client.post('/login', json={
        'username': 'testuser',
        'password': 'password'
    })
    access_token = json.loads(login_response.data)['access_token']

    # Then, access the protected route
    response = client.get('/protected', headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['logged_in_as'] == 'testuser'


def test_refresh_token(client, init_database):
    # First, login to get the tokens
    login_response = client.post('/login', json={
        'username': 'testuser',
        'password': 'password'
    })
    refresh_token = json.loads(login_response.data)['refresh_token']

    # Then, use the refresh token to get a new access token
    response = client.post('/refresh', headers={'Authorization': f'Bearer {refresh_token}'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'access_token' in data


def test_logout(client, init_database):
    # First, login to get the token
    login_response = client.post('/login', json={
        'username': 'testuser',
        'password': 'password'
    })
    access_token = json.loads(login_response.data)['access_token']

    # Then, logout
    response = client.post('/logout', headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == 200

    # Try to access protected route after logout
    response = client.get('/protected', headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == 401


if __name__ == "__main__":
    pytest.main([__file__])
