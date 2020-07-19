import pytest
from mongoengine import connect, disconnect
from mongoengine.connection import _get_db
from tests.utils import register_user, login_user, parse_login, oauth2_login
import json

VALID_USER = {
    'email': 'correct@email.com',
    'username': 'testUser',
    'password': 'testPw',
    'oauthToken': 'token_correct@email.com'
}
NEXT_ID = 5

class TestAuthController:
    def test_register_success(self, client):
        """ POST /register
        Should: return 200 with user id """

        res = register_user(client, VALID_USER['email'], VALID_USER['username'], VALID_USER['password'])
        res_json = res.get_json()
        assert res.status_code == 200
        assert res_json['id'] == NEXT_ID

    def test_register_repeated_email(self, client):
        """ POST /register
        Should: return 409 """

        res = register_user(client, VALID_USER['email'], VALID_USER['username'], VALID_USER['password'])
        assert res.status_code == 200
        res = register_user(client, VALID_USER['email'], 'someRandomUser', VALID_USER['password'])
        res_json = res.get_json()
        assert res.status_code == 409
        assert res_json['reason'] == 'User already registered'

    def test_register_repeated_username(self, client):
        """ POST /register
        Should: return 409 """

        res = register_user(client, VALID_USER['email'], VALID_USER['username'], VALID_USER['password'])
        assert res.status_code == 200
        res = register_user(client, 'someOther@email.com', VALID_USER['username'], VALID_USER['password'])
        res_json = res.get_json()
        assert res.status_code == 409
        assert res_json['reason'] == 'User already registered'

    def test_register_with_invalid_email(self, client):
        """ POST /register
        Should: return 400 """

        res = register_user(client, 'gibberish', VALID_USER['username'], VALID_USER['password'])
        res_json = res.get_json()
        assert res.status_code == 400
        assert res_json['reason'] == 'Invalid email address'

    def test_register_with_missing_fields(self, client):
        """ POST /register
        Should: return 400 """

        res = register_user(client, email=VALID_USER['email'], username=VALID_USER['username'])
        res_json = res.get_json()
        assert res.status_code == 400
        assert res_json['reason'] == 'Fields are incomplete'

        res = register_user(client, email=VALID_USER['email'], password=VALID_USER['password'])
        res_json = res.get_json()
        assert res.status_code == 400
        assert res_json['reason'] == 'Fields are incomplete'

        res = register_user(client, username=VALID_USER['username'], password=VALID_USER['password'])
        res_json = res.get_json()
        assert res.status_code == 400
        assert res_json['reason'] == 'Fields are incomplete'

    def test_login_success(self, client):
        """ POST /login
        Should: return 200 """

        res = register_user(client, VALID_USER['email'], VALID_USER['username'], VALID_USER['password'])
        res = login_user(client, VALID_USER['email'], VALID_USER['password'])
        res_json = res.get_json()
        assert res.status_code == 200
        assert res_json['token'] == 'token_{}'.format(VALID_USER['email'])
        assert res_json['user']['id'] == NEXT_ID
        assert res_json['user']['email'] == VALID_USER['email']
        assert res_json['user']['username'] == VALID_USER['username']

    def test_login_invalid_user(self, client):
        """ POST /login
        Should: return 401 """

        res = login_user(client, 'invalidEmail', VALID_USER['password'])
        res_json = res.get_json()
        assert res.status_code == 401
        assert res_json['reason'] == 'Wrong credentials'

    def test_login_wrong_password(self, client):
        """ POST /login
        Should: return 401 """

        res = register_user(client, VALID_USER['email'], VALID_USER['username'], VALID_USER['password'])
        res = login_user(client, VALID_USER['email'], 'superHackyPassword')
        res_json = res.get_json()
        assert res.status_code == 401
        assert res_json['reason'] == 'Wrong credentials'

    def test_login_with_missing_fields(self, client):
        """ POST /login
        Should: return 400 """

        res = login_user(client, email=VALID_USER['email'])
        res_json = res.get_json()
        assert res.status_code == 400
        assert res_json['reason'] == 'Email or password is missing'

        res = login_user(client, password=VALID_USER['password'])
        res_json = res.get_json()
        assert res.status_code == 400
        assert res_json['reason'] == 'Email or password is missing'

    def test_register_oauth(self, client):
        """ POST /oauth2login
        Should: return 200 with user id """

        res = oauth2_login(client, VALID_USER['oauthToken'])
        res_json = res.get_json()
        assert res.status_code == 200
        assert res_json['user']['id'] == NEXT_ID

    def test_register_and_login_oauth(self, client):
        """ POST /oauth2login
        Should: return 200 with the same id for register and login """

        #Register step
        res = oauth2_login(client, VALID_USER['oauthToken'])
        res_json = res.get_json()
        assert res.status_code == 200
        assert res_json['user']['id'] == NEXT_ID

        #Login step
        res = oauth2_login(client, VALID_USER['oauthToken'])
        res_json = res.get_json()
        assert res.status_code == 200
        assert res_json['user']['id'] == NEXT_ID

    def test_register_oauth(self, client):
        """ POST /oauth2login
        Should: return 400 """

        res = oauth2_login(client, "invalidToken")
        res_json = res.get_json()
        assert res.status_code == 400
