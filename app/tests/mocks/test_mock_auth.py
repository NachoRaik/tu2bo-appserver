import pytest
from json import loads
from shared_servers.AuthServer import MockAuthServer

CODE = 1111

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
        assert b'Wrong credentials' in response.get_data()
        assert response.status_code == 401

    def test_login_failure_inexistent(self):
        """ Login of unknown user should return 401 """

        login_data = {'email': 'email@gmail.com', 'password': 'wrong'}
        response = self.mock_auth_server.login(login_data)
        assert b'Wrong credentials' in response.get_data()
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

    def test_edit_user_success(self):
        """ Edit user should return 200 with user data """

        profile_data = {'picture': 'somePicture'}
        response = self.mock_auth_server.edit_user_profile(1, profile_data)
        json = loads(response.get_data())
        assert response.status_code == 200
        assert json['profile'] == profile_data

    def test_edit_user_inexistent(self):
        """ Edit inexistent user should return 404 """

        profile_data = {'picture': 'somePicture'}
        response = self.mock_auth_server.edit_user_profile(100, profile_data)
        json = loads(response.get_data())
        assert response.status_code == 404

    def test_delete_user_success(self):
        """ Delete user should return 200 with user data """

        response = self.mock_auth_server.delete_user_profile(1)
        assert response.status_code == 204

    def test_delete_user_inexistent(self):
        """ Delete user should return 404 with user data """

        response = self.mock_auth_server.delete_user_profile(100)
        assert response.status_code == 404

    def test_send_mail_success(self):
        """ Send mail should return 200 """

        request = {"email": "email1"}
        response = self.mock_auth_server.send_mail(request)
        assert response.status_code == 200

    def test_send_wrong_mail_should_return_200(self):
        """ Send wrong mail should return 200 """

        request = {"email": "wrongemail"}
        response = self.mock_auth_server.send_mail(request)
        assert response.status_code == 200

    def test_send_mail_should_return_400(self):
        """ Send mail should return 400 """

        response = self.mock_auth_server.send_mail({})
        assert response.status_code == 400

    def test_validate_code_success(self):
        """ Validate code should return 200 """

        email = "email1"
        request = {"email": email}
        response = self.mock_auth_server.send_mail(request)
        assert response.status_code == 200

        response = self.mock_auth_server.validate_code(CODE, email)
        assert response.status_code == 200

    def test_validate_code_wrong_email(self):
        """ Validate code should return 401 """

        response = self.mock_auth_server.validate_code(CODE, 'wrongEmail')
        assert response.status_code == 401

    def test_validate_code_wrong_code(self):
        """ Validate code should return 401 """

        email = "email1"
        request = {"email": email}
        response = self.mock_auth_server.send_mail(request)
        assert response.status_code == 200

        response = self.mock_auth_server.validate_code(1234, email)
        assert response.status_code == 401
        