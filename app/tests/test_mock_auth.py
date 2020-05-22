import pytest
import sys
sys.path.append("..")
from app.shared_servers.AuthServer import MockAuthServer
from flask import jsonify

class TestMockAuthServer:
    def setup_method(self, method):
        """ setup any state tied to the execution of the given method in a
        class.  setup_method is invoked for every test method of a class.
        """
        self.mock_auth_server = MockAuthServer()

    def test_register_success(self, client):
        """ POST /users/register
        Should: return 200 and with user id """

        data = jsonify({'email': 'email@gmail.com', 'username': 'theboss', 'password': '123'})
        res = self.mock_auth_server.register(data)
        json = res.get_json()
        assert json['id'] == 1
        assert res.status_code == 200

    '''
    def test_register_failure_invalid_email(self, client):
        """ POST /users/register with invalid email
        Should: return 400 and correct message """

        res = register(client, 'oli_wrong', 'invalid_email','123')
        assert b'Invalid email address' in res.data
        assert res.status_code == 400

    def test_register_failure_username_taken(self, client, context_register):
        """ POST /users/register with username taken
        Should: return 400 and correct message """

        res = register(client, 'oli', 'different@email.com','123') # same username as context
        assert b'User already registered' in res.data
        assert res.status_code == 409
    
    def test_login_success(self, client, context_register):
        """ POST /users/login
        Should: return 200 and with token """

        res = login(client, 'olifer97@gmail.com','123')
        json = res.get_json()
        assert 'token' in json
        assert json['user']['username'] == 'oli'
        assert json['user']['email'] == 'olifer97@gmail.com'
        assert res.status_code == 200

    def test_login_failure_password(self, client, context_register):
        """ POST /users/login wrong password
        Should: return 401 and correct message """

        res = login(client, 'olifer97@gmail.com','wrong')
        assert b'Password incorrect' in res.data
        assert res.status_code == 401

    def test_login_failure_inexistent(self, client): # without context_register
        """ POST /users/login user does not exist
        Should: return 401 and correct message """

        res = login(client, 'olifer97@gmail.com','123')
        assert b'Could not find user' in res.data
        assert res.status_code == 401

    def test_authorize_success(self, client, context_login):
        """ POST /users/authorize
        Should: return 200 """

        res = authorize(client, context_login)
        user_info = res.get_json()
        assert res.status_code == 200
        assert user_info['user']['username'] == 'oli'
        assert user_info['user']['email'] == 'olifer97@gmail.com'

    def test_authorize_failure_invalid(self, client):
        """ POST /users/authorize invalid token
        Should: return 401 """

        res = authorize(client, 'invalidtoken')
        assert b'Invalid Token' in res.data
        assert res.status_code == 401

    def test_authorize_failure_logged_out(self, client, context_logout):
        """ POST /users/authorize token logged out
        Should: return 401 """

        res = authorize(client, context_logout)
        assert b'Invalid Token' in res.data
        assert res.status_code == 401

    def test_authorize_failure_not_found(self, client):
        """ POST /users/authorize token not found
        Should: return 401 """

        res = authorize(client)
        assert b'Token not found' in res.data
        assert res.status_code == 401

    def test_logout_success(self, client, context_login):
        """ POST /users/logout
        Should: return 205 """

        res = logout(client, context_login)
        assert res.status_code == 205

    def test_logout_failure(self, client):
        """ POST /users/logout No token
        Should: return 401 """

        res = logout(client)
        assert res.status_code == 401

    def test_get_user_by_id_success(self, client, context_register):
        """ GET /users/id
        Should: return 200 with user data """

        res = get_user(client, context_register)
        user_info = res.get_json() 
        assert res.status_code == 200
        assert user_info['username'] == 'oli'
        assert user_info['email'] == 'olifer97@gmail.com'

    def test_get_user_by_id_failure(self, client): # no context_register
        """ GET /users/id
        Should: return 401 with correct message """

        res = get_user(client, 1)
        user_info = res.get_json() 
        assert b'Could not find user' in res.data
        assert res.status_code == 401

    def test_get_users_success(self, client, context_register):
        """ GET /users/id
        Should: return 200 with user data """

        res = client.get('/users')
        users = res.get_json() 
        assert res.status_code == 200
        assert len(users) == 1
        '''