import pytest
from mongoengine import connect, disconnect
from mongoengine.connection import _get_db
from tests.utils import add_user, get_users

class TestUser:
    def setup_method(self, method):
        """ setup any state tied to the execution of the given method in a
        class.  
            setup_method is invoked for every test method of a class.
        """
        connect('appserver-db-test', host='mongomock://localhost', alias='test')

    def teardown_method(self, method):
        """ teardown any state that was previously setup with a setup_method
        call.
        """
        db = _get_db()
        db.drop_collection('user')

    def test_add_user(self, client):
        """ POST /users
        Should: return 200 and the correct id in the body"""
        res = add_user(client, 'aUsername')
        assert res.status_code == 200

    def test_add_same_user_twice(self, client):
        """ POST /users
        Should: return 400 and correct message"""
        add_user(client, 'aUsername')
        res = add_user(client, 'aUsername')
        print(res.get_json())
        assert res.status_code == 400
        assert b'Invalid request' in res.data

    def test_add_invalid_user(self, client):
        """ POST /users
        Should: return 400 and correct message"""
        res = client.post('/users/', json={})
        assert res.status_code == 400
        assert b'Invalid request' in res.data

    def test_get_no_users(self, client):
        """ GET /users
        Should: return 200 and empty body"""
        res = get_users(client)
        user_info = res.get_json() 
        assert res.status_code == 200
        assert len(user_info) == 0
    
    def test_get_users(self, client):
        """ GET /users
        Should: return 200 and all users posted"""
        add_user(client, 'aUsername')
        add_user(client, 'anotherUserName')
        res = get_users(client)
        user_info = res.get_json() 
        assert res.status_code == 200
        assert len(user_info) == 2
    