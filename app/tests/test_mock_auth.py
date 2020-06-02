import pytest
from json import loads
from shared_servers.AuthServer import MockAuthServer

class TestMockAuthServer:
    def setup_method(self, method):
        """ setup any state tied to the execution of the given method in a
        class.  setup_method is invoked for every test method of a class.
        """
        self.mock_auth_server = MockAuthServer()

    def test_register_success(self):
        """ Register an user should return 200 """

        registration_data = {'email': 'email@gmail.com', 'username': 'theboss', 'password': '123'}
        response = self.mock_auth_server.register(registration_data)
        json = loads(response.get_data())
        assert json['id'] == 5
        assert response.status_code == 200

    def test_register_failure_invalid_email(self):
        """ Register an user should return 400 """

        registration_data = {'email': 'wrong_email', 'username': 'theboss', 'password': '123'}
        response = self.mock_auth_server.register(registration_data)
        assert b'Invalid email address' in response.get_data()
        assert response.status_code == 400

    def test_register_failure_username_taken(self):
        """ Register an user with username taken should return 400 """

        registration_data = {'email': 'email@gmail.com', 'username': 'theboss', 'password': '123'}
        self.mock_auth_server.register(registration_data)
        other_registration_data = {'email': 'other_email@gmail.com', 'username': 'theboss', 'password': '123'}
        response = self.mock_auth_server.register(other_registration_data)
        assert b'User already registered' in response.get_data()
        assert response.status_code == 409
    
    def test_login_success(self):
        """ User login should return 200 and a token """

        registration_data = {'email': 'email@gmail.com', 'username': 'theboss', 'password': '123'}
        self.mock_auth_server.register(registration_data)
        login_data = {'email': 'email@gmail.com', 'password': '123'}
        response = self.mock_auth_server.login(login_data)
        json = loads(response.get_data())
        assert 'token' in json
        assert json['user']['username'] == 'theboss'
        assert json['user']['email'] == 'email@gmail.com'
        assert response.status_code == 200

    def test_login_failure_password(self):
        """ User login with wrong password should return 401 """

        registration_data = {'email': 'email@gmail.com', 'username': 'theboss', 'password': '123'}
        self.mock_auth_server.register(registration_data)
        login_data = {'email': 'email@gmail.com', 'password': 'wrong'}
        response = self.mock_auth_server.login(login_data)
        assert b'Password incorrect' in response.get_data()
        assert response.status_code == 401

    def test_login_failure_inexistent(self):
        """ Login of unknown user should return 401 """

        login_data = {'email': 'email@gmail.com', 'password': 'wrong'}
        response = self.mock_auth_server.login(login_data)
        assert b'Could not find user' in response.get_data()
        assert response.status_code == 401

    def test_authorize_success(self):
        """ Authorize a user with valid token should return 200 """

        registration_data = {'email': 'email@gmail.com', 'username': 'theboss', 'password': '123'}
        self.mock_auth_server.register(registration_data)
        login_data = {'email': 'email@gmail.com', 'password': '123'}
        response = self.mock_auth_server.login(login_data)        
        json = loads(response.get_data())
        token = json['token']
        response = self.mock_auth_server.authorize_user(token)
        json = loads(response.get_data())
        assert json['user']['email'] == 'email@gmail.com'
        assert json['user']['username'] == 'theboss'
        assert response.status_code == 200

    def test_authorize_failure_invalid(self):
        """ Authorize a user with invalid token should return 401 """

        response = self.mock_auth_server.authorize_user('invalid_token')
        assert b'Invalid Token' in response.get_data()
        assert response.status_code == 401

    def test_get_users_success(self):
        """ Get users should return 200 with user data """

        response = self.mock_auth_server.get_users()
        json = loads(response.get_data())
        assert response.status_code == 200
        id = 1
        for user in json:
            assert user['id'] == str(id)
            assert user['email'] == 'email' + str(id)
            assert user['username'] == 'user' + str(id)
            id += 1

