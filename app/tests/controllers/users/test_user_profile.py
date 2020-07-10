import pytest
from mongoengine import connect, disconnect
from mongoengine.connection import _get_db
from tests.utils import *
import json

USER_1 = 1
USER_2 = 2

class TestUsersProfile:
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
        db.drop_collection('friends')
        db.drop_collection('pending_request')
        disconnect(alias='test')


    # -- Users management

    def test_get_existent_user(self, client):
        """ GET /users/user_id
        Should: return 200"""

        token = login_and_token_user(client, USER_1)
        res = get_user_profile(client, token, USER_2)
        res_json = json.loads(res.get_data())
        assert res.status_code == 200
        assert res_json['id'] == '2'
        assert res_json['username'] == 'user2'
        assert res_json['email'] == 'email2'
        assert res_json['profile']['picture'] == 'picture2'
    
    def test_get_inexistent_user(self, client):
        """ GET /users/user_id
        Should: return 404"""

        token = login_and_token_user(client, USER_1)
        res = get_user_profile(client, token, 100)
        assert res.status_code == 404
    
    def test_check_no_friends(self, client):
        """ GET /users/<user_id_request>
        Should: return 200"""

        token = login_and_token_user(client)
        res = get_user_profile(client, token, USER_2)

        assert res.status_code == 200
        res_json = json.loads(res.get_data())
        assert res_json["friendship_status"] == "no-friends"

    def test_check_same_user_d(self, client):
        """ GET /users/<user_id_request>
        Should: return 200"""

        token = login_and_token_user(client)
        res = get_user_profile(client, token, USER_1)

        assert res.status_code == 200
        res_json = json.loads(res.get_data())
        assert "friendship_status" not in res_json

    def test_edit_user_profile_successully(self, client):
        """ PUT /users/user_id
        Should: return 200 """

        new_profile_pic = 'myNewProfilePic'
        token = login_and_token_user(client, USER_1)

        res = edit_user_profile(client, token, USER_1, new_profile_pic)
        res_json = json.loads(res.get_data())
        assert res.status_code == 200
        assert res_json['profile']['picture'] == new_profile_pic
    
    def test_edit_forbidden_user_profile(self, client):
        """ PUT /users/user_id
        Should: return 403 """

        new_profile_pic = 'myNewProfilePic'
        token = login_and_token_user(client, USER_1)

        res = edit_user_profile(client, token, USER_2, new_profile_pic)
        assert res.status_code == 403

    def test_edit_bad_credentials_user_profile(self, client):
        """ PUT /users/user_id
        Should: return 401 """

        new_profile_pic = 'myNewProfilePic'
        res = edit_user_profile(client, 'invalid', USER_1, new_profile_pic)
        assert res.status_code == 401

    def test_delete_user_profile_successfully(self, client):
        """ DELETE /users/user_id
        Should: return 204 """

        token = login_and_token_user(client, USER_1)
        res = delete_user_profile(client, token, USER_1)
        assert res.status_code == 204

        other_token = login_and_token_user(client, USER_2)
        res = get_user_profile(client, other_token, USER_1)
        assert res.status_code == 404

    def test_delete_unauthorized_user_profile(self, client):
        """ DELETE /users/user_id
        Should: return 401 """

        res = delete_user_profile(client, 'invalidToken', USER_1)
        assert res.status_code == 401

    def test_delete_forbidden_user_profile(self, client):
        """ DELETE /users/user_id
        Should: return 403 """

        token = login_and_token_user(client, USER_1)
        res = delete_user_profile(client, token, USER_2)
        assert res.status_code == 403


