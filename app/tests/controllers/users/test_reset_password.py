import pytest
from mongoengine import connect, disconnect
from mongoengine.connection import _get_db
from tests.utils import *
import json

USER_1 = 1
CODE = 1111

class TestResetPassword:
 
    def setup_method(self, method):
        """ setup any state tied to the execution of the given method in a
        class.  setup_method is invoked for every test method of a class.
        """
        connect('appserver-db-test', host='mongomock://localhost', alias='test')

    def teardown_method(self, method):
        """ teardown any state that was previously setup with a setup_method
        call.
        """
        db = _get_db()
        disconnect(alias='test')

    def test_reset_password_successfully(self, client):
        """ POST /users/reset_password
        Should: return 200"""

        res = reset_password(client, 'email1')
        assert res.status_code == 200

    def test_reset_password_wrong_mail_should_return_200(self, client):
        """ POST /users/reset_password
        Should: return 200"""

        res = reset_password(client, 'wrongEmail')
        assert res.status_code == 200

    def test_reset_password_should_return_400(self, client):
        """ POST /users/reset_password
        Should: return 400"""

        res = reset_password(client)
        assert res.status_code == 400

    def test_validate_code_success(self, client):
        """ GET /users/password
        Should: return 200"""

        email = "email1"
        res = reset_password(client, email)
        assert res.status_code == 200

        res = validate_code(client, CODE, email)
        assert res.status_code == 200

    def test_validate_code_wrong_email(self, client):
        """ GET /users/password
        Should: return 401"""

        res = validate_code(client, CODE, 'wrongEmail')
        assert res.status_code == 401

    def test_validate_code_wrong_code(self, client):
        """ GET /users/password
        Should: return 401"""

        email = "email1"
        res = reset_password(client, email)
        assert res.status_code == 200

        res = validate_code(client, 1234, email)
        assert res.status_code == 401

    def test_change_password_success(self, client):
        """ POST /users/password
        Should: return 204"""

        email = "email1"
        res = reset_password(client, email)
        assert res.status_code == 200

        res = change_password(client, CODE, email, 'aPassword')
        assert res.status_code == 204

    def test_change_password_missing_fields(self, client):
        """ POST /users/password
        Should: return 400"""

        email = "email1"
        res = reset_password(client, email)
        assert res.status_code == 200

        res = change_password(client, CODE, email)
        assert res.status_code == 400

    def test_change_password_wrong_email(self, client):
        """ POST /users/password
        Should: return 401"""

        email = "email1"
        res = reset_password(client, email)
        assert res.status_code == 200

        res = change_password(client, CODE, 'wrongEmail', 'aPassword')
        assert res.status_code == 401
   
    def test_change_password_wrong_code(self, client):
        """ POST /users/password
        Should: return 401"""

        email = "email1"
        res = reset_password(client, email)
        assert res.status_code == 200

        res = change_password(client, 1234, email, 'aPassword')
        assert res.status_code == 401
    